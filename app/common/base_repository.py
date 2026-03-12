import uuid
from typing import Any

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


class BaseRepository[ModelType: SQLModel]:
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_all(self, *, offset: int = 0, limit: int = 20) -> list[ModelType]:
        statement = select(self.model).offset(offset).limit(limit)
        results = await self.session.exec(statement)
        return list(results.all())

    async def count(self) -> int:
        statement = select(self.model)
        results = await self.session.exec(statement)
        return len(results.all())

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> None:
        await self.session.delete(db_obj)
        await self.session.flush()
