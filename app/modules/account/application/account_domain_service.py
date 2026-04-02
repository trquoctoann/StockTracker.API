from __future__ import annotations

from app.modules.user.application.user_domain_service import UserDomainService
from app.modules.user.domain.user_entity import UserEntity


class AccountDomainService:
    def __init__(self, user_domain_service: UserDomainService) -> None:
        self._user_domain_service = user_domain_service

    async def update_profile(
        self,
        current_user: UserEntity,
        *,
        first_name: str,
        last_name: str | None,
    ) -> UserEntity:
        return await self._user_domain_service.update_profile(
            current_user.id,
            first_name=first_name,
            last_name=last_name,
        )

    async def update_password(self, current_user: UserEntity, *, new_password: str) -> None:
        await self._user_domain_service.update_password(current_user.id, new_password=new_password)
