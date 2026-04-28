from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.common.enum import RecordStatus
from app.modules.industry.application.command.industry_command import CreateIndustryCommand, UpdateIndustryCommand
from app.modules.industry.application.industry_domain_service import IndustryDomainService
from tests.support.factories import make_industry
from tests.support.fakes import make_mock_async_session


@pytest.fixture()
def session():
    return make_mock_async_session()


@pytest.fixture()
def industry_repo():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def service(session, industry_repo, query_service):
    return IndustryDomainService(
        session=session,
        industry_repository=industry_repo,
        query_service=query_service,
    )


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_returns_entity(self, service, industry_repo):
        created = make_industry()
        industry_repo.bulk_create.return_value = [created]

        cmd = CreateIndustryCommand(code="IND_001", name="Technology", level=1)
        result = await service.create(cmd)

        assert result.code == created.code
        assert result.name == created.name
        industry_repo.bulk_create.assert_called_once()


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_returns_saved_entity(self, service, industry_repo, query_service):
        existing = make_industry()
        query_service.get_by_id.return_value = existing

        updated = make_industry(name="Advanced Technology")
        industry_repo.bulk_update.return_value = [updated]

        cmd = UpdateIndustryCommand(id=1, code="IND_001", name="Advanced Technology", level=1)
        result = await service.update(cmd)

        assert result.name == "Advanced Technology"
        industry_repo.bulk_update.assert_called_once()


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_soft_deletes(self, service, industry_repo, query_service):
        existing = make_industry()
        query_service.get_by_id.return_value = existing

        await service.delete(1)

        industry_repo.bulk_update.assert_called_once()
        saved_entity = industry_repo.bulk_update.call_args[0][0][0]
        assert saved_entity.record_status == RecordStatus.DELETED
