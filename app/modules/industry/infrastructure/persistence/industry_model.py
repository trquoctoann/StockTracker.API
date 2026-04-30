from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.common.base_model import BaseSQLModelWithID
from app.common.enum import RecordStatus


class IndustryModel(BaseSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "industry"

    code: str = Field(nullable=False, max_length=20)
    name: str = Field(nullable=False, max_length=255)
    level: int = Field(nullable=False, default=0)
    record_status: RecordStatus = Field(default=RecordStatus.ENABLED, nullable=False)

    __table_args__ = (UniqueConstraint("code", name="uix_industry_code"),)
