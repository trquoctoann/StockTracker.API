from abc import abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.company_profile.domain.company_profile_entity import CompanyProfileEntity


class CompanyProfileRepository(RepositoryPort[CompanyProfileEntity]):
    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass
