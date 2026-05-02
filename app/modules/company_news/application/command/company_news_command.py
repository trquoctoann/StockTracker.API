from datetime import date
from typing import Annotated

from pydantic import Field, StringConstraints

from app.common.base_schema import BaseCommand

Title = Annotated[str, StringConstraints(min_length=1, max_length=500)]


class CreateCompanyNewsCommand(BaseCommand):
    title: Title
    image_url: str | None = Field(default=None, max_length=500)
    source_url: str | None = Field(default=None, max_length=500)
    public_date: date | None = Field(default=None)
    language: str | None = Field(default=None, max_length=50)
    price_change_percent: float | None = Field(default=None)
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int | None = Field(default=None)
