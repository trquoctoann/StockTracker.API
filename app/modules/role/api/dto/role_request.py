from pydantic import Field

from app.common.base_schema import BaseCommand
from app.modules.role.application.command.role_command import CreateRoleCommand as RoleCreateRequest


class RoleUpdateRequest(RoleCreateRequest):
    pass


class RoleSetPermissionsRequest(BaseCommand):
    permission_ids: set[int] = Field(default_factory=set)


__all__ = ["RoleCreateRequest", "RoleSetPermissionsRequest", "RoleUpdateRequest"]
