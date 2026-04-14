from __future__ import annotations

from typing import Annotated

from pydantic import Field, StringConstraints, field_validator

from app.common.base_schema import BaseCommand
from app.common.enum import RoleScope
from app.exception.exception import ValidationException

Name = Annotated[str, StringConstraints(min_length=1, max_length=255)]
Description = Annotated[str, StringConstraints(max_length=255)]


class CreateRoleCommand(BaseCommand):
    scope: RoleScope
    name: Name
    description: Description | None = Field(default=None)

    permission_ids: set[int] | None = Field(default=None)

    @field_validator("permission_ids")
    @classmethod
    def _validate_permission_ids(cls, v: set[int] | list[int] | None) -> set[int] | None:
        if v is None:
            return None
        items = [int(x) for x in v]
        if any(x <= 0 for x in items):
            raise ValidationException(message_key="errors.business.role.permission_ids_invalid")
        seen: set[int] = set()
        out: list[int] = []
        for x in items:
            if x in seen:
                continue
            seen.add(x)
            out.append(x)
        return set(out)


class UpdateRoleCommand(CreateRoleCommand):
    id: int


class SetRolePermissionsCommand(BaseCommand):
    id: int
    permission_ids: set[int]
