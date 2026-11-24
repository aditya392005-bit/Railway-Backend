
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.refund import Refund
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.user import User
from app.schemas.refund import RefundResponse
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin

router = APIRouter(prefix="/refunds", tags=["Refunds"])


@router.get("/me", response_model=list[RefundResponse])
def my_refunds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(
        select(Refund)
        .join(Payment, Refund.payment_id == Payment.id)
        .join(Booking, Payment.booking_id == Booking.id)
        .where(Booking.user_id == current_user.id)
        .order_by(Refund.created_at.desc())
    ).all()


@router.post(
    "/{refund_id}/mock-complete",
    response_model=RefundResponse,
)
def complete_mock_refund(
    refund_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    try:
        refund = db.scalar(
            select(Refund)
            .where(Refund.id == refund_id)
            .with_for_update()
        )

        if not refund:
            raise HTTPException(404, "Refund not found")

        if refund.status != "pending":
            raise HTTPException(
                409,
                f"Refund cannot be processed: {refund.status}",
            )

        refund.status = "completed"
        refund.processed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(refund)

        return refund

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
