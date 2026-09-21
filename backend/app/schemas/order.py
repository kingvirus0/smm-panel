from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class OrderCreate(BaseModel):
    service_id: str
    target_url: str
    quantity: int


class BulkOrderItem(BaseModel):
    service_id: str
    target_url: str
    quantity: int


class BulkOrderRequest(BaseModel):
    orders: list[BulkOrderItem]


class OrderRead(BaseModel):
    id: str
    service_id: str
    provider_order_id: int | None
    status: str
    target_url: str
    quantity: int
    start_count: int
    current_count: int
    remains: int
    charge: Decimal
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class OrderCreateResponse(BaseModel):
    id: str
    status: str
    charge: Decimal
    message: str = "Order placed successfully"
