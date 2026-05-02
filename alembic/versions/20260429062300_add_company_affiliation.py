"""add company_affiliation

Revision ID: 20260429062300
Revises: 20260429062200
Create Date: 2026-04-29 06:23:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260429062300"
down_revision: str | Sequence[str] | None = "20260429062200"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_affiliation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("ownership_percent", sa.Float(), nullable=True),
        sa.Column("data_source_id", sa.String(length=255), nullable=True),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"], name="fk_company_affiliation_stock_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_id", "data_source_id", name="uix_company_affiliation_stock_id_data_source_id"),
    )
    op.create_index("ix_company_affiliation_stock_id", "company_affiliation", ["stock_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_affiliation_stock_id", table_name="company_affiliation")
    op.drop_table("company_affiliation")
