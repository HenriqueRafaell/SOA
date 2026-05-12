"""Service do Quarto - regras de negócio."""
from sqlalchemy.orm import Session

from app.exceptions.domain import (
    DuplicateResourceException,
    RoomHasReservationsException,
    RoomNotFoundException,
)
from app.models.room import Room, RoomStatus
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RoomRepository(db)
        self.reservation_repo = ReservationRepository(db)

    def list_all(self) -> list[Room]:
        return self.repo.list_all()

    def get(self, room_id: str) -> Room:
        room = self.repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundException()
        return room

    def create(self, data: RoomCreate) -> Room:
        if self.repo.get_by_number(data.number):
            raise DuplicateResourceException("Já existe quarto com este número")

        room = Room(
            number=data.number,
            type=data.type.value,
            capacity=data.capacity,
            price_per_night=data.price_per_night,
            status=RoomStatus.ATIVO.value,
        )
        self.repo.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def update(self, room_id: str, data: RoomUpdate) -> Room:
        room = self.get(room_id)

        if data.type is not None:
            room.type = data.type.value
        if data.capacity is not None:
            room.capacity = data.capacity
        if data.price_per_night is not None:
            room.price_per_night = data.price_per_night
        if data.status is not None:
            room.status = data.status.value

        self.repo.update(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def delete(self, room_id: str) -> None:
        """Regra 7: não excluir fisicamente quartos com reservas ativas."""
        room = self.get(room_id)
        if self.reservation_repo.has_active_reservations_for_room(room.id):
            raise RoomHasReservationsException()
        self.repo.delete(room)
        self.db.commit()
