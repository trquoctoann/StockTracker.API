from sqlmodel import Field

from app.common.base_entity import BaseEntityWithUUID


class User(BaseEntityWithUUID, table=True):
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    full_name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
