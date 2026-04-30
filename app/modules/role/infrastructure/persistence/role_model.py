from typing import ClassVar

from sqlmodel import Field, Index

from app.common.base_model import BaseNonAuditableSQLModelWithID, BaseSQLModelWithID
from app.common.enum import RecordStatus, RoleScope, RoleType


class RoleModel(BaseSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "role"

    type: RoleType = Field(nullable=False)
    scope: RoleScope = Field(nullable=False)
    name: str = Field(nullable=False, max_length=255)
    description: str | None = Field(max_length=255)
    record_status: RecordStatus = Field(default=RecordStatus.ENABLED, nullable=False)
    version: int = Field(nullable=False)


class RolePermissionModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "role_permission"

    role_id: int = Field(nullable=False, foreign_key="role.id")
    permission_id: int = Field(nullable=False, foreign_key="permission.id")

    __table_args__ = (
        Index("ix_role_permission_role_id", "role_id"),
        Index("ix_role_permission_permission_id", "permission_id"),
    )
