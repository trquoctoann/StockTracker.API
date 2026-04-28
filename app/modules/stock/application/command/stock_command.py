from __future__ import annotations

from typing import Annotated

from pydantic import Field, StringConstraints

from app.common.base_schema import BaseCommand
from app.common.enum import StockExchange, StockType

Symbol = Annotated[str, StringConstraints(min_length=1, max_length=20)]
Name = Annotated[str, StringConstraints(min_length=1, max_length=500)]
ShortName = Annotated[str, StringConstraints(max_length=255)]


class CreateStockCommand(BaseCommand):
    symbol: Symbol
    name: Name
    short_name: ShortName | None = Field(default=None)
    exchange: StockExchange
    type: StockType
    industry_ids: set[int] | None = Field(default=None)


class UpdateStockCommand(CreateStockCommand):
    id: int
