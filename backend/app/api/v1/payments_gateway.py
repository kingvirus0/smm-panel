import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.payment import Payment
from app.config import get_settings

router = APIRouter()
settings = get_settings()


def generate_reference(prefix: str, user_id: str) -> str:
    return f"SMM-{prefix}-{user_id[:8]}-{uuid.uuid4().hex[:8]}"


@router.post("/paystack/initialize")
async def initialize_paystack(
    amount_naira: float,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if amount_naira < 100:
        raise HTTPException(400, "Minimum amount is ₦100")

    reference = generate_reference("PS", user.id)

    payment = Payment(
        user_id=user.id,
        telegram_user_id=user.telegram_id,
        amount=Decimal(str(amount_naira)),
        method="paystack",
        provider="paystack",
        reference=reference,
        status="pending",
    )
    db.add(payment)
    await db.commit()

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                "https://api.paystack.co/transaction/initialize",
                headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
                json={
                    "email": user.email,
                    "amount": int(amount_naira * 100),
                    "reference": reference,
                    "callback_url": f"{settings.FRONTEND_URL}/payment/verify",
                    "metadata": {"user_id": user.id, "payment_id": payment.id},
                },
            )
            data = response.json()
            if not data.get("status"):
                raise HTTPException(400, data.get("message", "Payment initialization failed"))
            return {
                "authorization_url": data["data"]["authorization_url"],
                "reference": reference,
            }
        except httpx.RequestError as e:
            raise HTTPException(502, f"Payment gateway error: {str(e)}")


@router.post("/flutterwave/initialize")
async def initialize_flutterwave(
    amount_naira: float,
    email: str,
    name: str = "",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if amount_naira < 100:
        raise HTTPException(400, "Minimum amount is ₦100")

    tx_ref = generate_reference("FW", user.id)

    payment = Payment(
        user_id=user.id,
        telegram_user_id=user.telegram_id,
        amount=Decimal(str(amount_naira)),
        method="flutterwave",
        provider="flutterwave",
        reference=tx_ref,
        status="pending",
    )
    db.add(payment)
    await db.commit()

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                "https://api.flutterwave.com/v3/payments",
                headers={"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"},
                json={
                    "tx_ref": tx_ref,
                    "amount": amount_naira,
                    "currency": "NGN",
                    "redirect_url": f"{settings.FRONTEND_URL}/payment/verify",
                    "customer": {"email": email, "name": name},
                    "customizations": {"title": "Fund Wallet", "logo": ""},
                },
            )
            data = response.json()
            if data.get("status") != "success":
                raise HTTPException(400, data.get("message", "Payment initialization failed"))
            return {
                "payment_link": data["data"]["link"],
                "tx_ref": tx_ref,
            }
        except httpx.RequestError as e:
            raise HTTPException(502, f"Payment gateway error: {str(e)}")


@router.get("/verify")
async def verify_payment(
    ref: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Payment).where(Payment.reference == ref, Payment.user_id == user.id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(404, "Payment not found")
    return {
        "status": payment.status,
        "amount": payment.amount,
        "reference": payment.reference,
        "provider": payment.provider,
        "verified_at": payment.verified_at,
    }


@router.get("/status")
async def check_payment_status(
    ref: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Payment).where(Payment.reference == ref))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(404, "Payment not found")
    return {
        "status": payment.status,
        "amount": payment.amount,
        "reference": payment.reference,
    }
