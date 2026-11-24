from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    train_number: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)