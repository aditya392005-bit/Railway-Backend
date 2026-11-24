from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column

from app.database import Base
class Station(Base):
    __tablename__="stations"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)