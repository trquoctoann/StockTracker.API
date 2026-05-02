from datetime import date

from app.common.base_schema import BaseResponse


class ResponseCompanyShareholder(BaseResponse):
    id: int
    name: str
    quantity: int | None
    ownership_percent: float | None
    updated_date: date | None
    stock_id: int
