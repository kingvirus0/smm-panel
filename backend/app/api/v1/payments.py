from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.payment import TopUpRequest, PaymentRead
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.services import payment_service
from app.core.exceptions import SMMPanelException

router = APIRouter()


@router.post("/topup", response_model=PaymentRead)
async def topup(req: TopUpRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await payment_service.create_topup_request(db, user.id, req.amount, req.method, req.tx_reference, req.proof_file_url)


@router.get("/my", response_model=list[PaymentRead])
async def my_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await payment_service.get_user_payments(db, user.id, skip, limit)


@router.get("/pending", response_model=list[PaymentRead])
async def pending_payments(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await payment_service.get_pending_payments(db)


@router.put("/{payment_id}/approve", response_model=PaymentRead)
async def approve(payment_id: str, admin_note: str = None, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await payment_service.approve_payment(db, payment_id, admin.id, admin_note)


@router.put("/{payment_id}/reject", response_model=PaymentRead)
async def reject(payment_id: str, admin_note: str = None, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await payment_service.reject_payment(db, payment_id, admin.id, admin_note)
