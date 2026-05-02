from abc import abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.company_news.domain.company_news_entity import CompanyNewsEntity


class CompanyNewsRepository(RepositoryPort[CompanyNewsEntity]):
    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass
