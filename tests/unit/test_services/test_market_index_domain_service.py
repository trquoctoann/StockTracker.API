from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.common.enum import RecordStatus
from app.modules.market_index.application.command.market_index_command import (
    CreateMarketIndexCommand,
    UpdateMarketIndexCommand,
)
from app.modules.market_index.application.market_index_domain_service import MarketIndexDomainService
from tests.support.factories import make_market_index, make_stock
from tests.support.fakes import make_mock_async_session


@pytest.fixture()
def session():
    return make_mock_async_session()


@pytest.fixture()
def market_index_repo():
    return AsyncMock()


@pytest.fixture()
def index_composition_repo():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def service(session, market_index_repo, index_composition_repo, query_service):
    return MarketIndexDomainService(
        session=session,
        market_index_repository=market_index_repo,
        index_composition_repository=index_composition_repo,
        query_service=query_service,
    )


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_returns_entity(self, service, market_index_repo, index_composition_repo):
        created = make_market_index()
        market_index_repo.bulk_create.return_value = [created]

        cmd = CreateMarketIndexCommand(symbol="VNINDEX", name="VN-Index", stock_ids={1, 2})
        result = await service.create(cmd)

        assert result.symbol == created.symbol
        market_index_repo.bulk_create.assert_called_once()
        index_composition_repo.create_many_for_index.assert_called_once_with(
            market_index_id=created.id, stock_ids={1, 2}
        )

    @pytest.mark.asyncio
    async def test_create_without_stocks(self, service, market_index_repo, index_composition_repo):
        created = make_market_index()
        market_index_repo.bulk_create.return_value = [created]

        cmd = CreateMarketIndexCommand(symbol="VNINDEX", name="VN-Index")
        result = await service.create(cmd)

        assert result.symbol == created.symbol
        market_index_repo.bulk_create.assert_called_once()
        index_composition_repo.create_many_for_index.assert_not_called()


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_returns_saved_entity(self, service, market_index_repo, query_service, index_composition_repo):
        existing = make_market_index(stocks=[make_stock(id=1)])
        query_service.get_by_id.return_value = existing

        updated = make_market_index(name="Updated Index")
        market_index_repo.bulk_update.return_value = [updated]

        cmd = UpdateMarketIndexCommand(id=1, symbol="VNINDEX", name="Updated Index", stock_ids={2, 3})
        result = await service.update(cmd)

        assert result.name == "Updated Index"
        market_index_repo.bulk_update.assert_called_once()

        # Original was {1}, new is {2, 3}. So it should delete {1} and create {2, 3}.
        index_composition_repo.delete_by_market_index_id_and_stock_ids.assert_called_once_with(
            market_index_id=updated.id, stock_ids={1}
        )
        index_composition_repo.create_many_for_index.assert_called_once_with(
            market_index_id=updated.id, stock_ids={2, 3}
        )


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_soft_deletes(self, service, market_index_repo, query_service):
        existing = make_market_index()
        query_service.get_by_id.return_value = existing

        await service.delete(1)

        market_index_repo.bulk_update.assert_called_once()
        saved_entity = market_index_repo.bulk_update.call_args[0][0][0]
        assert saved_entity.record_status == RecordStatus.DELETED
