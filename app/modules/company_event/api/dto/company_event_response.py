from datetime import date

from app.common.base_schema import BaseResponse


class ResponseCompanyEvent(BaseResponse):
    id: int
    title: str
    public_date: date | None
    issue_date: date | None
    source_url: str | None
    record_date: date | None
    exright_date: date | None
    stock_id: int
