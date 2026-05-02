from pydantic import BaseModel


class CompanyAffiliationEntity(BaseModel):
    id: int | None = None
    code: str | None = None
    name: str
    type: str | None = None
    ownership_percent: float | None = None
    data_source_id: str | None = None
    stock_id: int
