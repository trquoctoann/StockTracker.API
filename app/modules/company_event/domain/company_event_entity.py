from datetime import date

from pydantic import BaseModel


class CompanyEventEntity(BaseModel):
    id: int | None = None
    title: str
    public_date: date | None = None
    issue_date: date | None = None
    source_url: str | None = None
    record_date: date | None = None
    exright_date: date | None = None
    data_source_id: str | None = None
    stock_id: int
