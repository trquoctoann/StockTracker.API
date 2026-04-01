from pydantic import Field

from app.common.base_schema import BaseCommand
from app.modules.user.application.command.user_command import CreateUserCommand as UserCreateRequest


class UserUpdateRequest(UserCreateRequest):
    pass


class UserSetRolesRequest(BaseCommand):
    tenant_id: int | None = Field(default=None, gt=0)
    role_ids: set[int] = Field(default_factory=set)


__all__ = ["UserCreateRequest", "UserSetRolesRequest", "UserUpdateRequest"]
