import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)


class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
