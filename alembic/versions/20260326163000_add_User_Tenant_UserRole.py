"""add User Tenant UserRole

Revision ID: 20260326163000
Revises: 20260326162000
Create Date: 2026-03-26 16:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260326163000"
down_revision: str | None = "20260326162000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()

    recordstatus = postgresql.ENUM("ENABLED", "DELETED", name="recordstatus", create_type=False)
    userstatus = postgresql.ENUM("PENDING", "ACTIVE", "INACTIVE", name="userstatus", create_type=False)
    rolescope = postgresql.ENUM("ADMIN", "TENANT", name="rolescope", create_type=False)

    recordstatus.create(bind, checkfirst=True)
    userstatus.create(bind, checkfirst=True)
    rolescope.create(bind, checkfirst=True)

    op.create_table(
        "tenant",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("record_status", recordstatus, nullable=False),
        sa.Column("parent_tenant_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["parent_tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("status", userstatus, nullable=False),
        sa.Column("record_status", recordstatus, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uix_user_username"),
        sa.UniqueConstraint("email", name="uix_user_email"),
    )
    op.create_table(
        "user_role",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scope", rolescope, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("role_ids", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_role_role_ids",
        "user_role",
        ["role_ids"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_user_role_role_ids", table_name="user_role")
    op.drop_table("user_role")
    op.drop_table("user")
    op.drop_table("tenant")

    bind = op.get_bind()
    postgresql.ENUM(name="userstatus").drop(bind, checkfirst=True)
