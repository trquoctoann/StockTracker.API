from datetime import date

from pydantic import BaseModel


class CompanyOfficerEntity(BaseModel):
    id: int | None = None
    name: str
    position: str | None = None
    ownership_percent: float | None = None
    quantity: int | None = None
    updated_date: date | None = None
    data_source_id: str | None = None
    stock_id: int
