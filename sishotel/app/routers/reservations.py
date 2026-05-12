"""Router (Controller) de Reservas."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.error import ErrorResponse
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/api/v1/reservations", tags=["Reservas"])


@router.get("", response_model=list[ReservationResponse], summary="Lista todas as reservas")
def list_reservations(db: Session = Depends(get_db)):
    return ReservationService(db).list_all()


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Busca reserva por ID",
)
def get_reservation(reservation_id: str, db: Session = Depends(get_db)):
    return ReservationService(db).get(reservation_id)


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Datas/capacidade inválidas"},
        404: {"model": ErrorResponse, "description": "Hóspede ou quarto não encontrado"},
        409: {"model": ErrorResponse, "description": "Quarto indisponível no período"},
    },
    summary="Cria nova reserva",
)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)):
    return ReservationService(db).create(payload)


@router.post(
    "/{reservation_id}/check-in",
    response_model=ReservationResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse, "description": "Transição de estado inválida"},
        422: {"model": ErrorResponse, "description": "Fora da janela de check-in"},
    },
    summary="Realiza check-in da reserva",
)
def check_in(reservation_id: str, db: Session = Depends(get_db)):
    return ReservationService(db).check_in(reservation_id)


@router.post(
    "/{reservation_id}/check-out",
    response_model=ReservationResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse, "description": "Transição de estado inválida"},
    },
    summary="Realiza check-out da reserva (calcula valor final)",
)
def check_out(reservation_id: str, db: Session = Depends(get_db)):
    return ReservationService(db).check_out(reservation_id)


@router.post(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse, "description": "Reserva não está em CREATED"},
    },
    summary="Cancela reserva (apenas se estiver em CREATED)",
)
def cancel(reservation_id: str, db: Session = Depends(get_db)):
    return ReservationService(db).cancel(reservation_id)
