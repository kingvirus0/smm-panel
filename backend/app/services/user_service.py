from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User
from app.models.payment import BalanceLog
from app.core.exceptions import SMMPanelException


async def get_user_balance(db: AsyncSession, user_id: str) -> Decimal:
    result = await db.execute(select(User.balance).where(User.id == user_id))
    return result.scalar_one()


async def deduct_balance(db: AsyncSession, user_id: str, amount: Decimal, reference_type: str, reference_id: str, note: str = "") -> None:
    result = await db.execute(select(User).where(User.id == user_id).with_for_update())
    user = result.scalar_one()
    
    if user.balance < amount:
        raise SMMPanelException("Insufficient balance", 402)
    
    user.balance -= amount
    log = BalanceLog(
        user_id=user_id,
        amount=-amount,
        balance_after=user.balance,
        log_type="order_charge",
        reference_type=reference_type,
        reference_id=reference_id,
        note=note,
    )
    db.add(log)
    await db.commit()


async def credit_balance(db: AsyncSession, user_id: str, amount: Decimal, reference_type: str, reference_id: str, note: str = "") -> None:
    result = await db.execute(select(User).where(User.id == user_id).with_for_update())
    user = result.scalar_one()
    
    user.balance += amount
    log = BalanceLog(
        user_id=user_id,
        amount=amount,
        balance_after=user.balance,
        log_type="refund",
        reference_type=reference_type,
        reference_id=reference_id,
        note=note,
    )
    db.add(log)
    await db.commit()
