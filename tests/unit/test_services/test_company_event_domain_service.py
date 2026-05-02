from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.modules.company_event.application.command.company_event_command import (
    CreateCompanyEventCommand,
)
from app.modules.company_event.application.company_event_domain_service import (
    CompanyEventDomainService,
)
from tests.support.factories import make_company_event


@pytest.fixture()
def session():
    return AsyncMock()


@pytest.fixture()
def company_event_repository():
    return AsyncMock()


@pytest.fixture()
def stock_query_service():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def service(session, company_event_repository, stock_query_service, query_service):
    # Mock TransactionManager
    session.begin = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return CompanyEventDomainService(
        session=session,
        company_event_repository=company_event_repository,
        stock_query_service=stock_query_service,
        query_service=query_service,
    )


class TestSync:
    @pytest.mark.asyncio
    async def test_sync_creates_new_records(
        self, service, company_event_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        query_service.find_all.return_value = []

        commands = [CreateCompanyEventCommand(title="Dividend Payment", data_source_id="src_1")]
        result = await service.sync_events(1, commands)

        assert len(result) == 1
        company_event_repository.bulk_create.assert_called_once()
        company_event_repository.bulk_update.assert_not_called()
        company_event_repository.bulk_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_updates_existing_records(
        self, service, company_event_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        existing = make_company_event(id=10, title="Old Event", stock_id=1, data_source_id="src_1")
        query_service.find_all.return_value = [existing]

        commands = [CreateCompanyEventCommand(title="New Event", data_source_id="src_1")]
        result = await service.sync_events(1, commands)

        assert len(result) == 1
        assert result[0].title == "New Event"
        company_event_repository.bulk_update.assert_called_once()
        company_event_repository.bulk_create.assert_not_called()
        company_event_repository.bulk_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_deletes_stale_records(
        self, service, company_event_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        existing = make_company_event(id=10, title="Old Event", stock_id=1, data_source_id="src_1")
        query_service.find_all.return_value = [existing]

        result = await service.sync_events(1, [])

        assert len(result) == 0
        company_event_repository.bulk_delete.assert_called_once()
        company_event_repository.bulk_create.assert_not_called()
        company_event_repository.bulk_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_mixed_create_update_delete(
        self, service, company_event_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        existing_keep = make_company_event(id=10, title="Keep", stock_id=1, data_source_id="src_keep")
        existing_remove = make_company_event(id=11, title="Remove", stock_id=1, data_source_id="src_remove")
        query_service.find_all.return_value = [existing_keep, existing_remove]

        commands = [
            CreateCompanyEventCommand(title="Keep Updated", data_source_id="src_keep"),
            CreateCompanyEventCommand(title="Brand New", data_source_id="src_new"),
        ]
        result = await service.sync_events(1, commands)

        assert len(result) == 2
        company_event_repository.bulk_create.assert_called_once()
        company_event_repository.bulk_update.assert_called_once()
        company_event_repository.bulk_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_empty_commands_with_no_existing(
        self, service, company_event_repository, stock_query_service, query_service
    ):
        stock_query_service.get_by_id.return_value = AsyncMock()
        query_service.find_all.return_value = []

        result = await service.sync_events(1, [])

        assert len(result) == 0
        company_event_repository.bulk_create.assert_not_called()
        company_event_repository.bulk_update.assert_not_called()
        company_event_repository.bulk_delete.assert_not_called()


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_by_stock_id(self, service, company_event_repository):
        await service.delete_by_stock_id(1)
        company_event_repository.delete_by_stock_id.assert_called_once_with(1)
