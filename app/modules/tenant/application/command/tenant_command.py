from __future__ import annotations

from typing import Annotated

from pydantic import Field, StringConstraints

from app.common.base_schema import BaseCommand

Name = Annotated[str, StringConstraints(min_length=1, max_length=255)]


class CreateTenantCommand(BaseCommand):
    name: Name
    parent_tenant_id: int | None = Field(default=None, gt=0)


class UpdateTenantCommand(CreateTenantCommand):
    id: int
