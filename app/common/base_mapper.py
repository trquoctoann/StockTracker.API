from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel
from sqlalchemy.exc import NoInspectionAvailable
from sqlmodel import SQLModel, inspect

from app.common.base_schema import BaseCommand
from app.exception.exception import InternalException


class BaseMapper[M: SQLModel, E: BaseModel]:
    model_class: type[M]
    entity_class: type[E]

    _column_keys_cache: ClassVar[dict[type[SQLModel], frozenset[str]]] = {}

    @classmethod
    def _column_keys(cls, model_cls: type[SQLModel]) -> frozenset[str]:
        if model_cls in cls._column_keys_cache:
            return cls._column_keys_cache[model_cls]

        try:
            mapper = inspect(model_cls)
        except NoInspectionAvailable as err:
            raise InternalException(
                developer_message=f"{model_cls} is not a mapped SQLModel class",
            ) from err

        keys = frozenset(attr.key for attr in mapper.column_attrs)
        cls._column_keys_cache[model_cls] = keys
        return keys

    def to_entity(self, model: M) -> E:
        keys = self._column_keys(type(model)) & frozenset(self.entity_class.model_fields)
        data = {k: getattr(model, k) for k in keys}
        return self.entity_class(**data)

    def to_model(self, entity: E) -> M:
        column_keys = self._column_keys(self.model_class)
        dumped = entity.model_dump(exclude_unset=True)
        kwargs = {k: dumped[k] for k in column_keys if k in dumped}
        return self.model_class(**kwargs)

    def to_entity_list(self, models: list[M]) -> list[E]:
        return [self.to_entity(model) for model in models]

    def to_model_list(self, entities: list[E]) -> list[M]:
        return [self.to_model(entity) for entity in entities]


class SchemaMapper[E: BaseModel, R: BaseModel]:
    @staticmethod
    def shared_field_names(a: type[BaseModel], b: type[BaseModel]) -> set[str]:
        def field_names(model: type[BaseModel]) -> set[str]:
            names: set[str] = set()
            for name, f in model.model_fields.items():
                names.add(f.alias or name)
            return names

        return field_names(a) & field_names(b)

    @classmethod
    def command_to_entity(
        cls,
        command: BaseCommand,
        entity_class: type[E],
        *,
        overrides: dict[str, Any] | None = None,
    ) -> E:
        cmd_data = command.model_dump(exclude_unset=True)
        payload: dict[str, Any] = {k: v for k, v in cmd_data.items() if k in entity_class.model_fields}

        if overrides:
            conflict_keys = payload.keys() & overrides.keys()
            if conflict_keys:
                raise InternalException(
                    developer_message=f"Override conflicts with command fields: {conflict_keys}",
                )
            payload.update(overrides)
        return entity_class.model_validate(payload)

    @classmethod
    def entity_to_response(cls, entity: BaseModel, response_class: type[R]) -> R:
        keys = cls.shared_field_names(type(entity), response_class)
        return response_class.model_validate(entity.model_dump(include=keys, by_alias=True))

    @classmethod
    def merge_source_into_target(
        cls,
        source: E,
        target: R,
        *,
        forbidden: frozenset[str] | None = None,
    ) -> R:
        forbidden = forbidden or frozenset[str]()

        patch = source.model_dump(exclude_unset=True)
        base = target.model_dump()
        for key, value in patch.items():
            if key in forbidden:
                continue
            if key not in base:
                continue

            if isinstance(value, dict) and isinstance(base.get(key), dict):
                base[key] = _deep_merge(base[key], value)
            else:
                base[key] = value
        return type(target).model_validate(base)


def _deep_merge(target: dict, patch: dict) -> dict:
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            target[k] = _deep_merge(target[k], v)
        else:
            target[k] = v
    return target
