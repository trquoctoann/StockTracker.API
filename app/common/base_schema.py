from __future__ import annotations

from enum import StrEnum
from typing import Any, ClassVar, Self

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator
from sqlmodel import SQLModel, desc, exists, select

from app.exception.exception import InternalException, ValidationException


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginationQueryParameter(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: str | None = None

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


class FilterQueryParameter[TFilterKey: str](BaseModel):
    class RelatedFilterSpec:
        model: type[SQLModel]
        fk_on_root: str
        pk_on_related: str = "id"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    filterable_fields: ClassVar[frozenset[str] | None] = None

    related_filter_specs: ClassVar[dict[str, RelatedFilterSpec] | None] = None

    eq: dict[TFilterKey, Any] = Field(default_factory=dict)
    neq: dict[TFilterKey, Any] = Field(default_factory=dict)
    gt: dict[TFilterKey, Any] = Field(default_factory=dict)
    gte: dict[TFilterKey, Any] = Field(default_factory=dict)
    lt: dict[TFilterKey, Any] = Field(default_factory=dict)
    lte: dict[TFilterKey, Any] = Field(default_factory=dict)
    contains: dict[TFilterKey, str] = Field(default_factory=dict)
    startswith: dict[TFilterKey, str] = Field(default_factory=dict)
    endswith: dict[TFilterKey, str] = Field(default_factory=dict)
    in_: dict[TFilterKey, list[Any]] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("in"),
        serialization_alias="in",
    )
    nin: dict[TFilterKey, list[Any]] = Field(default_factory=dict)
    null: dict[TFilterKey, bool] = Field(default_factory=dict)

    @staticmethod
    def _split_field_key(key: str) -> tuple[str | None, str]:
        if "." not in key:
            return None, key
        alias, rest = key.split(".", 1)
        if "." in rest:
            raise ValidationException(
                message_key="errors.filter.relation_depth_exceeded",
                params={"key": key},
            )
        return alias, rest

    @classmethod
    def _resolve_related_spec(cls, alias: str) -> RelatedFilterSpec:
        specs = cls.related_filter_specs
        if not specs or alias not in specs:
            raise ValidationException(
                message_key="errors.filter.unknown_relation_alias",
                params={"alias": alias},
            )
        return specs[alias]

    @staticmethod
    def _filter_key_str(key: str | StrEnum) -> str:
        return key.value if isinstance(key, StrEnum) else key

    @model_validator(mode="after")
    def _validate_filter_keys(self) -> Self:
        allowed = self.__class__.filterable_fields
        if allowed is None:
            raise ValidationException(
                message_key="errors.filter.filterable_fields_required",
                params={"class_name": self.__class__.__name__},
            )
        operator_maps: list[tuple[str, Any]] = [
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
        for op_name, m in operator_maps:
            for key in m:
                key_s = self._filter_key_str(key)
                if key_s not in allowed:
                    raise ValidationException(
                        message_key="errors.filter.field_not_allowed",
                        params={
                            "field": key_s,
                            "operator": op_name,
                            "allowed": ", ".join(sorted(allowed)),
                        },
                    )
                alias, field = self._split_field_key(key_s)
                if alias is None:
                    continue
                spec = self.__class__._resolve_related_spec(alias)
                if not hasattr(spec.model, field):
                    raise ValidationException(
                        message_key="errors.filter.related_field_invalid",
                        params={
                            "field": field,
                            "model_name": spec.model.__name__,
                            "filter_key": key_s,
                        },
                    )
        return self

    def _fk_correlation(self, root_model: type[SQLModel], spec: RelatedFilterSpec) -> Any:
        return getattr(root_model, spec.fk_on_root) == getattr(spec.model, spec.pk_on_related)

    def _related_exists(
        self,
        root_model: type[SQLModel],
        alias: str,
        *predicates: Any,
    ) -> Any:
        spec = self._resolve_related_spec(alias)
        base = self._fk_correlation(root_model, spec)
        return exists(
            select(1).select_from(spec.model).where(base, *predicates),
        )

    def _column(self, root_model: type[SQLModel], key: str) -> Any:
        alias, name = self._split_field_key(key)
        if alias is None:
            return getattr(root_model, name)
        spec = self._resolve_related_spec(alias)
        return getattr(spec.model, name)

    def build_conditions(self, model: type[SQLModel]) -> list[Any]:
        conditions: list[Any] = []

        for field, value in self.eq.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field) == value)
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col == value))

        for field, value in self.neq.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field) != value)
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col != value))

        for field, value in self.gt.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field) > value)
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col > value))

        for field, value in self.gte.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field) >= value)
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col >= value))

        for field, value in self.lt.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field) < value)
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col < value))

        for field, value in self.lte.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field) <= value)
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col <= value))

        for field, value in self.contains.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field).ilike(f"%{value}%"))
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col.ilike(f"%{value}%")))

        for field, value in self.startswith.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field).ilike(f"{value}%"))
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col.ilike(f"{value}%")))

        for field, value in self.endswith.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field).ilike(f"%{value}"))
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col.ilike(f"%{value}")))

        for field, values in self.in_.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field).in_(values))
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col.in_(values)))

        for field, values in self.nin.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                conditions.append(self._column(model, field).not_in(values))
            else:
                col = self._column(model, field)
                conditions.append(self._related_exists(model, alias, col.not_in(values)))

        for field, null in self.null.items():
            field = self._filter_key_str(field)
            alias, _ = self._split_field_key(field)
            if alias is None:
                col = self._column(model, field)
                if null:
                    conditions.append(col.is_(None))
                else:
                    conditions.append(col.is_not(None))
            else:
                col = self._column(model, field)
                if null:
                    conditions.append(self._related_exists(model, alias, col.is_(None)))
                else:
                    conditions.append(self._related_exists(model, alias, col.is_not(None)))

        return conditions
