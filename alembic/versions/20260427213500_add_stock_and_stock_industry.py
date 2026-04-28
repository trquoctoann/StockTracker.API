"""add stock and stock industry

Revision ID: 20260427213500
Revises: 20260427191500
Create Date: 2026-04-27 21:35:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260427213500"
down_revision: str | Sequence[str] | None = "20260427191500"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()

    recordstatus = postgresql.ENUM("ENABLED", "DELETED", name="recordstatus", create_type=False)
    stockexchange = postgresql.ENUM("UPCOM", "HSX", "DELISTED", "HNX", "BOND", name="stockexchange", create_type=False)
    stocktype = postgresql.ENUM(
        "STOCK", "BOND", "FU", "DEBENTURE", "ETF", "UNIT_TRUST", "CW", name="stocktype", create_type=False
    )

    recordstatus.create(bind, checkfirst=True)
    stockexchange.create(bind, checkfirst=True)
    stocktype.create(bind, checkfirst=True)

    op.create_table(
        "stock",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("short_name", sa.String(length=255), nullable=True),
        sa.Column("exchange", stockexchange, nullable=False),
        sa.Column("type", stocktype, nullable=False),
        sa.Column("record_status", recordstatus, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol", name="uix_stock_symbol"),
    )
    op.create_index("ix_stock_exchange", "stock", ["exchange"], unique=False)
    op.create_index("ix_stock_type", "stock", ["type"], unique=False)

    op.create_table(
        "stock_industry",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("industry_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["industry_id"], ["industry.id"]),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stock_industry_stock_id", "stock_industry", ["stock_id"], unique=False)
    op.create_index("ix_stock_industry_industry_id", "stock_industry", ["industry_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_stock_industry_industry_id", table_name="stock_industry")
    op.drop_index("ix_stock_industry_stock_id", table_name="stock_industry")
    op.drop_table("stock_industry")

    op.drop_index("ix_stock_exchange", table_name="stock")
    op.drop_index("ix_stock_type", table_name="stock")
    op.drop_table("stock")

    bind = op.get_bind()
    postgresql.ENUM(name="stocktype").drop(bind, checkfirst=True)
    postgresql.ENUM(name="stockexchange").drop(bind, checkfirst=True)
