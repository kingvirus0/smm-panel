from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class DashboardStats(BaseModel):
    total_users: int
    new_users_today: int
    total_orders: int
    orders_today: int
    revenue_today: Decimal
    revenue_this_week: Decimal
    revenue_this_month: Decimal
    pending_payments: int
    active_orders: int


class SettingsUpdate(BaseModel):
    auto_process_orders: bool | None = None
    order_poll_interval: int | None = None
    min_topup_amount: Decimal | None = None
    registration_open: bool | None = None
    maintenance_mode: bool | None = None
    telegram_notifications: bool | None = None


class ProviderAccountCreate(BaseModel):
    name: str
    api_url: str
    api_key: str


class ProviderAccountRead(BaseModel):
    id: str
    name: str
    api_url: str
    balance: Decimal
    is_active: bool
    last_synced_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
