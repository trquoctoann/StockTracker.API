from __future__ import annotations

from app.modules.user.domain.user_entity import UserEntity


class AccountQueryService:
    async def get_me(self, current_user: UserEntity) -> UserEntity:
        return current_user
