import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _auditor_user_id(*_args: object, **_kwargs: object) -> str:
    from app.common.current_user import get_current_user_id

    return get_current_user_id()


class AbstractAuditableSQLModel(SQLModel, table=False):
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    created_by: str = Field(default_factory=_auditor_user_id, max_length=255, nullable=False)
    updated_at: datetime = Field(
        default_factory=_utc_now,
        nullable=False,
        sa_column_kwargs={"onupdate": _utc_now},
    )
    updated_by: str = Field(
        default_factory=_auditor_user_id,
        max_length=255,
        nullable=False,
        sa_column_kwargs={"onupdate": _auditor_user_id},
    )


class BaseSQLModelWithUUID(AbstractAuditableSQLModel, table=False):
    id: uuid.UUID = Field(default=uuid.uuid4, primary_key=True)


class BaseSQLModelWithID(AbstractAuditableSQLModel, table=False):
    id: int | None = Field(default=None, primary_key=True)


class BaseNonAuditableSQLModelWithID(SQLModel, table=False):
    id: int | None = Field(default=None, primary_key=True)
