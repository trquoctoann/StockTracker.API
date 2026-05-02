from typing import Annotated

from pydantic import Field, StringConstraints

from app.common.base_schema import BaseCommand

Name = Annotated[str, StringConstraints(min_length=1, max_length=255)]


class CreateCompanyAffiliationCommand(BaseCommand):
    code: str | None = Field(default=None, max_length=50)
    name: Name
    type: str | None = Field(default=None, max_length=50)
    ownership_percent: float | None = Field(default=None)
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int | None = Field(default=None)
