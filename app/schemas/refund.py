
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    amount: Decimal
    status: str
    reason: str | None
    created_at: datetime
    processed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
