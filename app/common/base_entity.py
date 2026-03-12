import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class AbstractAuditableEntity(SQLModel, table=False):
    created_at: datetime = Field(default=datetime.now(UTC), nullable=False)
    created_by: str = Field(max_length=255, nullable=False)
    updated_at: datetime = Field(
        default=datetime.now(UTC),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )
    updated_by: str = Field(max_length=255, nullable=False)


class BaseEntityWithUUID(AbstractAuditableEntity, table=False):
    id: uuid.UUID = Field(default=uuid.uuid4, primary_key=True)


class BaseEntityWithID(AbstractAuditableEntity, table=False):
    id: int | None = Field(default=None, primary_key=True)
