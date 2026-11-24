from pydantic import BaseModel, ConfigDict, Field


class CoachCreate(BaseModel):
    coach_number: str = Field(min_length=1, max_length=10)
    coach_type: str = Field(min_length=1, max_length=30)
    total_seats: int = Field(gt=0, le=100)


class CoachResponse(BaseModel):
    id: int
    train_id: int
    coach_number: str
    coach_type: str
    total_seats: int

    model_config = ConfigDict(from_attributes=True)