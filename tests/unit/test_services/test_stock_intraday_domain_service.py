from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.common.enum import MatchType
from app.modules.stock_intraday.application.command.stock_intraday_command import UpsertStockIntradayCommand
from app.modules.stock_intraday.application.stock_intraday_domain_service import StockIntradayDomainService
from tests.support.fakes import FakeCacheService


@pytest.fixture()
def session():
    return AsyncMock()


@pytest.fixture()
def repository():
    return AsyncMock()


@pytest.fixture()
def stock_query_service():
    return AsyncMock()


@pytest.fixture()
def cache_service():
    return FakeCacheService()


@pytest.fixture()
def service(session, repository, stock_query_service, cache_service):
    session.begin = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return StockIntradayDomainService(
        session=session,
        stock_intraday_repository=repository,
        stock_query_service=stock_query_service,
        cache_service=cache_service,
    )


class TestSyncIntraday:
    @pytest.mark.asyncio
    async def test_sync_creates_records(self, service, repository, stock_query_service):
        stock_query_service.get_by_id.return_value = AsyncMock()
        repository.bulk_upsert.return_value = None

        commands = [
            UpsertStockIntradayCommand(
                time=datetime.strptime("2026-05-01T10:00:00", "%Y-%m-%dT%H:%M:%S"),
                price=100.0,
                volume=500.0,
                match_type=MatchType.BUY,
                stock_id=1,
            )
        ]
        count = await service.sync_intraday(1, commands)

        assert count == 1
        repository.bulk_upsert.assert_called_once()
        stock_query_service.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_sync_empty_commands(self, service, repository, stock_query_service):
        stock_query_service.get_by_id.return_value = AsyncMock()

        count = await service.sync_intraday(1, [])

        assert count == 0
        repository.bulk_upsert.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_multiple_records(self, service, repository, stock_query_service):
        stock_query_service.get_by_id.return_value = AsyncMock()
        repository.bulk_upsert.return_value = None

        commands = [
            UpsertStockIntradayCommand(
                time=datetime.strptime(f"2026-05-01T10:0{i}:00", "%Y-%m-%dT%H:%M:%S"),
                price=100.0 + i,
                volume=500.0,
                match_type=MatchType.BUY,
                stock_id=1,
            )
            for i in range(5)
        ]
        count = await service.sync_intraday(1, commands)

        assert count == 5
        repository.bulk_upsert.assert_called_once()


class TestDeleteByStockId:
    @pytest.mark.asyncio
    async def test_delete_by_stock_id(self, service, repository):
        await service.delete_by_stock_id(1)
        repository.delete_by_stock_id.assert_called_once_with(1)
