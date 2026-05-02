"""add company_event

Revision ID: 20260429062400
Revises: 20260429062300
Create Date: 2026-04-29 06:24:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260429062400"
down_revision: str | Sequence[str] | None = "20260429062300"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("public_date", sa.Date(), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("record_date", sa.Date(), nullable=True),
        sa.Column("exright_date", sa.Date(), nullable=True),
        sa.Column("data_source_id", sa.String(length=255), nullable=True),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock.id"], name="fk_company_event_stock_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_id", "data_source_id", name="uix_company_event_stock_id_data_source_id"),
    )
    op.create_index("ix_company_event_stock_id", "company_event", ["stock_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_event_stock_id", table_name="company_event")
    op.drop_table("company_event")
