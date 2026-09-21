import hmac
import hashlib
import json
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select
import httpx

from app.database import async_session
from app.models.payment import Payment, BalanceLog
from app.models.user import User
from app.config import get_settings

router = APIRouter()
settings = get_settings()


async def notify_telegram(telegram_user_id: str, amount: Decimal, new_balance: Decimal):
    """Send Telegram notification after successful payment."""
    if not telegram_user_id:
        return
    try:
        from bot.bot_instance import bot
        await bot.send_message(
            chat_id=int(telegram_user_id),
            text=(
                f"*Payment Successful!*\n\n"
                f"Amount added: *₦{amount:,.0f}*\n"
                f"New wallet balance: *₦{new_balance:,.0f}*\n\n"
                f"You can now place orders. Use /services to browse."
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass


async def credit_wallet(payment: Payment):
    """Atomically credit user wallet and mark payment as success."""
    async with async_session() as db:
        async with db.begin():
            result = await db.execute(
                select(User).where(User.id == payment.user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if not user:
                return

            user.balance += payment.amount

            log = BalanceLog(
                user_id=user.id,
                amount=payment.amount,
                balance_after=user.balance,
                log_type="topup",
                reference_type="payment",
                reference_id=payment.id,
                note=f"Top-up via {payment.provider}",
            )
            db.add(log)

            pay_result = await db.execute(
                select(Payment).where(Payment.id == payment.id).with_for_update()
            )
            pay = pay_result.scalar_one()
            pay.status = "success"
            pay.verified_at = datetime.utcnow()

        await db.refresh(user)
        await notify_telegram(payment.telegram_user_id, payment.amount, user.balance)


@router.post("/paystack")
async def paystack_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Paystack-Signature", "")

    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        raw_body,
        hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(400, "Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON")

    event = payload.get("event")
    if event != "charge.success":
        return {"status": "ignored"}

    data = payload.get("data", {})
    reference = data.get("reference")

    if not reference:
        return {"status": "no reference"}

    async with async_session() as db:
        result = await db.execute(
            select(Payment).where(
                Payment.reference == reference,
                Payment.provider == "paystack",
            )
        )
        payment = result.scalar_one_or_none()

        if not payment or payment.status == "success":
            return {"status": "already processed"}

        paid_amount = Decimal(str(data.get("amount", 0))) / Decimal("100")
        if paid_amount != payment.amount:
            return {"status": "amount mismatch"}

    await credit_wallet(payment)
    return {"status": "success"}


@router.post("/flutterwave")
async def flutterwave_webhook(request: Request):
    raw_body = await request.body()
    verif_hash = request.headers.get("verif-hash", "")

    if not hmac.compare_digest(verif_hash, settings.FLUTTERWAVE_WEBHOOK_SECRET):
        raise HTTPException(401, "Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON")

    event = payload.get("event")
    data = payload.get("data", {})

    if event != "charge.completed" or data.get("status") != "successful":
        return {"status": "ignored"}

    tx_ref = data.get("tx_ref")
    if not tx_ref:
        return {"status": "no tx_ref"}

    async with async_session() as db:
        result = await db.execute(
            select(Payment).where(
                Payment.reference == tx_ref,
                Payment.provider == "flutterwave",
            )
        )
        payment = result.scalar_one_or_none()

        if not payment or payment.status == "success":
            return {"status": "already processed"}

        fw_tx_id = data.get("id")

        async with httpx.AsyncClient(timeout=30) as client:
            verify_response = await client.get(
                f"https://api.flutterwave.com/v3/transactions/{fw_tx_id}/verify",
                headers={"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"},
            )
            verify_data = verify_response.json()

        if verify_data.get("status") != "success":
            return {"status": "verification failed"}

        verified_amount = Decimal(str(verify_data["data"]["amount"]))
        if verified_amount != payment.amount:
            return {"status": "amount mismatch"}

    await credit_wallet(payment)
    return {"status": "success"}
