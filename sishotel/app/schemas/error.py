"""Schema do payload padronizado de erro."""
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(..., description="Código identificador do erro")
    message: str = Field(..., description="Mensagem explicativa")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: dict | list | None = Field(None, description="Detalhes opcionais (ex.: campos inválidos)")
