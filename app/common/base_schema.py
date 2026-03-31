from __future__ import annotations

import uuid
from collections import defaultdict
from collections.abc import Callable
from enum import Enum as PyEnum
from enum import StrEnum
from typing import Any, ClassVar, Self

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import and_
from sqlalchemy.orm import aliased
from sqlmodel import SQLModel, desc

from app.exception.exception import InternalException, ValidationException


class BaseCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class BaseResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class PaginatedResponse[T](BaseResponse):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginationQueryParameter(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    limit: int = Field(default=10, gt=0, le=100)
    offset: int = Field(default=0, ge=0)
    order_by: str | None = Field(default=None)

    orderable_fields: ClassVar[frozenset[str] | None] = None

    def build_order_by_clauses(self, model: type[SQLModel]) -> list[Any]:
        if self.order_by is None or not self.order_by.strip():
            return []
        clauses: list[Any] = []
        for field, is_desc in self._parse_order_entries(self.order_by):
            col = getattr(model, field)
            clauses.append(desc(col) if is_desc else col)
        return clauses

    @staticmethod
    def _field_name_from_order_token(token: str) -> str:
        token = token.strip()
        if token.startswith("-"):
            return token[1:].strip()
        if token.startswith("+"):
            return token[1:].strip()
        return token

    @classmethod
    def _parse_order_entries(cls, order_by: str) -> list[tuple[str, bool]]:
        out: list[tuple[str, bool]] = []
        for segment in order_by.split(","):
            token = segment.strip()
            if not token:
                continue
            is_desc = token.startswith("-")
            field = cls._field_name_from_order_token(token)
            out.append((field, is_desc))
        return out

    @model_validator(mode="after")
    def _validate_order_by_fields(self) -> Self:
        if self.order_by is None:
            return self
        if not self.order_by.strip():
            return self
        entries = self._parse_order_entries(self.order_by)
        if not entries:
            return self
        allowed = self.__class__.orderable_fields
        if allowed is None:
            raise InternalException(
                developer_message=f"{self.__class__.__name__} must assign orderable_fields when order_by is used",
            )
        for field, _desc in entries:
            if not field:
                raise ValidationException(message_key="errors.query.order_by_empty_field_name")
            if field not in allowed:
                raise ValidationException(
                    message_key="errors.query.order_by_field_not_allowed",
                    params={"field": field, "allowed": ", ".join(sorted(allowed))},
                )
        return self


class FilterQueryParameter(BaseModel):
    class RelatedFilterSpec:
        def __init__(
            self,
            model: type[SQLModel],
            fk_on_root: str,
            fk_on_related: str,
        ):
            self.model = model
            self.fk_on_root = fk_on_root
            self.fk_on_related = fk_on_related

    class JoinType(StrEnum):
        INNER = "inner"
        LEFT = "left"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    filterable_fields: ClassVar[set[str]] = set()
    related_filter_specs: ClassVar[dict[str, RelatedFilterSpec]] = {}

    eq: dict[str, Any] = Field(default_factory=dict)
    neq: dict[str, Any] = Field(default_factory=dict)
    gt: dict[str, Any] = Field(default_factory=dict)
    gte: dict[str, Any] = Field(default_factory=dict)
    lt: dict[str, Any] = Field(default_factory=dict)
    lte: dict[str, Any] = Field(default_factory=dict)
    contains: dict[str, str] = Field(default_factory=dict)
    startswith: dict[str, str] = Field(default_factory=dict)
    endswith: dict[str, str] = Field(default_factory=dict)
    in_: dict[str, list[Any]] = Field(default_factory=dict, alias="in")
    nin: dict[str, list[Any]] = Field(default_factory=dict)
    null: dict[str, bool] = Field(default_factory=dict)

    @classmethod
    def merge_ops(
        cls,
        filter_params: Self | None,
        **extra_ops: dict[str, Any],
    ) -> Self:
        raw: dict[str, Any] = filter_params.model_dump(exclude_none=True) if filter_params else {}

        for op_name, extra_mapping in extra_ops.items():
            if not extra_mapping:
                continue
            existing: dict[str, Any] = raw.get(op_name) or {}
            merged = {**existing, **extra_mapping}
            raw[op_name] = merged

        return cls(**raw)

    @staticmethod
    def _coerce_single_value_for_column(col: Any, value: Any) -> Any:
        if value is None:
            return None

        col_type = getattr(col, "type", None)
        if col_type is None:
            return value
        try:
            python_type = col_type.python_type
        except NotImplementedError:
            return value
        if not isinstance(python_type, type):
            return value

        if issubclass(python_type, int) and isinstance(value, str):
            v = value.strip()
            if v.lstrip("-").isdigit():
                return int(v)

        if (python_type is uuid.UUID or issubclass(python_type, uuid.UUID)) and isinstance(value, str):
            return uuid.UUID(value.strip())

        if issubclass(python_type, PyEnum) and isinstance(value, str):
            return python_type(value)
        return value

    @classmethod
    def _coerce_filter_value_for_column(cls, col: Any, op: str, value: Any) -> Any:
        if op in {"eq", "neq"}:
            return cls._coerce_single_value_for_column(col, value)
        if op in {"in", "nin"} and isinstance(value, list):
            return [cls._coerce_single_value_for_column(col, v) for v in value]
        return value

    @model_validator(mode="before")
    @classmethod
    def _merge_flat(cls, data: Any):
        if not isinstance(data, dict):
            return data

        result = dict(data)

        mapping = {
            "eq": "eq",
            "neq": "neq",
            "gt": "gt",
            "gte": "gte",
            "lt": "lt",
            "lte": "lte",
            "contains": "contains",
            "startswith": "startswith",
            "endswith": "endswith",
            "in": "in_",
            "nin": "nin",
            "null": "null",
        }

        to_remove = []

        for key, value in list(result.items()):
            if "." not in key:
                continue

            field, op = key.rsplit(".", 1)
            if op not in mapping:
                continue

            target = mapping[op]
            bucket = result.setdefault(target, {})

            if not isinstance(bucket, dict):
                bucket = {}
                result[target] = bucket

            if field in bucket:
                raise ValidationException(
                    message_key="errors.filter.conflicting_filter_definitions", params={"field": field, "operator": op}
                )
            if isinstance(value, list) and op not in {"in", "nin"}:
                raise ValidationException(
                    message_key="errors.filter.multiple_values_not_supported",
                    params={"field": field, "operator": op},
                )
            if op in {"in", "nin"}:
                value = cls._coerce_to_list(value)

            bucket[field] = value
            to_remove.append(key)

        for k in to_remove:
            result.pop(k, None)
        return result

    @model_validator(mode="after")
    def _validate(self):
        allowed = self.__class__.filterable_fields
        if not allowed:
            raise InternalException(
                developer_message=f"{allowed} must assign filterable_fields when filter_keys are used",
            )
        for op_name, mapping in self._iter_ops():
            for key in mapping:
                if key not in allowed:
                    raise ValidationException(
                        message_key="errors.query.field_not_allowed",
                        params={"field": key, "operator": op_name, "allowed": ", ".join(sorted(allowed))},
                    )

                alias, field = self._split(key)

                if alias:
                    spec = self.related_filter_specs.get(alias)
                    if not spec:
                        raise ValidationException(
                            message_key="errors.query.unknown_relation_alias", params={"alias": alias}
                        )

                    if not hasattr(spec.model, field):
                        raise ValidationException(
                            message_key="errors.query.related_field_invalid",
                            params={"field": field, "model_name": spec.model.__name__, "filter_key": key},
                        )

        return self

    @staticmethod
    def _split(key: str) -> tuple[str | None, str]:
        if "." not in key:
            return None, key
        alias, field = key.split(".", 1)
        return alias, field

    @classmethod
    def _coerce_to_list(cls, value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("(") and value.endswith(")"):
                value = value[1:-1]
            if "," in value:
                return [v.strip() for v in value.split(",") if v.strip()]
            return [value]
        return [value]

    def _iter_ops(self):
        return [
            ("eq", self.eq),
            ("neq", self.neq),
            ("gt", self.gt),
            ("gte", self.gte),
            ("lt", self.lt),
            ("lte", self.lte),
            ("contains", self.contains),
            ("startswith", self.startswith),
            ("endswith", self.endswith),
            ("in", self.in_),
            ("nin", self.nin),
            ("null", self.null),
        ]

    def _build_predicate(self, col, op: str, value):
        if op == "eq":
            return col == value
        if op == "neq":
            return col != value
        if op == "gt":
            return col > value
        if op == "gte":
            return col >= value
        if op == "lt":
            return col < value
        if op == "lte":
            return col <= value
        if op == "contains":
            return col.ilike(f"%{value}%")
        if op == "startswith":
            return col.ilike(f"{value}%")
        if op == "endswith":
            return col.ilike(f"%{value}")
        if op == "in":
            return col.in_(value)
        if op == "nin":
            return ~col.in_(value)
        if op == "null":
            return col.is_(None) if value else col.is_not(None)

        raise ValidationException(
            message_key="errors.query.field_not_allowed",
            params={"field": col, "operator": op, "allowed": ", ".join(sorted(self.__class__.filterable_fields))},
        )

    def _decide_join_type(self, op: str, value: Any) -> JoinType:
        if op in {"neq", "nin"}:
            return self.__class__.JoinType.LEFT
        if op == "null":
            return self.__class__.JoinType.LEFT if value is True else self.__class__.JoinType.INNER
        return self.__class__.JoinType.INNER

    def _rewrite_left_join_predicate(self, col, op: str, value):
        if op == "neq":
            return (col != value) | col.is_(None)
        if op == "nin":
            return (~col.in_(value)) | col.is_(None)
        if op == "null":
            if value:
                return col.is_(None)
            else:
                return col.is_not(None)
        return self._build_predicate(col, op, value)

    def build_conditions(self, root_model: type[SQLModel]):
        joins = {}
        join_types = {}
        conditions = []
        relation_predicates = {}

        for op, mapping in self._iter_ops():
            for key, value in mapping.items():
                alias, field = self._split(key)

                if alias is None:
                    col = getattr(root_model, field)
                    value = self._coerce_filter_value_for_column(col, op, value)
                    conditions.append(self._build_predicate(col, op, value))
                    continue

                spec = self.related_filter_specs[alias]

                if alias not in joins:
                    alias_model = aliased(spec.model)
                    joins[alias] = alias_model
                    join_types[alias] = self._decide_join_type(op, value)
                else:
                    alias_model = joins[alias]
                    jt = self._decide_join_type(op, value)
                    if jt == self.__class__.JoinType.LEFT:
                        join_types[alias] = self.__class__.JoinType.LEFT

                col = getattr(alias_model, field)
                value = self._coerce_filter_value_for_column(col, op, value)

                if join_types[alias] == self.__class__.JoinType.LEFT:
                    pred = self._rewrite_left_join_predicate(col, op, value)
                else:
                    pred = self._build_predicate(col, op, value)

                relation_predicates.setdefault(alias, []).append(pred)

        join_clauses = []
        for alias, preds in relation_predicates.items():
            spec = self.related_filter_specs[alias]
            alias_model = joins[alias]

            on_clause = getattr(root_model, spec.fk_on_root) == getattr(alias_model, spec.fk_on_related)
            join_clauses.append((alias, alias_model, on_clause, join_types[alias]))

            conditions.append(and_(*preds))
        return join_clauses, conditions


def _normalize_query_params(request: Request) -> dict[str, Any]:
    result: dict[str, list[Any]] = defaultdict(list)
    for k, v in request.query_params.multi_items():
        result[k].append(v)
    return {k: v if len(v) > 1 else v[0] for k, v in result.items()}


def build_query_param_dependency(
    model_cls: type[BaseModel], *, include_fields: set[str] | None = None, exclude_fields: set[str] | None = None
) -> Callable[[Request], BaseModel]:
    def dependency(request: Request) -> BaseModel:
        raw = _normalize_query_params(request)
        if include_fields is not None:
            data = {k: v for k, v in raw.items() if k in include_fields}
        elif exclude_fields is not None:
            data = {k: v for k, v in raw.items() if k not in exclude_fields}
        else:
            data = raw
        return model_cls.model_validate(data)

    return dependency


def get_model_fields(model_cls: type[BaseModel]) -> set[str]:
    return set(model_cls.model_fields.keys())
