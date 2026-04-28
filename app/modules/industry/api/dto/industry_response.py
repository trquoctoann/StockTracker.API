from datetime import datetime

from app.common.base_schema import BaseResponse
from app.common.enum import RecordStatus


class ResponseIndustry(BaseResponse):
    id: int
    code: str
    name: str
    level: int
    record_status: RecordStatus
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
