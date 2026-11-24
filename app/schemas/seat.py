from pydantic import BaseModel, ConfigDict, Field


class SeatCreate(BaseModel):
    seat_number: str = Field(min_length=1, max_length=10)
    seat_type: str = Field(
        default="Standard",
        min_length=1,
        max_length=30,
    )


class SeatResponse(BaseModel):
    id: int
    coach_id: int
    seat_number: str
    seat_type: str

    model_config = ConfigDict(from_attributes=True)