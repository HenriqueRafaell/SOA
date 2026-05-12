"""Service da Reserva - implementa a FSM e todas as regras de negócio.

Transições válidas:
  CREATED → CHECKED_IN → CHECKED_OUT
  CREATED → CANCELED
"""
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.exceptions.domain import (
    CapacityExceededException,
    CheckinWindowException,
    GuestNotFoundException,
    InvalidDateRangeException,
    InvalidReservationStateException,
    ReservationNotFoundException,
    RoomInactiveException,
    RoomNotFoundException,
    RoomUnavailableException,
)
from app.models.reservation import Reservation, ReservationStatus
from app.models.room import RoomStatus
from app.repositories.guest_repository import GuestRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.reservation import ReservationCreate


class ReservationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReservationRepository(db)
        self.guest_repo = GuestRepository(db)
        self.room_repo = RoomRepository(db)

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def list_all(self) -> list[Reservation]:
        return self.repo.list_all()

    def get(self, reservation_id: str) -> Reservation:
        reservation = self.repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundException()
        return reservation

    # ------------------------------------------------------------------ #
    # Criação
    # ------------------------------------------------------------------ #
    def create(self, data: ReservationCreate) -> Reservation:
        # Regra 1: datas (Pydantic já validou, mas reforçamos no domínio)
        if data.checkout_expected <= data.checkin_expected:
            raise InvalidDateRangeException()

        # Existência de hóspede e quarto
        guest = self.guest_repo.get_by_id(data.guest_id)
        if not guest:
            raise GuestNotFoundException()

        room = self.room_repo.get_by_id(data.room_id)
        if not room:
            raise RoomNotFoundException()

        # Quarto deve estar ATIVO
        if room.status != RoomStatus.ATIVO.value:
            raise RoomInactiveException()

        # Regra 3: capacidade
        if data.guests_count > room.capacity:
            raise CapacityExceededException(
                f"O quarto comporta no máximo {room.capacity} hóspedes; solicitados {data.guests_count}"
            )

        # Regra 2: disponibilidade (sobreposição)
        overlaps = self.repo.find_overlapping(
            room_id=room.id,
            checkin=data.checkin_expected,
            checkout=data.checkout_expected,
        )
        if overlaps:
            raise RoomUnavailableException()

        # Valor estimado
        nights = (data.checkout_expected - data.checkin_expected).days
        estimated = Decimal(nights) * Decimal(room.price_per_night)

        reservation = Reservation(
            guest_id=guest.id,
            room_id=room.id,
            checkin_expected=data.checkin_expected,
            checkout_expected=data.checkout_expected,
            status=ReservationStatus.CREATED.value,
            estimated_amount=estimated,
        )
        self.repo.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    # ------------------------------------------------------------------ #
    # Cancelamento
    # ------------------------------------------------------------------ #
    def cancel(self, reservation_id: str) -> Reservation:
        reservation = self.get(reservation_id)

        # Regra 4 (FSM): só pode cancelar enquanto CREATED
        if reservation.status != ReservationStatus.CREATED.value:
            raise InvalidReservationStateException(
                f"Não é possível cancelar reserva no estado {reservation.status}; "
                f"cancelamento permitido apenas em CREATED"
            )

        reservation.status = ReservationStatus.CANCELED.value
        reservation.updated_at = datetime.now(timezone.utc)
        self.repo.update(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    # ------------------------------------------------------------------ #
    # Check-in
    # ------------------------------------------------------------------ #
    def check_in(self, reservation_id: str) -> Reservation:
        reservation = self.get(reservation_id)

        # Regra 4 (FSM): só CREATED → CHECKED_IN
        if reservation.status != ReservationStatus.CREATED.value:
            raise InvalidReservationStateException(
                f"Check-in só é permitido para reservas em CREATED; estado atual: {reservation.status}"
            )

        # Regra 5: janela de check-in - permitido a partir da data prevista
        today = date.today()
        if today < reservation.checkin_expected:
            raise CheckinWindowException(
                f"Check-in disponível a partir de {reservation.checkin_expected.isoformat()}"
            )

        reservation.status = ReservationStatus.CHECKED_IN.value
        reservation.checkin_at = datetime.now(timezone.utc)
        reservation.updated_at = datetime.now(timezone.utc)
        self.repo.update(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    # ------------------------------------------------------------------ #
    # Check-out
    # ------------------------------------------------------------------ #
    def check_out(self, reservation_id: str) -> Reservation:
        reservation = self.get(reservation_id)

        # Regra 4 (FSM): só CHECKED_IN → CHECKED_OUT
        if reservation.status != ReservationStatus.CHECKED_IN.value:
            raise InvalidReservationStateException(
                f"Check-out só é permitido para reservas em CHECKED_IN; estado atual: {reservation.status}"
            )

        checkout_at = datetime.now(timezone.utc)
        room = self.room_repo.get_by_id(reservation.room_id)

        # Regra 6: cálculo do valor final
        # diarias = max(1, diasEntre(checkinEfetivo, checkoutEfetivo))
        checkin_date = reservation.checkin_at.date() if reservation.checkin_at else reservation.checkin_expected
        checkout_date = checkout_at.date()
        nights = max(1, (checkout_date - checkin_date).days)
        final_amount = Decimal(nights) * Decimal(room.price_per_night)

        reservation.status = ReservationStatus.CHECKED_OUT.value
        reservation.checkout_at = checkout_at
        reservation.final_amount = final_amount
        reservation.updated_at = datetime.now(timezone.utc)
        self.repo.update(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation
