from pydantic import BaseModel, ConfigDict, Field


class StationCreate(BaseModel):
    code: str = Field(min_length=2, max_length=10)
    name: str = Field(min_length=2, max_length=150)
    city: str = Field(min_length=2, max_length=100)


class StationResponse(BaseModel):
    id: int
    code: str
    name: str
    city: str

    model_config = ConfigDict(from_attributes=True)