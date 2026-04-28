from __future__ import annotations

from typing import Annotated

from pydantic import Field, StringConstraints

from app.common.base_schema import BaseCommand

Symbol = Annotated[str, StringConstraints(min_length=1, max_length=50)]
Name = Annotated[str, StringConstraints(min_length=1, max_length=255)]
Description = Annotated[str, StringConstraints(max_length=500)]
Group = Annotated[str, StringConstraints(max_length=100)]


class CreateMarketIndexCommand(BaseCommand):
    symbol: Symbol
    name: Name
    description: Description | None = Field(default=None)
    group: Group | None = Field(default=None)
    stock_ids: set[int] | None = Field(default=None)


class UpdateMarketIndexCommand(CreateMarketIndexCommand):
    id: int
