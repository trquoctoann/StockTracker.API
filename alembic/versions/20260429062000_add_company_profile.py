"""add company_profile

Revision ID: 20260429062000
Revises: 20260427213600
Create Date: 2026-04-29 06:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260429062000"
down_revision: str | Sequence[str] | None = "20260427213600"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("business_code", sa.String(length=255), nullable=True),
        sa.Column("business_model", sa.String(), nullable=True),
        sa.Column("founded_date", sa.Date(), nullable=True),
        sa.Column("charter_capital", sa.Float(), nullable=True),
        sa.Column("number_of_employees", sa.Integer(), nullable=True),
        sa.Column("listing_date", sa.Date(), nullable=True),
        sa.Column("par_value", sa.Float(), nullable=True),
        sa.Column("listing_price", sa.Float(), nullable=True),
        sa.Column("listing_volume", sa.Float(), nullable=True),
        sa.Column("ceo_name", sa.String(length=255), nullable=True),
        sa.Column("ceo_position", sa.String(length=255), nullable=True),
        sa.Column("inspector_name", sa.String(length=255), nullable=True),
        sa.Column("inspector_position", sa.String(length=255), nullable=True),
        sa.Column("establishment_license", sa.String(length=255), nullable=True),
        sa.Column("tax_id", sa.String(length=255), nullable=True),
        sa.Column("auditor", sa.String(length=255), nullable=True),
        sa.Column("company_type", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=100), nullable=True),
        sa.Column("fax", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("branches", sa.Integer(), nullable=True),
        sa.Column("history", sa.String(), nullable=True),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"], name="fk_company_profile_stock_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_company_profile_stock_id", "company_profile", ["stock_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_profile_stock_id", table_name="company_profile")
    op.drop_table("company_profile")
