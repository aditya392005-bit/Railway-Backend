from datetime import time 
from pydantic import BaseModel,ConfigDict

class TrainSearchResult(BaseModel):
    train_id:int
    train_number:str
    train_name:str

    source_station_id: int
    source_station_name: str
    source_departure: time | None

    destination_station_id: int
    destination_station_name: str
    destination_arrival: time | None

    model_config = ConfigDict(from_attributes=True)