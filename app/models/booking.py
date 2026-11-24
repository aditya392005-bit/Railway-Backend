
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Index,
    text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    pnr: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
    )
    total_fare: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    train_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trains.id"),
        nullable=False,
        index=True,
    )

    journey_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="confirmed",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    source_station_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("stations.id"),
        nullable=True,
    )

    destination_station_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("stations.id"),
        nullable=True,
    )


    user = relationship("User")
    train = relationship("Train")


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    __table_args__ = (
        Index(
            "uq_active_booking_seat_inventory",
            "seat_inventory_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    seat_inventory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seat_inventory.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    booking = relationship("Booking")
    inventory = relationship("SeatInventory")
