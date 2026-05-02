"""add company_shareholder

Revision ID: 20260429062100
Revises: 20260429062000
Create Date: 2026-04-29 06:21:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260429062100"
down_revision: str | Sequence[str] | None = "20260429062000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_shareholder",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("ownership_percent", sa.Float(), nullable=True),
        sa.Column("updated_date", sa.Date(), nullable=True),
        sa.Column("data_source_id", sa.String(length=255), nullable=True),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"], name="fk_company_shareholder_stock_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_id", "data_source_id", name="uix_company_shareholder_stock_id_data_source_id"),
    )
    op.create_index("ix_company_shareholder_stock_id", "company_shareholder", ["stock_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_shareholder_stock_id", table_name="company_shareholder")
    op.drop_table("company_shareholder")
