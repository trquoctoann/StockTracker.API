import pytest
from pydantic import ValidationError

from app.common.base_schema import PaginatedResponse, PaginationQueryParameter, get_model_fields
from app.exception.exception import InternalException, ValidationException


class ConcretePagination(PaginationQueryParameter):
    orderable_fields = frozenset({"name", "created_at"})


class TestPaginationQueryParameter:
    def test_defaults(self):
        p = ConcretePagination()
        assert p.limit == 10
        assert p.offset == 0
        assert p.order_by is None

    def test_valid_order_by(self):
        p = ConcretePagination(order_by="name,-created_at")
        assert p.order_by == "name,-created_at"

    def test_invalid_order_by_field(self):
        with pytest.raises(ValidationException):
            ConcretePagination(order_by="invalid_field")

    def test_descending_prefix(self):
        entries = ConcretePagination._parse_order_entries("-name,+created_at")
        assert entries == [("name", True), ("created_at", False)]

    def test_empty_order_by_allowed(self):
        p = ConcretePagination(order_by="")
        assert p.order_by == ""

    def test_limit_must_be_positive(self):
        with pytest.raises(ValidationError):
            ConcretePagination(limit=0)

    def test_offset_cannot_be_negative(self):
        with pytest.raises(ValidationError):
            ConcretePagination(offset=-1)

    def test_no_orderable_fields_raises_internal(self):
        with pytest.raises(InternalException):
            PaginationQueryParameter(order_by="anything")


class TestPaginatedResponse:
    def test_structure(self):
        resp = PaginatedResponse[str](
            items=["a", "b"],
            total=10,
            page=1,
            page_size=2,
            total_pages=5,
        )
        assert resp.items == ["a", "b"]
        assert resp.total == 10
        assert resp.total_pages == 5


class TestGetModelFields:
    def test_returns_field_names(self):
        fields = get_model_fields(ConcretePagination)
        assert "limit" in fields
        assert "offset" in fields
        assert "order_by" in fields
