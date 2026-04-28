"""add market index and index composition

Revision ID: 20260427213600
Revises: 20260427213500
Create Date: 2026-04-27 21:36:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260427213600"
down_revision: str | Sequence[str] | None = "20260427213500"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()

    recordstatus = postgresql.ENUM("ENABLED", "DELETED", name="recordstatus", create_type=False)
    recordstatus.create(bind, checkfirst=True)

    op.create_table(
        "market_index",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("group", sa.String(length=100), nullable=True),
        sa.Column("record_status", recordstatus, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol", name="uix_market_index_symbol"),
    )
    op.create_index("ix_market_index_group", "market_index", ["group"], unique=False)

    op.create_table(
        "index_composition",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("market_index_id", sa.Integer(), nullable=False),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["market_index_id"], ["market_index.id"], name="fk_index_composition_market_index_id"),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"], name="fk_index_composition_stock_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_index_composition_market_index_id", "index_composition", ["market_index_id"], unique=False)
    op.create_index("ix_index_composition_stock_id", "index_composition", ["stock_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_index_composition_market_index_id", table_name="index_composition")
    op.drop_index("ix_index_composition_stock_id", table_name="index_composition")
    op.drop_table("index_composition")

    op.drop_index("ix_market_index_group", table_name="market_index")
    op.drop_table("market_index")
