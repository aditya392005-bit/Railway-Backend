
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

"""
class BookingCreate(BaseModel):
    train_id: int = Field(gt=0)
    journey_date: date
    seat_ids: list[int] = Field(min_length=1, max_length=6)
"""

class BookingSeatResponse(BaseModel):
    seat_inventory_id: int
    seat_id: int
    coach_number: str
    seat_number: str
    seat_type: str
    status: str


class BookingResponse(BaseModel):
    id: int
    pnr: str
    user_id: int
    train_id: int
    journey_date: date
    status: str

    model_config = ConfigDict(from_attributes=True)


class BookingDetailResponse(BookingResponse):
    created_at: datetime
    seats: list[BookingSeatResponse]


class BookingCreate(BaseModel):
    train_id: int = Field(gt=0)
    source_station_id: int = Field(gt=0)
    destination_station_id: int = Field(gt=0)
    journey_date: date
    seat_ids: list[int] = Field(min_length=1, max_length=6)
