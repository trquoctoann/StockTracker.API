from datetime import date
from typing import Annotated

from pydantic import Field, StringConstraints

from app.common.base_schema import BaseCommand

Title = Annotated[str, StringConstraints(min_length=1, max_length=500)]


class CreateCompanyEventCommand(BaseCommand):
    title: Title
    public_date: date | None = Field(default=None)
    issue_date: date | None = Field(default=None)
    source_url: str | None = Field(default=None, max_length=500)
    record_date: date | None = Field(default=None)
    exright_date: date | None = Field(default=None)
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int | None = Field(default=None)
