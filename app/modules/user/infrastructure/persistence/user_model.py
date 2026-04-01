import uuid
from typing import Any, ClassVar

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel

from app.common.base_model import BaseSQLModelWithUUID
from app.common.enum import RecordStatus, RoleScope, UserStatus


class UserModel(BaseSQLModelWithUUID, table=True):
    __tablename__: ClassVar[str] = "user"

    username: str = Field(nullable=False, unique=True, index=True, max_length=255)
    email: str = Field(nullable=False, unique=True, index=True, max_length=255)
    first_name: str = Field(nullable=False, max_length=255)
    last_name: str | None = Field(max_length=255)
    status: UserStatus = Field(default=UserStatus.ACTIVE, nullable=False)
    record_status: RecordStatus = Field(default=RecordStatus.ENABLED, nullable=False)
    version: int = Field(nullable=False)


class UserRoleModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "user_role"

    id: int | None = Field(default=None, primary_key=True)
    scope: RoleScope = Field(nullable=False)
    user_id: uuid.UUID = Field(nullable=False, foreign_key="user.id")
    tenant_id: int | None = Field(foreign_key="tenant.id")
    role_ids: list[int] = Field(default_factory=list, sa_column=Column[Any](JSON, nullable=False))
    version: int = Field(nullable=False)
