from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.order import OrderCreate, OrderRead, OrderCreateResponse, BulkOrderRequest
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.services import order_service
from app.tasks.order_tasks import process_order
from app.core.exceptions import SMMPanelException

router = APIRouter()


@router.post("/", response_model=OrderCreateResponse)
async def create_order(req: OrderCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = await order_service.create_order(db, user.id, req.service_id, req.target_url, req.quantity)
    process_order.delay(order.id)
    return OrderCreateResponse(id=order.id, status=order.status, charge=order.charge)


@router.post("/bulk", response_model=list[OrderCreateResponse])
async def create_bulk_orders(req: BulkOrderRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    responses = []
    for item in req.orders:
        order = await order_service.create_order(db, user.id, item.service_id, item.target_url, item.quantity)
        process_order.delay(order.id)
        responses.append(OrderCreateResponse(id=order.id, status=order.status, charge=order.charge))
    return responses


@router.get("/", response_model=list[OrderRead])
async def list_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await order_service.get_user_orders(db, user.id, skip, limit)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = await order_service.get_order_by_id(db, order_id)
    if order.user_id != user.id:
        raise SMMPanelException("Forbidden", 403)
    return order


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(order_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = await order_service.cancel_order(db, order_id, user.id)
    return order


@router.get("/all", response_model=list[OrderRead])
async def list_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.order import Order
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())
