"""Repository do Hóspede - encapsula acesso a dados."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.guest import Guest


class GuestRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Guest]:
        return list(self.db.scalars(select(Guest).order_by(Guest.full_name)).all())

    def get_by_id(self, guest_id: str) -> Guest | None:
        return self.db.get(Guest, guest_id)

    def get_by_document(self, document: str) -> Guest | None:
        return self.db.scalar(select(Guest).where(Guest.document == document))

    def get_by_email(self, email: str) -> Guest | None:
        return self.db.scalar(select(Guest).where(Guest.email == email))

    def add(self, guest: Guest) -> Guest:
        self.db.add(guest)
        self.db.flush()
        return guest

    def update(self, guest: Guest) -> Guest:
        self.db.flush()
        return guest

    def delete(self, guest: Guest) -> None:
        self.db.delete(guest)
        self.db.flush()
