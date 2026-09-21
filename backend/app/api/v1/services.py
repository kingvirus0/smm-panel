from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.service import ServiceRead, ServiceCategoryRead, ServiceCreate, ServiceUpdate
from app.dependencies import get_current_user, require_admin
from app.models.service import Service, ServiceCategory
from app.models.user import User
from app.core.exceptions import SMMPanelException

router = APIRouter()


@router.get("/", response_model=list[ServiceRead])
async def list_services(
    category_id: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Service).where(Service.is_active == True)
    if category_id:
        query = query.where(Service.category_id == category_id)
    query = query.order_by(Service.name).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/categories", response_model=list[ServiceCategoryRead])
async def list_categories(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ServiceCategory).where(ServiceCategory.is_active == True).order_by(ServiceCategory.sort_order)
    )
    return list(result.scalars().all())


@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(service_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise SMMPanelException("Service not found", 404)
    return service


@router.post("/", response_model=ServiceRead)
async def create_service(req: ServiceCreate, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    service = Service(**req.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceRead)
async def update_service(service_id: str, req: ServiceUpdate, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise SMMPanelException("Service not found", 404)

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(service, key, value)

    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/{service_id}")
async def delete_service(service_id: str, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise SMMPanelException("Service not found", 404)
    service.is_active = False
    await db.commit()
    return {"message": "Service deactivated"}
