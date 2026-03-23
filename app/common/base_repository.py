from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel import SQLModel, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter

S = TypeVar("S")
K = TypeVar("K")
V = TypeVar("V")
E = TypeVar("E")


class RepositoryPort[E](ABC):
    @abstractmethod
    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
    ) -> list[E]:
        pass

    @abstractmethod
    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[E], K],
        value_fn: Callable[[E], V] | None = None,
    ) -> dict[K, list[V | E]]:
        pass

    @abstractmethod
    async def count(self, *, filter_param: FilterQueryParameter | None = None) -> int:
        pass

    @abstractmethod
    async def exists(self, *, filter_param: FilterQueryParameter | None = None) -> bool:
        pass

    @abstractmethod
    async def bulk_create(self, entities: Sequence[E], *, id_attr: str = "id") -> list[E]:
        pass

    @abstractmethod
    async def bulk_update(self, entities: Sequence[E]) -> list[E]:
        pass

    @abstractmethod
    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        pass


class SQLModelRepository[M: SQLModel]:
    def __init__(self, model: type[M], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    def _apply_filter_query_parameter(
        self,
        statement: SelectOfScalar[S],
        filter_param: FilterQueryParameter | None,
    ) -> SelectOfScalar[S]:
        if filter_param is None:
            return statement
        conditions = filter_param.build_conditions(self.model)
        if not conditions:
            return statement
        return statement.where(*conditions)

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
    ) -> list[M]:
        statement = select(self.model)
        statement = self._apply_filter_query_parameter(statement, filter_param)
        if pagination_param is not None:
            statement = statement.limit(pagination_param.limit)
            statement = statement.offset(pagination_param.offset)
            statement = statement.order_by(*pagination_param.build_order_by_clauses(self.model))
        result = await self.session.exec(statement)
        return list(result.all())

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_field: str = "id") -> int:
        statement = select(func.count(getattr(self.model, id_field)))
        statement = self._apply_filter_query_parameter(statement, filter_param)
        result = await self.session.exec(statement)
        return result.first() or 0

    async def exists(self, *, filter_param: FilterQueryParameter | None = None) -> bool:
        statement = select(1)
        statement = self._apply_filter_query_parameter(statement, filter_param)
        result = await self.session.exec(statement)
        return result.first() is not None

    async def bulk_create(
        self,
        entities: Sequence[M],
        *,
        id_attr: str = "id",
    ) -> list[M]:
        if not entities:
            return []
        self.session.add_all(entities)
        await self.session.flush()

        pk_col = getattr(self.model, id_attr)
        ids = [getattr(e, id_attr) for e in entities]

        statement: SelectOfScalar[M] = select(self.model).where(pk_col.in_(ids))
        result = await self.session.exec(statement)

        by_pk = {getattr(r, id_attr): r for r in result.all()}
        return [by_pk[i] for i in ids if i in by_pk]

    async def bulk_update(self, entities: Sequence[M]) -> list[M]:
        self.session.add_all(entities)
        await self.session.flush()
        return list[M](entities)

    async def bulk_delete(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
    ) -> None:
        statement = select(self.model)
        statement = self._apply_filter_query_parameter(statement, filter_param)
        result = await self.session.exec(statement)

        for record in result.all():
            await self.session.delete(record)
