from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order
from app.models.service import Service
from app.core.exceptions import SMMPanelException, OrderNotFoundError
from app.services.user_service import deduct_balance, credit_balance


async def create_order(db: AsyncSession, user_id: str, service_id: str, target_url: str, quantity: int) -> Order:
    result = await db.execute(select(Service).where(Service.id == service_id, Service.is_active == True))
    service = result.scalar_one_or_none()
    if not service:
        raise SMMPanelException("Service not found or inactive", 404)
    
    if quantity < service.min_quantity or quantity > service.max_quantity:
        raise SMMPanelException(f"Quantity must be between {service.min_quantity} and {service.max_quantity}")
    
    charge = Decimal(str(quantity)) / Decimal("1000") * service.price_per_1000
    
    order = Order(
        user_id=user_id,
        service_id=service_id,
        provider_account_id=service.provider_account_id,
        status="pending",
        target_url=target_url,
        quantity=quantity,
        charge=charge,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    await deduct_balance(db, user_id, charge, "order", order.id, f"Order #{order.id[:8]}")
    
    return order


async def cancel_order(db: AsyncSession, order_id: str, user_id: str) -> Order:
    result = await db.execute(select(Order).where(Order.id == order_id, Order.user_id == user_id))
    order = result.scalar_one_or_none()
    if not order:
        raise OrderNotFoundError()
    
    if order.status not in ("pending", "processing"):
        raise SMMPanelException("Cannot cancel order in current status")
    
    order.status = "cancelled"
    await credit_balance(db, user_id, order.charge, "refund", order.id, f"Refund for cancelled order #{order.id[:8]}")
    await db.commit()
    await db.refresh(order)
    return order


async def get_user_orders(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 50) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_order_by_id(db: AsyncSession, order_id: str) -> Order:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise OrderNotFoundError()
    return order
