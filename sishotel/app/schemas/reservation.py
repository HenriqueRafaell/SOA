"""DTOs (schemas Pydantic) da Reserva."""
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReservationCreate(BaseModel):
    guest_id: str = Field(..., description="UUID do hóspede")
    room_id: str = Field(..., description="UUID do quarto")
    checkin_expected: date = Field(..., description="Data prevista de check-in")
    checkout_expected: date = Field(..., description="Data prevista de check-out")
    guests_count: int = Field(1, gt=0, le=10, description="Quantidade de hóspedes")

    @model_validator(mode="after")
    def validate_dates(self):
        if self.checkout_expected <= self.checkin_expected:
            raise ValueError("checkout_expected deve ser posterior a checkin_expected")
        return self


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    guest_id: str
    room_id: str
    checkin_expected: date
    checkout_expected: date
    checkin_at: datetime | None
    checkout_at: datetime | None
    status: str
    estimated_amount: Decimal | None
    final_amount: Decimal | None
    created_at: datetime
    updated_at: datetime | None
