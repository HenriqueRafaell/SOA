"""V1 init - cria tabelas guests, rooms e reservations.

Revision ID: 0001_init
Revises:
Create Date: 2026-05-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "guests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("document", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_guests"),
        sa.UniqueConstraint("document", name="uq_guests_document"),
        sa.UniqueConstraint("email", name="uq_guests_email"),
    )

    op.create_table(
        "rooms",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("price_per_night", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_rooms"),
        sa.UniqueConstraint("number", name="uq_rooms_number"),
    )
    op.create_index("idx_rooms_status", "rooms", ["status"])

    op.create_table(
        "reservations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("guest_id", sa.String(length=36), nullable=False),
        sa.Column("room_id", sa.String(length=36), nullable=False),
        sa.Column("checkin_expected", sa.Date(), nullable=False),
        sa.Column("checkout_expected", sa.Date(), nullable=False),
        sa.Column("checkin_at", sa.DateTime(), nullable=True),
        sa.Column("checkout_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("estimated_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("final_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_reservations"),
        sa.ForeignKeyConstraint(["guest_id"], ["guests.id"], name="fk_reservations_guest"),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], name="fk_reservations_room"),
    )
    op.create_index("idx_reservations_room", "reservations", ["room_id"])
    op.create_index("idx_reservations_status", "reservations", ["status"])
    op.create_index(
        "idx_reservations_date_range",
        "reservations",
        ["checkin_expected", "checkout_expected"],
    )


def downgrade() -> None:
    op.drop_index("idx_reservations_date_range", table_name="reservations")
    op.drop_index("idx_reservations_status", table_name="reservations")
    op.drop_index("idx_reservations_room", table_name="reservations")
    op.drop_table("reservations")

    op.drop_index("idx_rooms_status", table_name="rooms")
    op.drop_table("rooms")

    op.drop_table("guests")
