"""Entry point da aplicação FastAPI."""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.config import settings
from app.exceptions.handlers import register_exception_handlers
from app.routers import guests, rooms, reservations


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API REST para gestão de reservas de hotel (check-in/check-out). "
            "Arquitetura em 3 camadas: Controller → Service → Repository. "
            "FIAP - 3ESPR - CP2."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    register_exception_handlers(app)

    app.include_router(guests.router)
    app.include_router(rooms.router)
    app.include_router(reservations.router)

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="/docs")

    @app.get("/health", tags=["Health"], summary="Healthcheck")
    def health():
        return {"status": "ok", "app": settings.app_name, "version": settings.app_version}

    return app


app = create_app()
