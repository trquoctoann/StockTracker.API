import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class AbstractAuditableSQLModel(SQLModel, table=False):
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    created_by: str = Field(default="", max_length=255, nullable=False)
    updated_at: datetime = Field(
        default_factory=_utc_now,
        nullable=False,
        sa_column_kwargs={"onupdate": _utc_now},
    )
    updated_by: str = Field(default="", max_length=255, nullable=False)


class BaseSQLModelWithUUID(AbstractAuditableSQLModel, table=False):
    id: uuid.UUID = Field(default=uuid.uuid4, primary_key=True)


class BaseSQLModelWithID(AbstractAuditableSQLModel, table=False):
    id: int | None = Field(default=None, primary_key=True)
