from abc import abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.company_officer.domain.company_officer_entity import CompanyOfficerEntity


class CompanyOfficerRepository(RepositoryPort[CompanyOfficerEntity]):
    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass
