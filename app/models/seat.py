from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Seat(Base):
    __tablename__ = "seats"

    __table_args__ = (
        UniqueConstraint(
            "coach_id",
            "seat_number",
            name="uq_coach_seat_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    coach_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("coaches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    seat_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Standard",
    )

    coach = relationship("Coach")