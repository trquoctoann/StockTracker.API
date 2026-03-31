from abc import ABC, abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.role.domain.role_entity import RoleEntity, RolePermissionEntity


class RoleRepository(RepositoryPort[RoleEntity]):
    pass


class RolePermissionRepository(ABC):
    @abstractmethod
    async def delete_by_role_id(self, role_id: int) -> None:
        pass

    @abstractmethod
    async def create_many_for_role(self, *, role_id: int, permission_ids: set[int]) -> None:
        pass

    @abstractmethod
    async def find_all_by_role_ids(self, role_ids: list[int]) -> list[RolePermissionEntity]:
        pass
