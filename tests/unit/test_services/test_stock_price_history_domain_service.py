from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.common.enum import PriceInterval
from app.modules.stock_price_history.application.command.stock_price_history_command import (
    UpsertStockPriceHistoryCommand,
)
from app.modules.stock_price_history.application.stock_price_history_domain_service import (
    StockPriceHistoryDomainService,
)
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
    return StockPriceHistoryDomainService(
        session=session,
        stock_price_history_repository=repository,
        stock_query_service=stock_query_service,
        cache_service=cache_service,
    )


class TestSyncPriceHistory:
    @pytest.mark.asyncio
    async def test_sync_creates_records(self, service, repository, stock_query_service):
        stock_query_service.get_by_id.return_value = AsyncMock()
        repository.bulk_upsert.return_value = None

        commands = [
            UpsertStockPriceHistoryCommand(
                time=datetime.strptime("2026-05-01T10:00:00", "%Y-%m-%dT%H:%M:%S"),
                interval=PriceInterval.ONE_DAY,
                open=100.0,
                high=105.0,
                low=99.0,
                close=103.0,
                volume=1000000.0,
                stock_id=1,
            )
        ]
        count = await service.sync_price_history(1, PriceInterval.ONE_DAY, commands)

        assert count == 1
        repository.bulk_upsert.assert_called_once()
        stock_query_service.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_sync_empty_commands(self, service, repository, stock_query_service):
        stock_query_service.get_by_id.return_value = AsyncMock()

        count = await service.sync_price_history(1, PriceInterval.ONE_DAY, [])

        assert count == 0
        repository.bulk_upsert.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_multiple_records(self, service, repository, stock_query_service):
        stock_query_service.get_by_id.return_value = AsyncMock()
        repository.bulk_upsert.return_value = None

        commands = [
            UpsertStockPriceHistoryCommand(
                time=datetime.strptime(f"2026-05-0{i}T10:00:00", "%Y-%m-%dT%H:%M:%S"),
                interval=PriceInterval.ONE_DAY,
                open=100.0,
                high=105.0,
                low=99.0,
                close=103.0,
                volume=1000000.0,
                stock_id=1,
            )
            for i in range(1, 4)
        ]
        count = await service.sync_price_history(1, PriceInterval.ONE_DAY, commands)

        assert count == 3
        repository.bulk_upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_invalidates_cache(self, service, repository, stock_query_service, cache_service):
        stock_query_service.get_by_id.return_value = AsyncMock()
        repository.bulk_upsert.return_value = None

        await cache_service.set("stock_price_history:1:1D:bars", "data")

        commands = [
            UpsertStockPriceHistoryCommand(
                time=datetime.strptime("2026-05-01T10:00:00", "%Y-%m-%dT%H:%M:%S"),
                interval=PriceInterval.ONE_DAY,
                open=100.0,
                high=105.0,
                low=99.0,
                close=103.0,
                volume=1000000.0,
                stock_id=1,
            )
        ]
        await service.sync_price_history(1, PriceInterval.ONE_DAY, commands)

        assert await cache_service.get("stock_price_history:1:1D:bars") is None


class TestDeleteByStockId:
    @pytest.mark.asyncio
    async def test_delete_by_stock_id(self, service, repository):
        await service.delete_by_stock_id(1)
        repository.delete_by_stock_id.assert_called_once_with(1)
