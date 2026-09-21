from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment


async def get_dashboard_stats(db: AsyncSession) -> dict:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)

    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    new_users_today = (await db.execute(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )).scalar()
    total_orders = (await db.execute(select(func.count(Order.id)))).scalar()
    orders_today = (await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= today_start)
    )).scalar()
    
    revenue_today_result = (await db.execute(
        select(func.coalesce(func.sum(Order.charge), 0)).where(
            and_(Order.created_at >= today_start, Order.status.in_(["completed", "in_progress"]))
        )
    )).scalar()
    
    revenue_week_result = (await db.execute(
        select(func.coalesce(func.sum(Order.charge), 0)).where(
            and_(Order.created_at >= week_start, Order.status.in_(["completed", "in_progress"]))
        )
    )).scalar()
    
    revenue_month_result = (await db.execute(
        select(func.coalesce(func.sum(Order.charge), 0)).where(
            and_(Order.created_at >= month_start, Order.status.in_(["completed", "in_progress"]))
        )
    )).scalar()
    
    pending_payments = (await db.execute(
        select(func.count(Payment.id)).where(Payment.status == "pending")
    )).scalar()
    
    active_orders = (await db.execute(
        select(func.count(Order.id)).where(Order.status.in_(["pending", "processing", "in_progress"]))
    )).scalar()

    return {
        "total_users": total_users,
        "new_users_today": new_users_today,
        "total_orders": total_orders,
        "orders_today": orders_today,
        "revenue_today": Decimal(str(revenue_today_result)),
        "revenue_this_week": Decimal(str(revenue_week_result)),
        "revenue_this_month": Decimal(str(revenue_month_result)),
        "pending_payments": pending_payments,
        "active_orders": active_orders,
    }
