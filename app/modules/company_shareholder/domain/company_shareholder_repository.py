from abc import abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.company_shareholder.domain.company_shareholder_entity import CompanyShareholderEntity


class CompanyShareholderRepository(RepositoryPort[CompanyShareholderEntity]):
    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass
