import asyncio
from datetime import datetime
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.database import async_session
from app.models.provider import ProviderAccount
from app.services.provider_service import get_provider_balance
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def sync_provider_balances():
    asyncio.get_event_loop().run_until_complete(_sync_provider_balances())


async def _sync_provider_balances():
    async with async_session() as db:
        try:
            result = await db.execute(
                select(ProviderAccount).where(ProviderAccount.is_active == True)
            )
            providers = result.scalars().all()

            for provider in providers:
                try:
                    balance = await get_provider_balance(db, provider.id)
                    provider.last_synced_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"Provider {provider.name} balance: {balance}")
                except Exception as e:
                    logger.error(f"Error syncing provider {provider.name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in sync_provider_balances: {e}")
