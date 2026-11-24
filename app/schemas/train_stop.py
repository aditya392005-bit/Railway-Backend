from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class TrainStopCreate(BaseModel):
    station_id: int
    stop_order: int = Field(gt=0)
    arrival_time: time | None = None
    departure_time: time | None = None


class TrainStopResponse(BaseModel):
    id: int
    train_id: int
    station_id: int
    stop_order: int
    arrival_time: time | None
    departure_time: time | None

    model_config = ConfigDict(from_attributes=True)