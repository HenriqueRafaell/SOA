"""Hierarquia de exceções de domínio.

Cada exceção carrega:
- code: identificador estável (string), usado no payload de erro
- status_code: HTTP status correspondente
- message: mensagem padrão
"""


class DomainException(Exception):
    """Exceção base do domínio."""
    code: str = "DOMAIN_ERROR"
    status_code: int = 400
    message: str = "Erro de domínio"

    def __init__(self, message: str | None = None, details: dict | list | None = None):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundException(DomainException):
    code = "NOT_FOUND"
    status_code = 404
    message = "Recurso não encontrado"


class GuestNotFoundException(NotFoundException):
    code = "GUEST_NOT_FOUND"
    message = "Hóspede não encontrado"


class RoomNotFoundException(NotFoundException):
    code = "ROOM_NOT_FOUND"
    message = "Quarto não encontrado"


class ReservationNotFoundException(NotFoundException):
    code = "RESERVATION_NOT_FOUND"
    message = "Reserva não encontrada"


class InvalidDateRangeException(DomainException):
    code = "INVALID_DATE_RANGE"
    status_code = 400
    message = "Intervalo de datas inválido: checkout deve ser posterior ao checkin"


class RoomUnavailableException(DomainException):
    code = "ROOM_UNAVAILABLE"
    status_code = 409
    message = "Quarto indisponível no período solicitado (sobreposição de reservas)"


class CapacityExceededException(DomainException):
    code = "CAPACITY_EXCEEDED"
    status_code = 400
    message = "Número de hóspedes excede a capacidade do quarto"


class InvalidReservationStateException(DomainException):
    code = "INVALID_RESERVATION_STATE"
    status_code = 409
    message = "Transição de estado da reserva inválida"


class CheckinWindowException(DomainException):
    code = "CHECKIN_WINDOW_VIOLATION"
    status_code = 422
    message = "Check-in fora da janela permitida"


class RoomHasReservationsException(DomainException):
    code = "ROOM_HAS_RESERVATIONS"
    status_code = 409
    message = "Quarto possui reservas ativas - desative (status INATIVO) ao invés de excluir"


class DuplicateResourceException(DomainException):
    code = "DUPLICATE_RESOURCE"
    status_code = 409
    message = "Recurso já existe (chave única duplicada)"


class RoomInactiveException(DomainException):
    code = "ROOM_INACTIVE"
    status_code = 409
    message = "Quarto está INATIVO e não aceita novas reservas"
