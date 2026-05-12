"""V2 seed - dados iniciais (hóspedes, quartos e uma reserva exemplo).

Revision ID: 0002_seed
Revises: 0001_init
Create Date: 2026-05-04

"""
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_seed"
down_revision: Union[str, None] = "0001_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    guests = sa.table(
        "guests",
        sa.column("id", sa.String),
        sa.column("full_name", sa.String),
        sa.column("document", sa.String),
        sa.column("email", sa.String),
        sa.column("phone", sa.String),
    )
    op.bulk_insert(
        guests,
        [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "full_name": "Ana Silva",
                "document": "12345678901",
                "email": "ana@example.com",
                "phone": "+55-11-99999-1111",
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "full_name": "Bruno Souza",
                "document": "98765432100",
                "email": "bruno@example.com",
                "phone": "+55-21-98888-2222",
            },
        ],
    )

    rooms = sa.table(
        "rooms",
        sa.column("id", sa.String),
        sa.column("number", sa.Integer),
        sa.column("type", sa.String),
        sa.column("capacity", sa.Integer),
        sa.column("price_per_night", sa.Numeric),
        sa.column("status", sa.String),
    )
    op.bulk_insert(
        rooms,
        [
            {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "number": 101,
                "type": "STANDARD",
                "capacity": 2,
                "price_per_night": 250.00,
                "status": "ATIVO",
            },
            {
                "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "number": 201,
                "type": "DELUXE",
                "capacity": 3,
                "price_per_night": 380.00,
                "status": "ATIVO",
            },
            {
                "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                "number": 301,
                "type": "SUITE",
                "capacity": 4,
                "price_per_night": 520.00,
                "status": "ATIVO",
            },
        ],
    )

    reservations = sa.table(
        "reservations",
        sa.column("id", sa.String),
        sa.column("guest_id", sa.String),
        sa.column("room_id", sa.String),
        sa.column("checkin_expected", sa.Date),
        sa.column("checkout_expected", sa.Date),
        sa.column("status", sa.String),
        sa.column("estimated_amount", sa.Numeric),
    )
    op.bulk_insert(
        reservations,
        [
            {
                "id": "99999999-9999-9999-9999-999999999999",
                "guest_id": "11111111-1111-1111-1111-111111111111",
                "room_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "checkin_expected": date(2026, 6, 5),
                "checkout_expected": date(2026, 6, 7),
                "status": "CREATED",
                "estimated_amount": 500.00,
            },
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM reservations WHERE id = '99999999-9999-9999-9999-999999999999'")
    op.execute(
        "DELETE FROM rooms WHERE id IN ("
        "'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',"
        "'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',"
        "'cccccccc-cccc-cccc-cccc-cccccccccccc')"
    )
    op.execute(
        "DELETE FROM guests WHERE id IN ("
        "'11111111-1111-1111-1111-111111111111',"
        "'22222222-2222-2222-2222-222222222222')"
    )
