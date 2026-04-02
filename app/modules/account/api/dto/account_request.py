from pydantic import Field

from app.common.base_schema import BaseCommand
from app.modules.user.application.command.user_command import Password


class AccountUpdateProfileRequest(BaseCommand):
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)


class AccountUpdatePasswordRequest(BaseCommand):
    new_password: Password
