from app.common.base_schema import BaseResponse


class ResponseCompanyAffiliation(BaseResponse):
    id: int
    code: str | None
    name: str
    type: str | None
    ownership_percent: float | None
    stock_id: int
