
from sqlalchemy import (
    Column, Integer, ForeignKey, String, Numeric,
    DateTime, func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)

    payment_id = Column(
        Integer,
        ForeignKey("payments.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    reason = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    processed_at = Column(DateTime(timezone=True), nullable=True)

    payment = relationship("Payment")
