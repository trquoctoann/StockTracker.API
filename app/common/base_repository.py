from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import delete
from sqlmodel import SQLModel, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter

S = TypeVar("S")
K = TypeVar("K")
V = TypeVar("V")


class RepositoryPort[E: BaseModel](ABC):
    @abstractmethod
    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
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
    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        pass

    @abstractmethod
    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        pass

    @abstractmethod
    async def bulk_create(self, entities: Sequence[E], *, id_attr: str = "id") -> list[E]:
        pass

    @abstractmethod
    async def bulk_update(self, entities: Sequence[E], *, id_attr: str = "id") -> list[E]:
        pass

    @abstractmethod
    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        pass


class SQLExecutor[M: SQLModel]:
    def __init__(self, model: type[M], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    def _apply_filter_query_parameter(
        self, statement: SelectOfScalar[S], filter_param: FilterQueryParameter | None, id_attr: str = "id"
    ) -> SelectOfScalar[S]:
        if filter_param is None:
            return statement
        joins, conditions = filter_param.build_conditions(self.model)
        for _, alias_model, on_clause, join_type in joins:
            if join_type == FilterQueryParameter.JoinType.LEFT:
                statement = statement.outerjoin(alias_model, on_clause)
            else:
                statement = statement.join(alias_model, on_clause)
        if not conditions:
            return statement
        statement = statement.where(*conditions)
        if not joins:
            return statement
        return statement.distinct(getattr(self.model, id_attr))

    async def execute(self, statement: SelectOfScalar[S]) -> list[S]:
        result = await self.session.exec(statement)
        return list(result.all())

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[M]:
        statement = select(self.model)
        statement = self._apply_filter_query_parameter(statement, filter_param, id_attr)
        if pagination_param is not None:
            statement = statement.limit(pagination_param.limit)
            statement = statement.offset(pagination_param.offset)
            statement = statement.order_by(*pagination_param.build_order_by_clauses(self.model))
        result = await self.session.exec(statement)
        return list(result.all())

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        statement = select(func.count(getattr(self.model, id_attr)))
        statement = self._apply_filter_query_parameter(statement, filter_param, id_attr)
        result = await self.session.exec(statement)
        return result.first() or 0

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        statement = select(1)
        statement = self._apply_filter_query_parameter(statement, filter_param, id_attr)
        result = await self.session.exec(statement)
        return result.first() is not None

    async def bulk_create(self, models: Sequence[M], *, id_attr: str = "id") -> list[M]:
        if not models:
            return []
        self.session.add_all(models)
        await self.session.flush()

        pk_col = getattr(self.model, id_attr)
        ids = [getattr(e, id_attr) for e in models]

        statement: SelectOfScalar[M] = select(self.model).where(pk_col.in_(ids))
        result = await self.session.exec(statement)

        by_pk = {getattr(r, id_attr): r for r in result.all()}
        return [by_pk[i] for i in ids if i in by_pk]

    async def bulk_update(self, models: Sequence[M], *, id_attr: str = "id") -> list[M]:
        pk_col = getattr(self.model, id_attr)
        ids = [getattr(model, id_attr) for model in models]

        statement = select(self.model).where(pk_col.in_(ids))
        query_result = await self.session.exec(statement)

        update_result = []
        db_models = {getattr(e, id_attr): e for e in query_result.all()}
        for model in models:
            db_obj = db_models.get(getattr(model, id_attr))
            if db_obj:
                for field in model.model_fields_set:
                    value = getattr(model, field)
                    setattr(db_obj, field, value)
                self.session.add(db_obj)
                update_result.append(db_obj)

        await self.session.flush()
        return update_result

    async def bulk_delete(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        id_attr: str = "id",
    ) -> None:
        if not filter_param:
            statement = delete(self.model)
            await self.session.exec(statement)
            return

        joins, conditions = filter_param.build_conditions(self.model)

        subquery = select(getattr(self.model, id_attr))
        for _, alias_model, on_clause in joins:
            subquery = subquery.join(alias_model, on_clause)
        if conditions:
            subquery = subquery.where(*conditions)

        statement = delete(self.model).where(getattr(self.model, id_attr).in_(subquery))
        await self.session.exec(statement)
