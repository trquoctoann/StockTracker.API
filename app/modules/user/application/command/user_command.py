import uuid
from typing import Annotated

from pydantic import EmailStr, Field, StringConstraints, field_validator

from app.common.base_schema import BaseCommand
from app.exception.exception import ValidationException

Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class CreateUserCommand(BaseCommand):
    username: str = Field(min_length=1, max_length=255)
    password: Password
    email: EmailStr = Field(min_length=1, max_length=255)
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str | None = Field(max_length=255)

    @field_validator("password")
    @classmethod
    def _validate_password_strength(cls, v: str) -> str:
        if not (any(c.isupper() for c in v) and any(c.isdigit() for c in v) and any(not c.isalnum() for c in v)):
            raise ValidationException(message_key="errors.business.user.password_strength")
        return v


class UpdateUserCommand(CreateUserCommand):
    id: uuid.UUID


class UpdatePasswordCommand(BaseCommand):
    id: uuid.UUID
    current_password: Password
    new_password: Password

    @field_validator("new_password")
    @classmethod
    def _validate_password_strength(cls, v: str) -> str:
        if not (any(c.isupper() for c in v) and any(c.isdigit() for c in v) and any(not c.isalnum() for c in v)):
            raise ValidationException(message_key="errors.business.user.password_strength")
        return v


class SetUserRolesCommand(BaseCommand):
    id: uuid.UUID
    tenant_id: int | None = Field(default=None, gt=0)
    role_ids: set[int] = Field(default_factory=set)
