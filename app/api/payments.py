
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/{booking_id}/mock-pay",
    response_model=PaymentResponse,
)
def mock_payment(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = db.scalar(
            select(Booking)
            .where(
                Booking.id == booking_id,
                Booking.user_id == current_user.id,
            )
            .with_for_update()
        )

        if not booking:
            raise HTTPException(404, "Booking not found")

        payment = db.scalar(
            select(Payment)
            .where(Payment.booking_id == booking.id)
            .with_for_update()
        )

        if not payment:
            raise HTTPException(404, "Payment record not found")

        if payment.status != "pending":
            raise HTTPException(
                409,
                f"Payment cannot be processed: {payment.status}",
            )

        if booking.status != "pending_payment":
            raise HTTPException(
                409,
                "Booking is not awaiting payment",
            )

        payment.status = "succeeded"
        payment.transaction_ref = secrets.token_hex(8).upper()
        payment.paid_at = datetime.now(timezone.utc)

        booking.status = "confirmed"

        db.commit()
        db.refresh(payment)

        return payment

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
