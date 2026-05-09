"""add stock_price_history

Revision ID: 20260502170000
Revises: 20260429062500
Create Date: 2026-05-02 17:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260502170000"
down_revision: str | Sequence[str] | None = "20260429062500"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stock_price_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("time", sa.DateTime(), nullable=False),
        sa.Column("interval", sa.String(length=10), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"], name="fk_stock_price_history_stock_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_id", "time", "interval", name="uix_stock_price_history_stock_time_interval"),
    )
    op.create_index(
        "ix_stock_price_history_stock_interval_time",
        "stock_price_history",
        ["stock_id", "interval", "time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_stock_price_history_stock_interval_time", table_name="stock_price_history")
    op.drop_table("stock_price_history")
