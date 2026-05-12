"""DTOs (schemas Pydantic) do Hóspede."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GuestCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=120, description="Nome completo")
    document: str = Field(..., min_length=5, max_length=30, description="CPF ou passaporte")
    email: EmailStr = Field(..., description="E-mail válido")
    phone: str | None = Field(None, max_length=30, description="Telefone com DDD")


class GuestUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=3, max_length=120)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)


class GuestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    document: str
    email: EmailStr
    phone: str | None
    created_at: datetime
