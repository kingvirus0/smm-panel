import httpx
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.provider import ProviderAccount
from app.core.exceptions import ProviderAPIError


async def call_provider_api(provider: ProviderAccount, action: str, **kwargs) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        data = {"key": provider.api_key, "action": action, **kwargs}
        try:
            response = await client.post(provider.api_url, data=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ProviderAPIError(f"Provider API error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ProviderAPIError(f"Provider connection error: {str(e)}")


async def get_provider_balance(db: AsyncSession, provider_id: str) -> Decimal:
    result = await db.execute(select(ProviderAccount).where(ProviderAccount.id == provider_id))
    provider = result.scalar_one()
    
    data = await call_provider_api(provider, "balance")
    if "balance" in data:
        provider.balance = Decimal(str(data["balance"]))
        await db.commit()
        return provider.balance
    return provider.balance


async def sync_provider_services(db: AsyncSession, provider_id: str) -> list[dict]:
    result = await db.execute(select(ProviderAccount).where(ProviderAccount.id == provider_id))
    provider = result.scalar_one()
    
    data = await call_provider_api(provider, "services")
    if isinstance(data, list):
        return data
    return []


async def place_order_on_provider(provider: ProviderAccount, service_id: int, link: str, quantity: int) -> dict:
    data = await call_provider_api(provider, "add", service=service_id, link=link, quantity=quantity)
    return data


async def check_order_status_on_provider(provider: ProviderAccount, order_id: int) -> dict:
    data = await call_provider_api(provider, "status", order=order_id)
    return data
