"""Service do Hóspede - orquestra regras de negócio e persistência."""
from sqlalchemy.orm import Session

from app.exceptions.domain import (
    DuplicateResourceException,
    GuestNotFoundException,
)
from app.models.guest import Guest
from app.repositories.guest_repository import GuestRepository
from app.schemas.guest import GuestCreate, GuestUpdate


class GuestService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = GuestRepository(db)

    def list_all(self) -> list[Guest]:
        return self.repo.list_all()

    def get(self, guest_id: str) -> Guest:
        guest = self.repo.get_by_id(guest_id)
        if not guest:
            raise GuestNotFoundException()
        return guest

    def create(self, data: GuestCreate) -> Guest:
        if self.repo.get_by_document(data.document):
            raise DuplicateResourceException("Já existe hóspede com este documento")
        if self.repo.get_by_email(data.email):
            raise DuplicateResourceException("Já existe hóspede com este e-mail")

        guest = Guest(
            full_name=data.full_name,
            document=data.document,
            email=data.email,
            phone=data.phone,
        )
        self.repo.add(guest)
        self.db.commit()
        self.db.refresh(guest)
        return guest

    def update(self, guest_id: str, data: GuestUpdate) -> Guest:
        guest = self.get(guest_id)

        if data.email and data.email != guest.email:
            existing = self.repo.get_by_email(data.email)
            if existing and existing.id != guest.id:
                raise DuplicateResourceException("E-mail já cadastrado em outro hóspede")
            guest.email = data.email

        if data.full_name:
            guest.full_name = data.full_name
        if data.phone is not None:
            guest.phone = data.phone

        self.repo.update(guest)
        self.db.commit()
        self.db.refresh(guest)
        return guest

    def delete(self, guest_id: str) -> None:
        guest = self.get(guest_id)
        self.repo.delete(guest)
        self.db.commit()
