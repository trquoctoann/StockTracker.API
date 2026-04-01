import uuid
from abc import ABC, abstractmethod

from app.common.base_repository import RepositoryPort
from app.common.enum import RoleScope
from app.modules.user.domain.user_entity import UserEntity, UserRoleEntity


class UserRepository(RepositoryPort[UserEntity]):
    pass


class UserRoleRepository(ABC):
    @abstractmethod
    async def find_all_by_user_ids(self, user_ids: list[uuid.UUID]) -> list[UserRoleEntity]:
        pass

    @abstractmethod
    async def delete_by_user_id(self, *, user_id: uuid.UUID, scope: RoleScope, tenant_id: int | None) -> None:
        pass

    @abstractmethod
    async def upsert_user_roles(
        self, *, user_id: uuid.UUID, scope: RoleScope, tenant_id: int | None, role_ids: set[int]
    ) -> UserRoleEntity:
        pass
