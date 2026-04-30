from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.modules.company_profile.application.command.company_profile_command import UpsertCompanyProfileCommand
from app.modules.company_profile.application.company_profile_domain_service import CompanyProfileDomainService
from tests.support.factories import make_company_profile


@pytest.fixture()
def session():
    return AsyncMock()


@pytest.fixture()
def company_profile_repository():
    return AsyncMock()


@pytest.fixture()
def stock_query_service():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def service(session, company_profile_repository, stock_query_service, query_service):
    # Mock TransactionManager
    session.begin = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return CompanyProfileDomainService(
        session=session,
        company_profile_repository=company_profile_repository,
        stock_query_service=stock_query_service,
        query_service=query_service,
    )


class TestUpsert:
    @pytest.mark.asyncio
    async def test_upsert_creates_new(self, service, company_profile_repository, stock_query_service, query_service):
        stock_query_service.get_by_id.return_value = AsyncMock()
        query_service.find_by_stock_id.return_value = None

        created = make_company_profile()
        company_profile_repository.bulk_create.return_value = [created]

        cmd = UpsertCompanyProfileCommand(symbol="FPT", stock_id=1)
        result = await service.upsert(cmd)

        assert result.id == 1
        assert result.symbol == "FPT"
        company_profile_repository.bulk_create.assert_called_once()
        company_profile_repository.bulk_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_upsert_updates_existing(
        self, service, company_profile_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        existing = make_company_profile()
        query_service.find_by_stock_id.return_value = existing

        updated = make_company_profile(id=1, symbol="FPT_NEW", stock_id=1)
        company_profile_repository.bulk_update.return_value = [updated]

        cmd = UpsertCompanyProfileCommand(symbol="FPT_NEW", stock_id=1)
        result = await service.upsert(cmd)

        assert result.symbol == "FPT_NEW"
        company_profile_repository.bulk_update.assert_called_once()
        company_profile_repository.bulk_create.assert_not_called()


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_by_stock_id(self, service, company_profile_repository):
        await service.delete_by_stock_id(1)
        company_profile_repository.delete_by_stock_id.assert_called_once_with(1)
