
from datetime import date

from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models.train import Train
from app.models.coach import Coach
from app.models.seat import Seat
from app.models.seat_inventory import SeatInventory
from app.core.permissions import require_admin
from app.services.route_validation import validate_route

router = APIRouter(prefix="/inventory", tags=["Seat Inventory"])


@router.post("/trains/{train_id}/{journey_date}")
def initialize_inventory(
    train_id: int,
    journey_date: date,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    if journey_date < date.today():
        raise HTTPException(400, "Journey date cannot be in the past")

    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(404, "Train not found")

    coaches = db.query(Coach).filter(
        Coach.train_id == train_id
    ).all()

    seats = []

    for coach in coaches:
        seats.extend(
            db.query(Seat).filter(
                Seat.coach_id == coach.id
            ).all()
        )

    if not seats:
        raise HTTPException(400, "This train has no seats configured")

    existing = {
        row[0]
        for row in db.query(SeatInventory.seat_id).filter(
            SeatInventory.journey_date == journey_date,
            SeatInventory.seat_id.in_([seat.id for seat in seats]),
        ).all()
    }

    new_rows = [
        SeatInventory(
            seat_id=seat.id,
            journey_date=journey_date,
            status="available",
        )
        for seat in seats
        if seat.id not in existing
    ]

    db.add_all(new_rows)
    db.commit()

    return {
        "train_id": train_id,
        "journey_date": journey_date,
        "seats_found": len(seats),
        "inventory_created": len(new_rows),
        "already_initialized": len(existing),
    }



@router.get(
    "/trains/{train_id}/{journey_date}/availability",
    tags=["Inventory"],
)
def check_availability(
    train_id: int,
    journey_date: date,
    source_station_id: int = Query(gt=0),
    destination_station_id: int = Query(gt=0),
    db: Session = Depends(get_db),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(404, "Train not found")

    validate_route(
        db,
        train_id,
        source_station_id,
        destination_station_id,
    )

    statement = (
        select(
            SeatInventory.id.label("inventory_id"),
            Seat.id.label("seat_id"),
            Seat.seat_number,
            Seat.seat_type,
            Coach.coach_number,
            Coach.coach_type,
        )
        .join(Seat, SeatInventory.seat_id == Seat.id)
        .join(Coach, Seat.coach_id == Coach.id)
        .where(
            Coach.train_id == train_id,
            SeatInventory.journey_date == journey_date,
            SeatInventory.status == "available",
        )
        .order_by(Coach.coach_number, Seat.seat_number)
    )

    rows = db.execute(statement).mappings().all()

    return {
        "train_id": train_id,
        "journey_date": journey_date,
        "source_station_id": source_station_id,
        "destination_station_id": destination_station_id,
        "available_count": len(rows),
        "seats": [dict(row) for row in rows],
    }
