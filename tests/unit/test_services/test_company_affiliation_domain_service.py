from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.modules.company_affiliation.application.command.company_affiliation_command import (
    CreateCompanyAffiliationCommand,
)
from app.modules.company_affiliation.application.company_affiliation_domain_service import (
    CompanyAffiliationDomainService,
)
from tests.support.factories import make_company_affiliation


@pytest.fixture()
def session():
    return AsyncMock()


@pytest.fixture()
def company_affiliation_repository():
    return AsyncMock()


@pytest.fixture()
def stock_query_service():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def service(session, company_affiliation_repository, stock_query_service, query_service):
    # Mock TransactionManager
    session.begin = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return CompanyAffiliationDomainService(
        session=session,
        company_affiliation_repository=company_affiliation_repository,
        stock_query_service=stock_query_service,
        query_service=query_service,
    )


class TestSync:
    @pytest.mark.asyncio
    async def test_sync_creates_new_records(
        self, service, company_affiliation_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        query_service.find_all.return_value = []

        commands = [CreateCompanyAffiliationCommand(name="Subsidiary A", type="Subsidiary", data_source_id="src_1")]
        result = await service.sync_affiliations(1, commands)

        assert len(result) == 1
        company_affiliation_repository.bulk_create.assert_called_once()
        company_affiliation_repository.bulk_update.assert_not_called()
        company_affiliation_repository.bulk_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_updates_existing_records(
        self, service, company_affiliation_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        existing = make_company_affiliation(id=10, name="Old Name", stock_id=1, data_source_id="src_1")
        query_service.find_all.return_value = [existing]

        commands = [CreateCompanyAffiliationCommand(name="New Name", type="Parent", data_source_id="src_1")]
        result = await service.sync_affiliations(1, commands)

        assert len(result) == 1
        assert result[0].name == "New Name"
        company_affiliation_repository.bulk_update.assert_called_once()
        company_affiliation_repository.bulk_create.assert_not_called()
        company_affiliation_repository.bulk_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_deletes_stale_records(
        self, service, company_affiliation_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        existing = make_company_affiliation(id=10, name="Old Affiliation", stock_id=1, data_source_id="src_1")
        query_service.find_all.return_value = [existing]

        result = await service.sync_affiliations(1, [])

        assert len(result) == 0
        company_affiliation_repository.bulk_delete.assert_called_once()
        company_affiliation_repository.bulk_create.assert_not_called()
        company_affiliation_repository.bulk_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_mixed_create_update_delete(
        self, service, company_affiliation_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        existing_keep = make_company_affiliation(id=10, name="Keep", stock_id=1, data_source_id="src_keep")
        existing_remove = make_company_affiliation(id=11, name="Remove", stock_id=1, data_source_id="src_remove")
        query_service.find_all.return_value = [existing_keep, existing_remove]

        commands = [
            CreateCompanyAffiliationCommand(name="Keep Updated", type="Subsidiary", data_source_id="src_keep"),
            CreateCompanyAffiliationCommand(name="Brand New", type="Parent", data_source_id="src_new"),
        ]
        result = await service.sync_affiliations(1, commands)

        assert len(result) == 2
        company_affiliation_repository.bulk_create.assert_called_once()
        company_affiliation_repository.bulk_update.assert_called_once()
        company_affiliation_repository.bulk_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_empty_commands_with_no_existing(
        self, service, company_affiliation_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        query_service.find_all.return_value = []

        result = await service.sync_affiliations(1, [])

        assert len(result) == 0
        company_affiliation_repository.bulk_create.assert_not_called()
        company_affiliation_repository.bulk_update.assert_not_called()
        company_affiliation_repository.bulk_delete.assert_not_called()


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_by_stock_id(self, service, company_affiliation_repository):
        await service.delete_by_stock_id(1)
        company_affiliation_repository.delete_by_stock_id.assert_called_once_with(1)
