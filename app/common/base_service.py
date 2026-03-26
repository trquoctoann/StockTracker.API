import uuid
from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from app.common.base_schema import FilterQueryParameter, PaginatedResponse, PaginationQueryParameter

TFetchSpec = TypeVar("TFetchSpec")


class QueryService[T: BaseModel, TFetchSpec](ABC):
    @abstractmethod
    async def find_by_id(self, id: uuid.UUID | int, *, fetch_spec: TFetchSpec | None = None) -> T | None:
        pass

    @abstractmethod
    async def find_all(self, filter_params: FilterQueryParameter, *, fetch_spec: TFetchSpec | None = None) -> list[T]:
        pass

    @abstractmethod
    async def find_page(
        self,
        filter_params: FilterQueryParameter,
        pagination_params: PaginationQueryParameter,
        *,
        fetch_spec: TFetchSpec | None = None,
    ) -> PaginatedResponse[T]:
        pass

    @abstractmethod
    async def count(self, filter_params: FilterQueryParameter) -> int:
        pass

    @abstractmethod
    async def exists(self, filter_params: FilterQueryParameter) -> bool:
        pass

    @abstractmethod
    async def _enrich_entities(self, entities: list[T], fetch_spec: TFetchSpec) -> list[T]:
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
