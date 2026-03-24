from typing import Any

from pydantic import BaseModel
from sqlalchemy.exc import NoInspectionAvailable
from sqlmodel import SQLModel, inspect

from app.exception.exception import InternalException


class BaseMapper[M: SQLModel, E: BaseModel]:
    model_class: type[M]
    entity_class: type[E]

    def to_entity(self, model: M) -> E:
        data: dict[str, Any] = self._extract_columns(model)
        return self.entity_class.model_validate(data)

    def to_model(self, entity: E) -> M:
        data: dict[str, Any] = entity.model_dump()
        return self.model_class(**data)

    def to_entity_list(self, models: list[M]) -> list[E]:
        return [self.to_entity(model) for model in models]

    def to_model_list(self, entities: list[E]) -> list[M]:
        return [self.to_model(entity) for entity in entities]

    def _extract_columns(self, model: M) -> dict[str, Any]:
        try:
            mapper = inspect(type(model))
        except NoInspectionAvailable as err:
            raise InternalException(
                developer_message=f"{type(model)} is not a mapped SQLModel model",
            ) from err
        return {column.key: getattr(model, column.key) for column in mapper.column_attrs}
