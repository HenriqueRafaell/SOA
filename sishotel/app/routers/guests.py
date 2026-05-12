"""Router (Controller) de Hóspedes."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.error import ErrorResponse
from app.schemas.guest import GuestCreate, GuestResponse, GuestUpdate
from app.services.guest_service import GuestService

router = APIRouter(prefix="/api/v1/guests", tags=["Hóspedes"])


@router.get(
    "",
    response_model=list[GuestResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista todos os hóspedes",
)
def list_guests(db: Session = Depends(get_db)):
    return GuestService(db).list_all()


@router.get(
    "/{guest_id}",
    response_model=GuestResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
    summary="Busca hóspede por ID",
)
def get_guest(guest_id: str, db: Session = Depends(get_db)):
    return GuestService(db).get(guest_id)


@router.post(
    "",
    response_model=GuestResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Cadastra novo hóspede",
)
def create_guest(payload: GuestCreate, db: Session = Depends(get_db)):
    return GuestService(db).create(payload)


@router.put(
    "/{guest_id}",
    response_model=GuestResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Atualiza dados do hóspede",
)
def update_guest(guest_id: str, payload: GuestUpdate, db: Session = Depends(get_db)):
    return GuestService(db).update(guest_id, payload)


@router.delete(
    "/{guest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Remove um hóspede",
)
def delete_guest(guest_id: str, db: Session = Depends(get_db)):
    GuestService(db).delete(guest_id)
    return None
