from datetime import date

from app.common.base_schema import BaseResponse


class ResponseCompanyNews(BaseResponse):
    id: int
    title: str
    image_url: str | None
    source_url: str | None
    public_date: date | None
    language: str | None
    price_change_percent: float | None
    stock_id: int
