from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class ServiceCategoryRead(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    icon_url: str | None
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


class ServiceRead(BaseModel):
    id: str
    category_id: str
    provider_service_id: int
    name: str
    description: str | None
    price_per_1000: Decimal
    min_quantity: int
    max_quantity: int
    avg_time_seconds: int
    drip_feed_support: bool
    refill_support: bool
    cancel_support: bool
    is_active: bool

    class Config:
        from_attributes = True


class ServiceCreate(BaseModel):
    category_id: str
    provider_account_id: str
    provider_service_id: int
    name: str
    description: str | None = None
    price_per_1000: Decimal
    min_quantity: int
    max_quantity: int
    avg_time_seconds: int = 0
    drip_feed_support: bool = False
    refill_support: bool = False
    cancel_support: bool = False


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price_per_1000: Decimal | None = None
    min_quantity: int | None = None
    max_quantity: int | None = None
    is_active: bool | None = None
