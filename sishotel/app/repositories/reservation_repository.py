"""Repository da Reserva - inclui consulta de sobreposição de período."""
from datetime import date
from sqlalchemy import select, and_, or_, not_
from sqlalchemy.orm import Session

from app.models.reservation import Reservation, ReservationStatus


class ReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Reservation]:
        return list(self.db.scalars(select(Reservation).order_by(Reservation.created_at.desc())).all())

    def get_by_id(self, reservation_id: str) -> Reservation | None:
        return self.db.get(Reservation, reservation_id)

    def has_active_reservations_for_room(self, room_id: str) -> bool:
        """Verifica se existem reservas não-canceladas e não-finalizadas para o quarto."""
        stmt = select(Reservation).where(
            and_(
                Reservation.room_id == room_id,
                Reservation.status.in_([
                    ReservationStatus.CREATED.value,
                    ReservationStatus.CHECKED_IN.value,
                ]),
            )
        ).limit(1)
        return self.db.scalar(stmt) is not None

    def find_overlapping(
        self,
        room_id: str,
        checkin: date,
        checkout: date,
        exclude_reservation_id: str | None = None,
    ) -> list[Reservation]:
        """Retorna reservas que se sobrepõem ao intervalo [checkin, checkout) para o mesmo quarto.

        Regra (do enunciado): conflito se entradaA < saídaB e entradaB < saídaA.
        Reservas CANCELED são desconsideradas.
        """
        conditions = [
            Reservation.room_id == room_id,
            Reservation.status != ReservationStatus.CANCELED.value,
            Reservation.checkin_expected < checkout,
            checkin < Reservation.checkout_expected,
        ]
        if exclude_reservation_id is not None:
            conditions.append(Reservation.id != exclude_reservation_id)

        stmt = select(Reservation).where(and_(*conditions))
        return list(self.db.scalars(stmt).all())

    def add(self, reservation: Reservation) -> Reservation:
        self.db.add(reservation)
        self.db.flush()
        return reservation

    def update(self, reservation: Reservation) -> Reservation:
        self.db.flush()
        return reservation

    def delete(self, reservation: Reservation) -> None:
        self.db.delete(reservation)
        self.db.flush()
