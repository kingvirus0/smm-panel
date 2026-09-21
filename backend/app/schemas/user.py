from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class UserRead(BaseModel):
    id: str
    email: str
    username: str
    role: str
    balance: Decimal
    is_active: bool
    telegram_linked: bool
    referral_code: str
    affiliate_earnings: Decimal
    reseller_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: str | None = None
    username: str | None = None


class AdminUserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    is_banned: bool | None = None
    balance_adjustment: Decimal | None = None
    balance_note: str | None = None
