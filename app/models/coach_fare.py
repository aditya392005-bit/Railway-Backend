
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CoachFare(Base):
    __tablename__ = "coach_fares"

    __table_args__ = (
        UniqueConstraint(
            "train_id",
            "coach_type",
            name="uq_train_coach_fare",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    train_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    coach_type: Mapped[str] = mapped_column(String(30), nullable=False)

    fare_per_seat: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    train = relationship("Train")
