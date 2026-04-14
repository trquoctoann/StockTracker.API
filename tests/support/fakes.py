from __future__ import annotations

import uuid

from app.common.cache import CacheService
from app.common.enum import RoleScope
from app.modules.user.domain.identity_provider import (
    IdentityCreateUserPayload,
    IdentityProvider,
    IdentityUpdatePasswordPayload,
    IdentityUpdateProfilePayload,
)
from app.modules.user.domain.user_entity import UserRoleEntity
from app.modules.user.domain.user_repository import UserRoleRepository


class FakeIdentityProvider(IdentityProvider):
    def __init__(self, *, fixed_user_id: str | None = None) -> None:
        self._fixed_user_id = fixed_user_id

    async def create_user(self, payload: IdentityCreateUserPayload) -> str:
        return self._fixed_user_id or str(uuid.uuid4())

    async def update_profile(self, payload: IdentityUpdateProfilePayload) -> None:
        pass

    async def update_password(self, payload: IdentityUpdatePasswordPayload) -> None:
        pass

    async def delete_user(self, identity_user_id: str) -> None:
        pass


class FakeUserRoleRepository(UserRoleRepository):
    def __init__(self) -> None:
        self._data: list[UserRoleEntity] = []

    async def find_all_by_user_ids(self, user_ids: list[uuid.UUID]) -> list[UserRoleEntity]:
        return [ur for ur in self._data if ur.user_id in user_ids]

    async def delete_by_user_id(self, *, user_id: uuid.UUID, scope: RoleScope, tenant_id: int | None) -> None:
        self._data = [
            ur for ur in self._data if not (ur.user_id == user_id and ur.scope == scope and ur.tenant_id == tenant_id)
        ]

    async def upsert_user_roles(
        self, *, user_id: uuid.UUID, scope: RoleScope, tenant_id: int | None, role_ids: set[int]
    ) -> UserRoleEntity:
        await self.delete_by_user_id(user_id=user_id, scope=scope, tenant_id=tenant_id)
        entity = UserRoleEntity(
            id=len(self._data) + 1,
            scope=scope,
            user_id=user_id,
            tenant_id=tenant_id,
            role_ids=list(role_ids),
            version=1,
        )
        self._data.append(entity)
        return entity

    async def delete_all_by_tenant_id(self, tenant_id: int) -> list[tuple[uuid.UUID, RoleScope, int | None]]:
        removed = [(ur.user_id, ur.scope, ur.tenant_id) for ur in self._data if ur.tenant_id == tenant_id]
        self._data = [ur for ur in self._data if ur.tenant_id != tenant_id]
        return removed

    async def remove_role_id_from_all_assignments(self, role_id: int) -> list[tuple[uuid.UUID, RoleScope, int | None]]:
        affected: list[tuple[uuid.UUID, RoleScope, int | None]] = []
        for ur in self._data:
            if role_id in ur.role_ids:
                ur.role_ids = [rid for rid in ur.role_ids if rid != role_id]
                affected.append((ur.user_id, ur.scope, ur.tenant_id))
        return affected


class FakeCacheService(CacheService):
    def __init__(self) -> None:
        super().__init__(client=None)
        self._store: dict[str, str] = {}

    def _use_redis(self) -> bool:
        return True

    def _key(self, key: str, is_service_level_cache: bool) -> str:
        return f"test:{key}"

    async def get(self, key: str, *, is_service_level_cache: bool = False) -> str | None:
        return self._store.get(self._key(key, is_service_level_cache))

    async def get_many(self, *keys: str, is_service_level_cache: bool = False) -> list[str | None]:
        return [self._store.get(self._key(k, is_service_level_cache)) for k in keys]

    async def set(self, key: str, value: str, *, ttl: int | None = None, is_service_level_cache: bool = False) -> None:
        self._store[self._key(key, is_service_level_cache)] = value

    async def set_many(
        self, mapping: dict[str, str], *, ttl: int | None = None, is_service_level_cache: bool = False
    ) -> None:
        for k, v in mapping.items():
            self._store[self._key(k, is_service_level_cache)] = v

    async def delete(self, *keys: str, is_service_level_cache: bool = False) -> None:
        for k in keys:
            self._store.pop(self._key(k, is_service_level_cache), None)


def make_mock_async_session():
    from unittest.mock import AsyncMock, MagicMock

    s = AsyncMock()
    s.in_transaction = MagicMock(return_value=False)

    async def _begin() -> MagicMock:
        tx = MagicMock()
        tx.commit = AsyncMock()
        tx.rollback = AsyncMock()
        return tx

    s.begin = MagicMock(side_effect=_begin)
    s.begin_nested = MagicMock(side_effect=_begin)
    return s
