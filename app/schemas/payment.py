
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    status: str
    transaction_ref: str | None
    created_at: datetime
    paid_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
