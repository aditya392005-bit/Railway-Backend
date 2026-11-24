from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.train import Train
from app.models.station import Station
from app.models.train_stop import TrainStop
from app.schemas.train_stop import (
    TrainStopCreate,
    TrainStopResponse,
)
from app.core.permissions import require_admin
from app.services.schedule_validation import validate_stop_schedule

router = APIRouter(tags=["Train Routes"])


@router.post(
    "/trains/{train_id}/stops",
    response_model=TrainStopResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_train_stop(
    train_id: int,
    stop_data: TrainStopCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found",
        )

    station = db.get(Station, stop_data.station_id)

    if not station:
        raise HTTPException(
            status_code=404,
            detail="Station not found",
        )

    existing_stop = (
        db.query(TrainStop)
        .filter(
            TrainStop.train_id == train_id,
            TrainStop.stop_order == stop_data.stop_order,
        )
        .first()
    )

    if existing_stop:
        raise HTTPException(
            status_code=409,
            detail="This stop order is already used for this train",
        )

    # Build the proposed stop without saving it yet.
    proposed_stop = TrainStop(
        train_id=train_id,
        station_id=stop_data.station_id,
        stop_order=stop_data.stop_order,
        arrival_time=stop_data.arrival_time,
        departure_time=stop_data.departure_time,
    )

    existing_stops = (
        db.query(TrainStop)
        .filter(TrainStop.train_id == train_id)
        .all()
    )

    # Validate the complete route, including the new stop.
    validate_stop_schedule(existing_stops + [proposed_stop])

    db.add(proposed_stop)

    try:
        db.commit()
        db.refresh(proposed_stop)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not add this train stop",
        )

    return proposed_stop


@router.get(
    "/trains/{train_id}/stops",
    response_model=list[TrainStopResponse],
)
def get_train_stops(
    train_id: int,
    db: Session = Depends(get_db),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found",
        )

    return (
        db.query(TrainStop)
        .filter(TrainStop.train_id == train_id)
        .order_by(TrainStop.stop_order)
        .all()
    )


@router.delete(
    "/trains/{train_id}/stops/{stop_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_train_stop(
    train_id: int,
    stop_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found",
        )

    stop = (
        db.query(TrainStop)
        .filter(
            TrainStop.id == stop_id,
            TrainStop.train_id == train_id,
        )
        .first()
    )

    if not stop:
        raise HTTPException(
            status_code=404,
            detail="Train stop not found",
        )

    remaining_stops = (
        db.query(TrainStop)
        .filter(
            TrainStop.train_id == train_id,
            TrainStop.id != stop_id,
        )
        .all()
    )

    # Validate the route that would remain after deletion.
    validate_stop_schedule(remaining_stops)

    db.delete(stop)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not delete this train stop",
        )
