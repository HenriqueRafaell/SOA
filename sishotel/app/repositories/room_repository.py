"""Repository do Quarto."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.room import Room


class RoomRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Room]:
        return list(self.db.scalars(select(Room).order_by(Room.number)).all())

    def get_by_id(self, room_id: str) -> Room | None:
        return self.db.get(Room, room_id)

    def get_by_number(self, number: int) -> Room | None:
        return self.db.scalar(select(Room).where(Room.number == number))

    def add(self, room: Room) -> Room:
        self.db.add(room)
        self.db.flush()
        return room

    def update(self, room: Room) -> Room:
        self.db.flush()
        return room

    def delete(self, room: Room) -> None:
        self.db.delete(room)
        self.db.flush()
