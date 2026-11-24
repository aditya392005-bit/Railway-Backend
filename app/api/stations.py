from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.permissions import require_admin
from app.database import get_db
from app.models.station import Station
from app.models.user import User
from app.schemas.station import StationCreate, StationResponse

router = APIRouter(prefix="/stations", tags=["Stations"])


@router.post(
    "/",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_station(
    data: StationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    station = Station(
        code=data.code.strip().upper(),
        name=data.name.strip(),
        city=data.city.strip(),
    )

    db.add(station)

    try:
        db.commit()
        db.refresh(station)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A station with this code already exists",
        )

    return station


@router.get("/", response_model=list[StationResponse])
def list_stations(db: Session = Depends(get_db)):
    return db.scalars(select(Station).order_by(Station.name)).all()


@router.get("/{station_id}", response_model=StationResponse)
def get_station(station_id: int, db: Session = Depends(get_db)):
    station = db.get(Station, station_id)

    if station is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found",
        )

    return station


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(
    station_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    station = db.get(Station, station_id)

    if station is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found",
        )

    db.delete(station)
    db.commit()