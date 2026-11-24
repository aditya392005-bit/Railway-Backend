from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.train import Train
from app.models.coach import Coach
from app.schemas.coach import CoachCreate, CoachResponse
from app.core.permissions import require_admin


router = APIRouter(tags=["Coaches"])


@router.post(
    "/trains/{train_id}/coaches",
    response_model=CoachResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_coach(
    train_id: int,
    coach_data: CoachCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    train = db.get(Train, train_id)

    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found",
        )

    coach = Coach(
        train_id=train_id,
        coach_number=coach_data.coach_number.strip().upper(),
        coach_type=coach_data.coach_type.strip(),
        total_seats=coach_data.total_seats,
    )

    db.add(coach)

    try:
        db.commit()
        db.refresh(coach)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This coach number already exists for this train",
        )

    return coach