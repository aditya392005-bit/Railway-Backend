
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CoachFareCreate(BaseModel):
    train_id: int = Field(gt=0)
    coach_type: str = Field(min_length=1, max_length=30)
    fare_per_seat: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class CoachFareResponse(CoachFareCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
