from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class TrainStop(Base):
    __tablename__ = "train_stops"

    __table_args__ = (
        UniqueConstraint(
            "train_id",
            "stop_order",
            name="uq_train_stop_order",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    train_id = Column(
        Integer,
        ForeignKey("trains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    station_id = Column(
        Integer,
        ForeignKey("stations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    stop_order = Column(Integer, nullable=False)

    arrival_time = Column(Time, nullable=True)
    departure_time = Column(Time, nullable=True)

    train = relationship("Train")
    station = relationship("Station")