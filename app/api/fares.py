
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.coach_fare import CoachFare
from app.models.train import Train
from app.models.user import User
from app.schemas.coach_fare import CoachFareCreate, CoachFareResponse
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin

router = APIRouter(prefix="/fares", tags=["Fares"])


@router.post("/", response_model=CoachFareResponse, status_code=201)
def create_fare(
    payload: CoachFareCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if not db.get(Train, payload.train_id):
        raise HTTPException(404, "Train not found")

    fare = CoachFare(**payload.model_dump())
    db.add(fare)

    try:
        db.commit()
        db.refresh(fare)
        return fare
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            "A fare already exists for this train and coach type",
        )


@router.get(
    "/train/{train_id}",
    response_model=list[CoachFareResponse],
)
def get_train_fares(
    train_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.get(Train, train_id):
        raise HTTPException(404, "Train not found")

    return db.scalars(
        select(CoachFare)
        .where(CoachFare.train_id == train_id)
        .order_by(CoachFare.coach_type)
    ).all()
