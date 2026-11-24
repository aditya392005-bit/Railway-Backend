
import secrets
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.booking import Booking, BookingSeat
from app.models.seat_inventory import SeatInventory
from app.models.seat import Seat
from app.models.coach import Coach
from app.models.train import Train
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingSeatResponse,
    BookingDetailResponse,
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.coach_fare import CoachFare
from app.models.payment import Payment
from app.services.route_validation import validate_route

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def get_booking_details(
    db: Session,
    booking: Booking,
) -> BookingDetailResponse:
    statement = (
        select(
            BookingSeat.seat_inventory_id,
            SeatInventory.seat_id,
            Coach.coach_number,
            Seat.seat_number,
            Seat.seat_type,
            BookingSeat.status,
        )
        .join(
            SeatInventory,
            BookingSeat.seat_inventory_id == SeatInventory.id,
        )
        .join(Seat, SeatInventory.seat_id == Seat.id)
        .join(Coach, Seat.coach_id == Coach.id)
        .where(BookingSeat.booking_id == booking.id)
        .order_by(Coach.coach_number, Seat.seat_number)
    )

    rows = db.execute(statement).all()

    seats = [
        BookingSeatResponse(
            seat_inventory_id=row.seat_inventory_id,
            seat_id=row.seat_id,
            coach_number=row.coach_number,
            seat_number=row.seat_number,
            seat_type=row.seat_type,
            status=row.status,
        )
        for row in rows
    ]

    return BookingDetailResponse(
        id=booking.id,
        pnr=booking.pnr,
        user_id=booking.user_id,
        train_id=booking.train_id,
        journey_date=booking.journey_date,
        status=booking.status,
        created_at=booking.created_at,
        seats=seats,
    )


@router.get(
    "/pnr/{pnr}/details",
    response_model=BookingDetailResponse,
)
def get_booking_by_pnr(
    pnr: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.scalar(
        select(Booking).where(
            Booking.pnr == pnr.upper(),
            Booking.user_id == current_user.id,
        )
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    return get_booking_details(db, booking)


def generate_pnr() -> str:
    return secrets.token_hex(5).upper()


@router.post(
    "/",
    response_model=BookingDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.journey_date < date.today():
        raise HTTPException(400, "Journey date cannot be in the past")

    if len(payload.seat_ids) != len(set(payload.seat_ids)):
        raise HTTPException(400, "Duplicate seat IDs in request")

    try:
        train = db.get(Train, payload.train_id)

        if train is None:
            raise HTTPException(404, "Train not found")
        
        source_order, destination_order = validate_route(
            db=db,
            train_id=payload.train_id,
            source_station_id=payload.source_station_id,
            destination_station_id=payload.destination_station_id,
        )
        

        # Lock inventory rows so concurrent requests serialize
        # their attempts to book the same inventory.
        inventory_rows = db.scalars(
            select(SeatInventory)
            .where(
                SeatInventory.seat_id.in_(payload.seat_ids),
                SeatInventory.journey_date == payload.journey_date,
            )
            .order_by(SeatInventory.id)
            .with_for_update()
        ).all()

        if len(inventory_rows) != len(payload.seat_ids):
            raise HTTPException(
                409,
                "Seat inventory is missing for this journey date",
            )

        inventory_by_seat = {
            row.seat_id: row for row in inventory_rows
        }

        total_fare = Decimal("0.00")
        for seat_id in payload.seat_ids:
            seat = db.get(Seat, seat_id)

            if seat is None:
                raise HTTPException(404, f"Seat {seat_id} not found")

            coach = db.get(Coach, seat.coach_id)

            if coach is None or coach.train_id != payload.train_id:
                raise HTTPException(
                    400,
                    f"Seat {seat_id} does not belong to this train",
                )

            inventory = inventory_by_seat[seat_id]

            if inventory.status != "available":
                raise HTTPException(
                    409,
                    f"Seat {seat_id} is not available",
                )

            fare = db.scalar(
                select(CoachFare).where(
                    CoachFare.train_id == payload.train_id,
                    CoachFare.coach_type == coach.coach_type,
                )
            )
            if fare is None:
                raise HTTPException(
                    400,
                    f"No fare configured for coach type {coach.coach_type}",
                )

            total_fare += fare.fare_per_seat

        booking = Booking(
            pnr=generate_pnr(),
            user_id=current_user.id,
            train_id=payload.train_id,
            journey_date=payload.journey_date,
            status="pending_payment",
            total_fare=total_fare,
            source_station_id=payload.source_station_id,
            destination_station_id=payload.destination_station_id,
        )

        db.add(booking)
        db.flush()

        for seat_id in payload.seat_ids:
            inventory = inventory_by_seat[seat_id]
            inventory.status = "booked"

            db.add(
                BookingSeat(
                    booking_id=booking.id,
                    seat_inventory_id=inventory.id,
                    status="active",
                )
            )
        db.add(
            Payment(
                booking_id=booking.id,
                amount=total_fare,
                status="pending",
            )
        )

        db.commit()
        db.refresh(booking)

        return get_booking_details(db, booking)
    

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            "Booking conflict detected. Please try again.",
        )
    except Exception:
        db.rollback()
        raise

    


@router.get("/me", response_model=list[BookingResponse])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )





@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = db.scalars(
            select(Booking)
            .where(
                Booking.id == booking_id,
                Booking.user_id == current_user.id,
            )
            .with_for_update()
        ).first()

        if not booking:
            raise HTTPException(404, "Booking not found")

        if booking.status != "confirmed":
            raise HTTPException(
                409,
                "Booking is not active and cannot be cancelled",
            )

        assignments = db.scalars(
            select(BookingSeat)
            .where(
                BookingSeat.booking_id == booking.id,
                BookingSeat.status == "active",
            )
            .order_by(BookingSeat.seat_inventory_id)
            .with_for_update()
        ).all()

        for assignment in assignments:
            inventory = db.scalars(
                select(SeatInventory)
                .where(
                    SeatInventory.id == assignment.seat_inventory_id
                )
                .with_for_update()
            ).first()

            if inventory:
                inventory.status = "available"

            assignment.status = "cancelled"

        booking.status = "cancelled"

        db.commit()
        db.refresh(booking)

        return booking

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
