"""DTOs (schemas Pydantic) do Quarto."""
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.room import RoomType, RoomStatus


class RoomCreate(BaseModel):
    number: int = Field(..., gt=0, description="Número único do quarto")
    type: RoomType = Field(..., description="Tipo: STANDARD, DELUXE ou SUITE")
    capacity: int = Field(..., gt=0, le=10, description="Capacidade máxima de hóspedes")
    price_per_night: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)


class RoomUpdate(BaseModel):
    type: RoomType | None = None
    capacity: int | None = Field(None, gt=0, le=10)
    price_per_night: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)
    status: RoomStatus | None = None


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    number: int
    type: str
    capacity: int
    price_per_night: Decimal
    status: str
