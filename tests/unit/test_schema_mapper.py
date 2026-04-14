import pytest
from pydantic import BaseModel

from app.common.base_mapper import SchemaMapper, _deep_merge
from app.common.base_schema import BaseCommand
from app.exception.exception import InternalException


class SampleCommand(BaseCommand):
    name: str
    description: str | None = None
    extra: int = 0


class SampleEntity(BaseModel):
    name: str
    description: str | None = None
    extra: int = 0
    read_only: str = "default"


class SampleResponse(BaseModel):
    name: str
    description: str | None = None


class TestCommandToEntity:
    def test_basic_mapping(self):
        cmd = SampleCommand(name="Test", description="desc", extra=5)
        entity = SchemaMapper.command_to_entity(cmd, SampleEntity)
        assert entity.name == "Test"
        assert entity.description == "desc"
        assert entity.extra == 5

    def test_unset_fields_excluded(self):
        cmd = SampleCommand(name="Test")
        entity = SchemaMapper.command_to_entity(cmd, SampleEntity)
        assert entity.name == "Test"
        assert entity.read_only == "default"

    def test_overrides_applied(self):
        cmd = SampleCommand(name="Test")
        entity = SchemaMapper.command_to_entity(cmd, SampleEntity, overrides={"read_only": "custom"})
        assert entity.read_only == "custom"

    def test_conflicting_override_raises(self):
        cmd = SampleCommand(name="Test")
        with pytest.raises(InternalException):
            SchemaMapper.command_to_entity(cmd, SampleEntity, overrides={"name": "conflict"})


class TestEntityToResponse:
    def test_basic_mapping(self):
        entity = SampleEntity(name="E", description="D", extra=10)
        resp = SchemaMapper.entity_to_response(entity, SampleResponse)
        assert resp.name == "E"
        assert resp.description == "D"

    def test_extra_fields_ignored(self):
        entity = SampleEntity(name="E", extra=99)
        resp = SchemaMapper.entity_to_response(entity, SampleResponse)
        assert resp.name == "E"
        assert not hasattr(resp, "extra")


class TestMergeSourceIntoTarget:
    def test_merge_updates_target(self):
        source = SampleEntity(name="new_name")
        target = SampleEntity(name="old", description="keep", extra=1)
        merged = SchemaMapper.merge_source_into_target(source, target)
        assert merged.name == "new_name"
        assert merged.description == "keep"

    def test_forbidden_fields_preserved(self):
        source = SampleEntity(name="new_name", extra=99)
        target = SampleEntity(name="old", extra=1)
        merged = SchemaMapper.merge_source_into_target(source, target, forbidden=frozenset({"extra"}))
        assert merged.extra == 1
        assert merged.name == "new_name"


class TestDeepMerge:
    def test_flat_merge(self):
        result = _deep_merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_nested_merge(self):
        result = _deep_merge({"a": {"x": 1, "y": 2}}, {"a": {"y": 3, "z": 4}})
        assert result == {"a": {"x": 1, "y": 3, "z": 4}}

    def test_overwrite_non_dict(self):
        result = _deep_merge({"a": 1}, {"a": "new"})
        assert result == {"a": "new"}


class TestSharedFieldNames:
    def test_intersects_fields(self):
        shared = SchemaMapper.shared_field_names(SampleEntity, SampleResponse)
        assert "name" in shared
        assert "description" in shared
        assert "extra" not in shared
