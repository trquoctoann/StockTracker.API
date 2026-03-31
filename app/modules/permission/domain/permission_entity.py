from pydantic import BaseModel

from app.common.enum import RoleScope


class PermissionEntity(BaseModel):
    id: int | None = None
    scope: RoleScope
    code: str
