from typing import ClassVar

from sqlmodel import Field, Index

from app.common.base_model import BaseSQLModelWithID
from app.common.enum import RecordStatus


class TenantModel(BaseSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "tenant"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, max_length=255)
    path: str = Field(nullable=False, max_length=255)
    record_status: RecordStatus = Field(default=RecordStatus.ENABLED, nullable=False)
    parent_tenant_id: int | None = Field(foreign_key="tenant.id")

    _table_args__ = (Index("ix_tenant_parent_tenant_id", "parent_tenant_id"),)
