from abc import abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.company_affiliation.domain.company_affiliation_entity import CompanyAffiliationEntity


class CompanyAffiliationRepository(RepositoryPort[CompanyAffiliationEntity]):
    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass
