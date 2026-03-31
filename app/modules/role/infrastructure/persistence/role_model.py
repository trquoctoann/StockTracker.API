from typing import ClassVar

from sqlmodel import Field, SQLModel

from app.common.base_model import BaseSQLModelWithID
from app.common.enum import RecordStatus, RoleScope, RoleType


class RoleModel(BaseSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "role"

    id: int | None = Field(default=None, primary_key=True)
    type: RoleType = Field(nullable=False)
    scope: RoleScope = Field(nullable=False)
    name: str = Field(nullable=False, max_length=255)
    description: str | None = Field(max_length=255)
    record_status: RecordStatus = Field(default=RecordStatus.ENABLED, nullable=False)
    version: int = Field(nullable=False)


class RolePermissionModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "role_permission"

    id: int | None = Field(default=None, primary_key=True)
    role_id: int = Field(nullable=False, foreign_key="role.id", index=True)
    permission_id: int = Field(nullable=False, foreign_key="permission.id", index=True)
