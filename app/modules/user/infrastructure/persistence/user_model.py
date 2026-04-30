import uuid
from typing import ClassVar

from sqlalchemy import Column
from sqlmodel import ARRAY, Field, Index, Integer, UniqueConstraint

from app.common.base_model import BaseNonAuditableSQLModelWithID, BaseSQLModelWithUUID
from app.common.enum import RecordStatus, RoleScope, UserStatus


class UserModel(BaseSQLModelWithUUID, table=True):
    __tablename__: ClassVar[str] = "user"

    username: str = Field(nullable=False, max_length=255)
    email: str = Field(nullable=False, max_length=255)
    first_name: str = Field(nullable=False, max_length=255)
    last_name: str | None = Field(max_length=255)
    status: UserStatus = Field(default=UserStatus.ACTIVE, nullable=False)
    record_status: RecordStatus = Field(default=RecordStatus.ENABLED, nullable=False)
    version: int = Field(nullable=False)

    __table_args__ = (
        UniqueConstraint("username", name="uix_user_username"),
        UniqueConstraint("email", name="uix_user_email"),
    )


class UserRoleModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "user_role"

    scope: RoleScope = Field(nullable=False)
    user_id: uuid.UUID = Field(nullable=False, foreign_key="user.id")
    tenant_id: int | None = Field(foreign_key="tenant.id")
    role_ids: list[int] = Field(default_factory=list, sa_column=Column(ARRAY(Integer), nullable=False))
    version: int = Field(nullable=False)

    __table_args__ = (
        Index("ix_user_role_tenant_id", "tenant_id"),
        Index("ix_user_role_user_id", "user_id"),
        Index("ix_user_role_role_ids", "role_ids", postgresql_using="gin"),
    )
