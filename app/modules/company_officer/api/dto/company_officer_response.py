from datetime import date

from app.common.base_schema import BaseResponse


class ResponseCompanyOfficer(BaseResponse):
    id: int
    name: str
    position: str | None
    ownership_percent: float | None
    quantity: int | None
    updated_date: date | None
    stock_id: int
