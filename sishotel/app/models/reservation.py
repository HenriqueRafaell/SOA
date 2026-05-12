"""Model SQLAlchemy da Reserva (Reservation) + enum de status (FSM)."""
import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.guest import Guest
from app.models.room import Room


class ReservationStatus(str, enum.Enum):
    CREATED = "CREATED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELED = "CANCELED"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    guest_id: Mapped[str] = mapped_column(String(36), ForeignKey("guests.id"), nullable=False)
    room_id: Mapped[str] = mapped_column(String(36), ForeignKey("rooms.id"), nullable=False)
    checkin_expected: Mapped[date] = mapped_column(Date, nullable=False)
    checkout_expected: Mapped[date] = mapped_column(Date, nullable=False)
    checkin_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    checkout_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=ReservationStatus.CREATED.value)
    estimated_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    final_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.current_timestamp(), nullable=True)

    guest: Mapped["Guest"] = relationship(back_populates="reservations")
    room: Mapped["Room"] = relationship(back_populates="reservations")
