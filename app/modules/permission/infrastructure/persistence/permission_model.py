from typing import ClassVar

from sqlmodel import Field, UniqueConstraint

from app.common.base_model import BaseNonAuditableSQLModelWithID
from app.common.enum import RoleScope


class PermissionModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "permission"

    scope: RoleScope = Field(nullable=False)
    code: str = Field(nullable=False, max_length=255)

    __table_args__ = (UniqueConstraint("scope", "code", name="uix_permission_scope_code"),)
