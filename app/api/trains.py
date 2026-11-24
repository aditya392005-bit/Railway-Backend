from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.train import Train
from app.models.train_stop import TrainStop
from app.models.coach import Coach
from app.models.booking import Booking
from app.schemas.train import TrainCreate, TrainUpdate, TrainResponse
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin

router = APIRouter(tags=["Trains"])


# Admin: Create a train
@router.post(
    "/trains",
    response_model=TrainResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_train(
    train_data: TrainCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    train_number = train_data.train_number.strip()
    name = train_data.name.strip()

    if not train_number or not name:
        raise HTTPException(
            status_code=400,
            detail="Train number and name cannot be empty",
        )

    existing_train = (
        db.query(Train)
        .filter(Train.train_number == train_number)
        .first()
    )

    if existing_train:
        raise HTTPException(
            status_code=409,
            detail="A train with this train number already exists",
        )

    train = Train(
        train_number=train_number,
        name=name,
    )

    db.add(train)

    try:
        db.commit()
        db.refresh(train)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not create train; train number may already exist",
        )

    return train


# Logged-in users: List trains
@router.get(
    "/trains",
    response_model=list[TrainResponse],
)
def get_trains(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(Train)
        .order_by(Train.train_number)
        .all()
    )


# Logged-in users: Get one train
@router.get(
    "/trains/{train_id}",
    response_model=TrainResponse,
)
def get_train(
    train_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found",
        )

    return train


# Admin: Update a train
@router.patch(
    "/trains/{train_id}",
    response_model=TrainResponse,
)
def update_train(
    train_id: int,
    train_data: TrainUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found",
        )

    update_data = train_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update",
        )

    for field, value in update_data.items():
        if value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise HTTPException(
                    status_code=422,
                    detail=f"{field} cannot be empty",
                )

        setattr(train, field, value)

    try:
        db.commit()
        db.refresh(train)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not update train; train number may already exist",
        )

    return train


# Admin: Delete a train only when it has no dependent data
@router.delete(
    "/trains/{train_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_train(
    train_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found",
        )

    has_stops = (
        db.query(TrainStop.id)
        .filter(TrainStop.train_id == train_id)
        .first()
    )

    has_coaches = (
        db.query(Coach.id)
        .filter(Coach.train_id == train_id)
        .first()
    )

    has_bookings = (
        db.query(Booking.id)
        .filter(Booking.train_id == train_id)
        .first()
    )

    if has_stops or has_coaches or has_bookings:
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete this train because it has routes, "
                "coaches, or bookings. Deactivate it instead."
            ),
        )

    db.delete(train)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this train because related records exist",
        )

