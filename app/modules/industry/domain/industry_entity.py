from datetime import datetime

from pydantic import BaseModel

from app.common.enum import RecordStatus


class IndustryEntity(BaseModel):
    id: int | None = None
    code: str
    name: str
    level: int
    record_status: RecordStatus
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
