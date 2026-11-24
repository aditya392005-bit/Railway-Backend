from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased

from app.database import get_db
from app.models.train import Train
from app.models.train_stop import TrainStop
from app.models.station import Station
from app.schemas.train_search import TrainSearchResult


router = APIRouter(prefix="/search", tags=["Train Search"])


@router.get("/trains", response_model=list[TrainSearchResult])
def search_trains(
    source_station_id: int = Query(gt=0),
    destination_station_id: int = Query(gt=0),
    db: Session = Depends(get_db),
):
    if source_station_id == destination_station_id:
        raise HTTPException(
            status_code=400,
            detail="Source and destination stations must be different",
        )

    source_stop = aliased(TrainStop)
    destination_stop = aliased(TrainStop)
    source_station = aliased(Station)
    destination_station = aliased(Station)

    results = (
        db.query(
            Train.id.label("train_id"),
            Train.train_number.label("train_number"),
            Train.name.label("train_name"),
            source_station.id.label("source_station_id"),
            source_station.name.label("source_station_name"),
            source_stop.departure_time.label("source_departure"),
            destination_station.id.label("destination_station_id"),
            destination_station.name.label("destination_station_name"),
            destination_stop.arrival_time.label("destination_arrival"),
        )
        .join(source_stop, source_stop.train_id == Train.id)
        .join(
            destination_stop,
            destination_stop.train_id == Train.id,
        )
        .join(
            source_station,
            source_station.id == source_stop.station_id,
        )
        .join(
            destination_station,
            destination_station.id == destination_stop.station_id,
        )
        .filter(
            source_stop.station_id == source_station_id,
            destination_stop.station_id == destination_station_id,
            source_stop.stop_order < destination_stop.stop_order,
        )
        .order_by(source_stop.departure_time)
        .all()
    )

    return [
        TrainSearchResult.model_validate(
            row._mapping
        )
        for row in results
    ]