from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.admin import DashboardStats, SettingsUpdate, ProviderAccountCreate, ProviderAccountRead
from app.dependencies import require_admin
from app.models.user import User
from app.models.provider import ProviderAccount
from app.services import admin_service, provider_service
from app.core.exceptions import SMMPanelException

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await admin_service.get_dashboard_stats(db)


@router.post("/providers", response_model=ProviderAccountRead)
async def create_provider(req: ProviderAccountCreate, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    provider = ProviderAccount(**req.model_dump())
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return provider


@router.get("/providers", response_model=list[ProviderAccountRead])
async def list_providers(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(ProviderAccount).order_by(ProviderAccount.created_at.desc()))
    return list(result.scalars().all())


@router.get("/providers/{provider_id}/balance")
async def get_provider_balance(provider_id: str, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    balance = await provider_service.get_provider_balance(db, provider_id)
    return {"balance": balance}
