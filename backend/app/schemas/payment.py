from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class TopUpRequest(BaseModel):
    amount: Decimal
    method: str
    tx_reference: str | None = None
    proof_file_url: str | None = None


class PaymentRead(BaseModel):
    id: str
    amount: Decimal
    method: str
    status: str
    tx_reference: str | None
    admin_note: str | None
    created_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True


class BalanceLogRead(BaseModel):
    id: str
    amount: Decimal
    balance_after: Decimal
    log_type: str
    reference_type: str | None
    note: str | None
    created_at: datetime

    class Config:
        from_attributes = True
