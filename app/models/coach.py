from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Coach(Base):
    __tablename__ = "coaches"

    __table_args__ = (
        UniqueConstraint(
            "train_id",
            "coach_number",
            name="uq_train_coach_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    train_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    coach_number: Mapped[str] = mapped_column(String(10), nullable=False)
    coach_type: Mapped[str] = mapped_column(String(30), nullable=False)

    total_seats: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    train = relationship("Train")