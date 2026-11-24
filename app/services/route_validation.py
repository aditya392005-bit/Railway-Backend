
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.train_stop import TrainStop


def validate_route(
    db: Session,
    train_id: int,
    source_station_id: int,
    destination_station_id: int,
):
    stops = db.scalars(
        select(TrainStop)
        .where(TrainStop.train_id == train_id)
        .order_by(TrainStop.stop_order)
    ).all()

    if not stops:
        raise HTTPException(
            status_code=400,
            detail="No route configured for this train",
        )

    positions = {
        stop.station_id: stop.stop_order
        for stop in stops
    }

    if source_station_id not in positions:
        raise HTTPException(
            status_code=400,
            detail="Source station is not on this train's route",
        )

    if destination_station_id not in positions:
        raise HTTPException(
            status_code=400,
            detail="Destination station is not on this train's route",
        )

    source_order = positions[source_station_id]
    destination_order = positions[destination_station_id]

    if source_order >= destination_order:
        raise HTTPException(
            status_code=400,
            detail="Destination must come after the source station",
        )

    return source_order, destination_order

