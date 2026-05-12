"""Router (Controller) de Quartos."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.error import ErrorResponse
from app.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from app.services.room_service import RoomService

router = APIRouter(prefix="/api/v1/rooms", tags=["Quartos"])


@router.get("", response_model=list[RoomResponse], summary="Lista todos os quartos")
def list_rooms(db: Session = Depends(get_db)):
    return RoomService(db).list_all()


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Busca quarto por ID",
)
def get_room(room_id: str, db: Session = Depends(get_db)):
    return RoomService(db).get(room_id)


@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Cadastra novo quarto",
)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    return RoomService(db).create(payload)


@router.put(
    "/{room_id}",
    response_model=RoomResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Atualiza dados do quarto",
)
def update_room(room_id: str, payload: RoomUpdate, db: Session = Depends(get_db)):
    return RoomService(db).update(room_id, payload)


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Remove um quarto (se não tiver reservas ativas)",
)
def delete_room(room_id: str, db: Session = Depends(get_db)):
    RoomService(db).delete(room_id)
    return None
