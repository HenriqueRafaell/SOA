"""Handlers globais de exceções, convertendo erros em ErrorResponse padronizado."""
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.domain import DomainException, DuplicateResourceException


def _error_payload(code: str, message: str, details=None) -> dict:
    return {
        "code": code,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Achatar os erros do Pydantic em uma lista amigável
        details = [
            {
                "field": ".".join(str(p) for p in err["loc"] if p not in ("body", "query", "path")),
                "message": err["msg"],
                "type": err["type"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content=_error_payload(
                "VALIDATION_ERROR",
                "Erro de validação dos dados de entrada",
                details,
            ),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        # Violação de UNIQUE / FK no banco — mapeia para 409
        dup = DuplicateResourceException()
        return JSONResponse(
            status_code=dup.status_code,
            content=_error_payload(dup.code, dup.message, {"db_error": str(exc.orig)}),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                f"HTTP_{exc.status_code}",
                str(exc.detail),
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                "INTERNAL_SERVER_ERROR",
                "Erro interno do servidor",
                {"type": exc.__class__.__name__},
            ),
        )
