import uuid
from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.common.base_schema import FilterQueryParameter, PaginatedResponse, PaginationQueryParameter


class QueryService[T: BaseModel, TFilterKey: str](ABC):
    @abstractmethod
    async def find_by_id(self, id: uuid.UUID | int) -> list[T]:
        pass

    @abstractmethod
    async def find_all(self, filter_params: FilterQueryParameter[TFilterKey]) -> list[T]:
        pass

    @abstractmethod
    async def find_page(
        self, filter_params: FilterQueryParameter[TFilterKey], pagination_params: PaginationQueryParameter
    ) -> PaginatedResponse[T]:
        pass

    @abstractmethod
    async def count(self, filter_params: FilterQueryParameter[TFilterKey]) -> int:
        pass

    @abstractmethod
    async def exists(self, filter_params: FilterQueryParameter[TFilterKey]) -> bool:
        pass


class CRUDService[T: BaseModel](ABC):
    @abstractmethod
    async def create(self, data: T) -> T:
        pass

    @abstractmethod
    async def update(self, data: T) -> T:
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID | int) -> None:
        pass
