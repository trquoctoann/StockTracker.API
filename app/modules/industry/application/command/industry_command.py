from typing import Annotated

from pydantic import Field, StringConstraints

from app.common.base_schema import BaseCommand

Code = Annotated[str, StringConstraints(min_length=1, max_length=20)]
Name = Annotated[str, StringConstraints(min_length=1, max_length=255)]


class CreateIndustryCommand(BaseCommand):
    code: Code
    name: Name
    level: int = Field(default=0, ge=0)


class UpdateIndustryCommand(CreateIndustryCommand):
    id: int
