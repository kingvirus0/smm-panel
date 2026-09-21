import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User
from app.models.referral import Referral, AffiliateLink, MicroTask, ResellerProduct
from app.config import get_settings

settings = get_settings()


async def process_referral_commission(db: AsyncSession, referrer_id: str, order_amount: Decimal):
    commission = order_amount * Decimal(str(settings.REFERRAL_COMMISSION_RATE))
    if commission <= 0:
        return
    
    result = await db.execute(select(User).where(User.id == referrer_id).with_for_update())
    referrer = result.scalar_one()
    referrer.balance += commission
    referrer.affiliate_earnings += commission
    
    referral = Referral(
        referrer_id=referrer_id,
        referred_id=referrer_id,
        commission_earned=commission,
    )
    db.add(referral)
    await db.commit()


async def create_affiliate_link(db: AsyncSession, user_id: str) -> AffiliateLink:
    code = uuid.uuid4().hex[:8].upper()
    link = AffiliateLink(user_id=user_id, code=code)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def get_affiliate_links(db: AsyncSession, user_id: str) -> list[AffiliateLink]:
    result = await db.execute(
        select(AffiliateLink).where(AffiliateLink.user_id == user_id)
    )
    return list(result.scalars().all())


async def create_micro_task(db: AsyncSession, creator_id: str, title: str, description: str, task_type: str, reward: Decimal, target_url: str | None = None, platform: str | None = None, max_completions: int = 1) -> MicroTask:
    task = MicroTask(
        title=title,
        description=description,
        task_type=task_type,
        reward=reward,
        target_url=target_url,
        platform=platform,
        max_completions=max_completions,
        created_by=creator_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_available_micro_tasks(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[MicroTask]:
    result = await db.execute(
        select(MicroTask)
        .where(MicroTask.is_active == True, MicroTask.current_completions < MicroTask.max_completions)
        .order_by(MicroTask.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_reseller_product(db: AsyncSession, user_id: str, service_id: str, custom_price_per_1000: Decimal) -> ResellerProduct:
    product = ResellerProduct(
        user_id=user_id,
        service_id=service_id,
        custom_price_per_1000=custom_price_per_1000,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product
