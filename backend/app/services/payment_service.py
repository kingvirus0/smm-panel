from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.payment import Payment, BalanceLog
from app.models.user import User
from app.core.exceptions import SMMPanelException, SMMPanelException


async def create_topup_request(db: AsyncSession, user_id: str, amount: Decimal, method: str, tx_reference: str | None = None, proof_file_url: str | None = None) -> Payment:
    if amount < Decimal("1.00"):
        raise SMMPanelException("Minimum top-up is $1.00")
    
    payment = Payment(
        user_id=user_id,
        amount=amount,
        method=method,
        tx_reference=tx_reference,
        proof_file_url=proof_file_url,
        status="pending",
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def approve_payment(db: AsyncSession, payment_id: str, admin_id: str, admin_note: str | None = None) -> Payment:
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise SMMPanelException("Payment not found", 404)
    if payment.status != "pending":
        raise SMMPanelException("Payment already processed")
    
    payment.status = "approved"
    payment.processed_at = datetime.utcnow()
    payment.processed_by = admin_id
    payment.admin_note = admin_note
    
    user_result = await db.execute(select(User).where(User.id == payment.user_id).with_for_update())
    user = user_result.scalar_one()
    user.balance += payment.amount
    
    log = BalanceLog(
        user_id=payment.user_id,
        amount=payment.amount,
        balance_after=user.balance,
        log_type="topup",
        reference_type="payment",
        reference_id=payment.id,
        note=f"Top-up via {payment.method}",
    )
    db.add(log)
    await db.commit()
    await db.refresh(payment)
    return payment


async def reject_payment(db: AsyncSession, payment_id: str, admin_id: str, admin_note: str | None = None) -> Payment:
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise SMMPanelException("Payment not found", 404)
    
    payment.status = "rejected"
    payment.processed_at = datetime.utcnow()
    payment.processed_by = admin_id
    payment.admin_note = admin_note
    await db.commit()
    await db.refresh(payment)
    return payment


async def get_user_payments(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 50) -> list[Payment]:
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_pending_payments(db: AsyncSession) -> list[Payment]:
    result = await db.execute(
        select(Payment)
        .where(Payment.status == "pending")
        .order_by(Payment.created_at.desc())
    )
    return list(result.scalars().all())
