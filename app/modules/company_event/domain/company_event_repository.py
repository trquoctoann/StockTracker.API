from abc import abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.company_event.domain.company_event_entity import CompanyEventEntity


class CompanyEventRepository(RepositoryPort[CompanyEventEntity]):
    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass
