
from pydantic import BaseModel, ConfigDict, Field


class TrainCreate(BaseModel):
    train_number: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=2, max_length=150)


class TrainUpdate(BaseModel):
    train_number: str | None = Field(
        default=None, min_length=1, max_length=10
    )
    name: str | None = Field(
        default=None, min_length=2, max_length=150
    )


class TrainResponse(BaseModel):
    id: int
    train_number: str
    name: str

    model_config = ConfigDict(from_attributes=True)
