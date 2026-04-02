from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, EmailStr


class IdentityCreateUserPayload(BaseModel):
    username: str
    password: str
    email: EmailStr
    first_name: str
    last_name: str | None = None


class IdentityUpdateProfilePayload(BaseModel):
    identity_user_id: str
    first_name: str
    last_name: str | None = None


class IdentityUpdatePasswordPayload(BaseModel):
    identity_user_id: str
    new_password: str
    temporary: bool


class IdentityProvider(ABC):
    @abstractmethod
    async def create_user(self, payload: IdentityCreateUserPayload) -> str:
        pass

    @abstractmethod
    async def update_profile(self, payload: IdentityUpdateProfilePayload) -> None:
        pass

    @abstractmethod
    async def update_password(self, payload: IdentityUpdatePasswordPayload) -> None:
        pass

    @abstractmethod
    async def delete_user(self, identity_user_id: str) -> None:
        pass
