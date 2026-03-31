from typing import ClassVar

from sqlmodel import Field, SQLModel

from app.common.enum import RoleScope


class PermissionModel(SQLModel, table=True):
    __tablename__: ClassVar[str] = "permission"

    id: int | None = Field(default=None, primary_key=True)
    scope: RoleScope = Field(nullable=False)
    code: str = Field(nullable=False, unique=True, index=True, max_length=255)
