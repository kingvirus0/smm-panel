import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from app.tasks.celery_app import celery_app
from app.database import async_session
from app.models.order import Order
from app.models.provider import ProviderAccount
from app.services.provider_service import place_order_on_provider, check_order_status_on_provider
from app.services.referral_service import process_referral_commission
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_order(self, order_id: str):
    asyncio.get_event_loop().run_until_complete(_process_order(self, order_id))


async def _process_order(task, order_id: str):
    async with async_session() as db:
        try:
            result = await db.execute(
                select(Order).where(Order.id == order_id).with_for_update()
            )
            order = result.scalar_one_or_none()
            if not order or order.status != "pending":
                return

            order.status = "processing"
            await db.commit()

            provider_result = await db.execute(
                select(ProviderAccount).where(ProviderAccount.id == order.provider_account_id)
            )
            provider = provider_result.scalar_one()

            service_result = await db.execute(
                select(__import__('app.models.service', fromlist=['Service']).Service).where(
                    __import__('app.models.service', fromlist=['Service']).Service.id == order.service_id
                )
            )
            service = service_result.scalar_one()

            try:
                response = await place_order_on_provider(
                    provider, service.provider_service_id, order.target_url, order.quantity
                )

                if "order" in response:
                    order.provider_order_id = response["order"]
                    order.status = "in_progress"
                elif "error" in response:
                    order.status = "error"
                    order.error_message = response["error"]
                    from app.services.user_service import credit_balance
                    await credit_balance(db, order.user_id, order.charge, "refund", order.id, f"Refund: {response['error']}")

                await db.commit()
            except Exception as e:
                order.retry_count += 1
                if order.retry_count >= 3:
                    order.status = "error"
                    order.error_message = str(e)
                    from app.services.user_service import credit_balance
                    await credit_balance(db, order.user_id, order.charge, "refund", order.id, f"Refund: {str(e)}")
                await db.commit()
                raise task.retry(exc=e)

        except Exception as e:
            logger.error(f"Error processing order {order_id}: {e}")
            raise


@celery_app.task
def sync_order_status():
    asyncio.get_event_loop().run_until_complete(_sync_order_status())


async def _sync_order_status():
    async with async_session() as db:
        try:
            result = await db.execute(
                select(Order).where(
                    Order.status.in_(["processing", "in_progress"])
                ).limit(50)
            )
            orders = result.scalars().all()

            for order in orders:
                try:
                    provider_result = await db.execute(
                        select(ProviderAccount).where(ProviderAccount.id == order.provider_account_id)
                    )
                    provider = provider_result.scalar_one()

                    if not order.provider_order_id:
                        continue

                    status_data = await check_order_status_on_provider(provider, order.provider_order_id)

                    if "status" in status_data:
                        provider_status = status_data["status"].lower()
                        if "charge" in status_data:
                            order.charge = status_data["charge"]

                        if provider_status == "completed":
                            order.status = "completed"
                            order.completed_at = datetime.utcnow()
                            order.remains = 0

                            if order.user_id:
                                from app.models.user import User
                                user_result = await db.execute(
                                    select(User).where(User.id == order.user_id)
                                )
                                user = user_result.scalar_one_or_none()
                                if user and user.referred_by:
                                    await process_referral_commission(db, user.referred_by, order.charge)

                        elif provider_status == "partial":
                            order.status = "partial"
                            if "start_count" in status_data:
                                order.start_count = status_data["start_count"]
                            if "current_count" in status_data:
                                order.current_count = status_data["current_count"]
                            if "remains" in status_data:
                                order.remains = status_data["remains"]

                        elif provider_status in ("in progress", "processing"):
                            order.status = "in_progress"
                            if "current_count" in status_data:
                                order.current_count = status_data["current_count"]
                            if "remains" in status_data:
                                order.remains = status_data["remains"]

                        elif provider_status == "refunded":
                            order.status = "refunded"
                            from app.services.user_service import credit_balance
                            await credit_balance(db, order.user_id, order.charge, "refund", order.id, "Provider refund")

                    await db.commit()
                except Exception as e:
                    logger.error(f"Error syncing order {order.id}: {e}")
                    continue

            stale_cutoff = datetime.utcnow() - timedelta(hours=48)
            stale_result = await db.execute(
                select(Order).where(
                    and_(Order.status == "in_progress", Order.created_at < stale_cutoff)
                )
            )
            for stale_order in stale_result.scalars().all():
                stale_order.status = "error"
                stale_order.error_message = "Order stuck for over 48 hours"
                from app.services.user_service import credit_balance
                await credit_balance(db, stale_order.user_id, stale_order.charge, "refund", stale_order.id, "Refund: stuck order")
                await db.commit()

        except Exception as e:
            logger.error(f"Error in sync_order_status: {e}")
