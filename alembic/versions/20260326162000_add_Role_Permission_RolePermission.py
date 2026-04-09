"""add Role Permission RolePermission

Revision ID: 20260326162000
Revises:
Create Date: 2026-03-26 16:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260326162000"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()

    recordstatus = postgresql.ENUM("ENABLED", "DELETED", name="recordstatus", create_type=False)
    roletype = postgresql.ENUM("DEFAULT", "CUSTOM", name="roletype", create_type=False)
    rolescope = postgresql.ENUM("ADMIN", "TENANT", name="rolescope", create_type=False)

    recordstatus.create(bind, checkfirst=True)
    roletype.create(bind, checkfirst=True)
    rolescope.create(bind, checkfirst=True)

    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type", roletype, nullable=False),
        sa.Column("scope", rolescope, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("record_status", recordstatus, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "permission",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scope", rolescope, nullable=False),
        sa.Column("code", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope", "code", name="uix_permission_scope_code"),
    )

    op.create_table(
        "role_permission",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.ForeignKeyConstraint(["permission_id"], ["permission.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_role_permission_permission_id", "role_permission", ["permission_id"], unique=False)
    op.create_index("ix_role_permission_role_id", "role_permission", ["role_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_role_permission_permission_id", table_name="role_permission")
    op.drop_index("ix_role_permission_role_id", table_name="role_permission")
    op.drop_table("role_permission")
    op.drop_table("permission")
    op.drop_table("role")

    bind = op.get_bind()
    postgresql.ENUM(name="recordstatus").drop(bind, checkfirst=True)
    postgresql.ENUM(name="rolescope").drop(bind, checkfirst=True)
    postgresql.ENUM(name="roletype").drop(bind, checkfirst=True)
