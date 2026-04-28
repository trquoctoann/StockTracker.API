from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.common.enum import RecordStatus, StockExchange, StockType
from app.modules.stock.application.command.stock_command import CreateStockCommand, UpdateStockCommand
from app.modules.stock.application.stock_domain_service import StockDomainService
from tests.support.factories import make_industry, make_stock
from tests.support.fakes import make_mock_async_session


@pytest.fixture()
def session():
    return make_mock_async_session()


@pytest.fixture()
def stock_repo():
    return AsyncMock()


@pytest.fixture()
def stock_industry_repo():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def service(session, stock_repo, stock_industry_repo, query_service):
    return StockDomainService(
        session=session,
        stock_repository=stock_repo,
        stock_industry_repository=stock_industry_repo,
        query_service=query_service,
    )


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_returns_entity(self, service, stock_repo, stock_industry_repo):
        created = make_stock()
        stock_repo.bulk_create.return_value = [created]

        cmd = CreateStockCommand(
            symbol="FPT", name="FPT Corporation", exchange=StockExchange.HSX, type=StockType.STOCK, industry_ids={1, 2}
        )
        result = await service.create(cmd)

        assert result.symbol == created.symbol
        stock_repo.bulk_create.assert_called_once()
        stock_industry_repo.create_many_for_stock.assert_called_once_with(stock_id=created.id, industry_ids={1, 2})

    @pytest.mark.asyncio
    async def test_create_without_industries(self, service, stock_repo, stock_industry_repo):
        created = make_stock()
        stock_repo.bulk_create.return_value = [created]

        cmd = CreateStockCommand(symbol="FPT", name="FPT Corporation", exchange=StockExchange.HSX, type=StockType.STOCK)
        result = await service.create(cmd)

        assert result.symbol == created.symbol
        stock_repo.bulk_create.assert_called_once()
        stock_industry_repo.create_many_for_stock.assert_not_called()


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_returns_saved_entity(self, service, stock_repo, query_service, stock_industry_repo):
        existing = make_stock(industries=[make_industry(id=1)])
        query_service.get_by_id.return_value = existing

        updated = make_stock(name="Updated FPT")
        stock_repo.bulk_update.return_value = [updated]

        cmd = UpdateStockCommand(
            id=1,
            symbol="FPT",
            name="Updated FPT",
            exchange=StockExchange.HSX,
            type=StockType.STOCK,
            industry_ids={2, 3},
        )
        result = await service.update(cmd)

        assert result.name == "Updated FPT"
        stock_repo.bulk_update.assert_called_once()

        stock_industry_repo.delete_by_stock_id_and_industry_ids.assert_called_once_with(
            stock_id=updated.id, industry_ids={1}
        )
        stock_industry_repo.create_many_for_stock.assert_called_once_with(stock_id=updated.id, industry_ids={2, 3})


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_soft_deletes(self, service, stock_repo, query_service):
        existing = make_stock()
        query_service.get_by_id.return_value = existing

        await service.delete(1)

        stock_repo.bulk_update.assert_called_once()
        saved_entity = stock_repo.bulk_update.call_args[0][0][0]
        assert saved_entity.record_status == RecordStatus.DELETED
