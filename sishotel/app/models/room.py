"""Model SQLAlchemy do Quarto (Room) + enums de tipo e status."""
import enum
import uuid
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation


class RoomType(str, enum.Enum):
    STANDARD = "STANDARD"
    DELUXE = "DELUXE"
    SUITE = "SUITE"


class RoomStatus(str, enum.Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_night: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=RoomStatus.ATIVO.value)

    reservations: Mapped[List["Reservation"]] = relationship(back_populates="room")
