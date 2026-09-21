from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.schemas.user import UserRead, UserUpdate, AdminUserUpdate
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.payment import BalanceLog
from app.core.security import get_password_hash
from app.core.exceptions import SMMPanelException

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserRead)
async def update_me(req: UserUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if req.email:
        user.email = req.email
    if req.username:
        user.username = req.username
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/", response_model=list[UserRead])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(User)
    if search:
        query = query.where((User.email.contains(search)) | (User.username.contains(search)))
    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise SMMPanelException("User not found", 404)
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: str, req: AdminUserUpdate, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise SMMPanelException("User not found", 404)

    if req.role is not None:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active
    if req.is_banned is not None:
        user.is_banned = req.is_banned
    if req.balance_adjustment is not None:
        user.balance += req.balance_adjustment
        log = BalanceLog(
            user_id=user_id,
            amount=req.balance_adjustment,
            balance_after=user.balance,
            log_type="admin_adjustment",
            note=req.balance_note or "Admin balance adjustment",
        )
        db.add(log)

    await db.commit()
    await db.refresh(user)
    return user
