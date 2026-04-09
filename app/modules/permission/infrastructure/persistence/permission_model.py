from typing import ClassVar

from sqlmodel import Field, SQLModel, UniqueConstraint

from app.common.enum import RoleScope


class PermissionModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "permission"

    id: int | None = Field(default=None, primary_key=True)
    scope: RoleScope = Field(nullable=False)
    code: str = Field(nullable=False, max_length=255)

    __table_args__ = (UniqueConstraint("scope", "code", name="uix_permission_scope_code"),)
