
from datetime import date

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    UniqueConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SeatInventory(Base):
    __tablename__ = "seat_inventory"

    __table_args__ = (
        UniqueConstraint(
            "seat_id",
            "journey_date",
            name="uq_seat_journey_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    seat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    journey_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="available",
    )

    seat = relationship("Seat")
