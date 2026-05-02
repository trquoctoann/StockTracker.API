"""add company_news

Revision ID: 20260429062500
Revises: 20260429062400
Create Date: 2026-04-29 06:25:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260429062500"
down_revision: str | Sequence[str] | None = "20260429062400"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_news",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("public_date", sa.Date(), nullable=True),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column("price_change_percent", sa.Float(), nullable=True),
        sa.Column("data_source_id", sa.String(length=255), nullable=True),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"], name="fk_company_news_stock_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_id", "data_source_id", name="uix_company_news_stock_id_data_source_id"),
    )
    op.create_index("ix_company_news_stock_id", "company_news", ["stock_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_news_stock_id", table_name="company_news")
    op.drop_table("company_news")
