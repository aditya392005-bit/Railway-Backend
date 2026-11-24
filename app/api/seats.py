
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.train import Train
from app.models.coach import Coach
from app.models.seat import Seat
from app.schemas.seat import SeatCreate, SeatResponse
from app.schemas.coach import CoachResponse
from app.core.permissions import require_admin


router = APIRouter(tags=["Seats"])


# Create a single seat
@router.post(
    "/coaches/{coach_id}/seats",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_seat(
    coach_id: int,
    seat_data: SeatCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    coach = db.get(Coach, coach_id)

    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found",
        )

    seat_number = seat_data.seat_number.strip()

    if not seat_number:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Seat number cannot be empty",
        )

    existing = (
        db.query(Seat)
        .filter(
            Seat.coach_id == coach_id,
            Seat.seat_number == seat_number,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat number already exists",
        )

    count = (
        db.query(Seat)
        .filter(Seat.coach_id == coach_id)
        .count()
    )

    if count >= coach.total_seats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coach capacity reached",
        )

    seat = Seat(
        coach_id=coach_id,
        seat_number=seat_number,
        seat_type=seat_data.seat_type.strip(),
    )

    db.add(seat)

    try:
        db.commit()
        db.refresh(seat)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create seat; seat number may already exist",
        )

    return seat


# Get all coaches belonging to a train
@router.get(
    "/trains/{train_id}/coaches",
    response_model=list[CoachResponse],
)
def get_train_coaches(
    train_id: int,
    db: Session = Depends(get_db),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found",
        )

    return (
        db.query(Coach)
        .filter(Coach.train_id == train_id)
        .order_by(Coach.coach_number)
        .all()
    )


# Get all seats belonging to a coach
@router.get(
    "/coaches/{coach_id}/seats",
    response_model=list[SeatResponse],
)
def get_coach_seats(
    coach_id: int,
    db: Session = Depends(get_db),
):
    coach = db.get(Coach, coach_id)

    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found",
        )

    return (
        db.query(Seat)
        .filter(Seat.coach_id == coach_id)
        .order_by(Seat.seat_number)
        .all()
    )


# Get complete coach-wise seat map for a train
@router.get("/trains/{train_id}/seat-map")
def get_train_seat_map(
    train_id: int,
    db: Session = Depends(get_db),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found",
        )

    coaches = (
        db.query(Coach)
        .filter(Coach.train_id == train_id)
        .order_by(Coach.coach_number)
        .all()
    )

    result = []

    for coach in coaches:
        seats = (
            db.query(Seat)
            .filter(Seat.coach_id == coach.id)
            .order_by(Seat.seat_number)
            .all()
        )

        result.append(
            {
                "coach_id": coach.id,
                "coach_number": coach.coach_number,
                "coach_type": coach.coach_type,
                "declared_capacity": int(coach.total_seats),
                "created_seats": len(seats),
                "seats": [
                    {
                        "id": seat.id,
                        "seat_number": seat.seat_number,
                        "seat_type": seat.seat_type,
                    }
                    for seat in seats
                ],
            }
        )

    return {
        "train_id": train.id,
        "train_number": train.train_number,
        "train_name": train.name,
        "coaches": result,
    }
