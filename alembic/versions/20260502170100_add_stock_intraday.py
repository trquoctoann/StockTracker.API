"""add stock_intraday

Revision ID: 20260502170100
Revises: 20260502170000
Create Date: 2026-05-02 17:01:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260502170100"
down_revision: str | Sequence[str] | None = "20260502170000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stock_intraday",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("time", sa.DateTime(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
        sa.Column("match_type", sa.String(length=20), nullable=False),
        sa.Column("data_source_id", sa.String(length=255), nullable=True),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"], name="fk_stock_intraday_stock_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_id", "time", "data_source_id", name="uix_stock_intraday_stock_time_source"),
    )
    op.create_index(
        "ix_stock_intraday_stock_id_time",
        "stock_intraday",
        ["stock_id", "time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_stock_intraday_stock_id_time", table_name="stock_intraday")
    op.drop_table("stock_intraday")
