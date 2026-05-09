from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.support.factories import make_stock_price_history


@pytest.mark.asyncio
class TestSyncStockPriceHistory:
    async def test_sync_price_history_200(
        self, app_client: AsyncClient, admin_auth_header, mock_stock_price_history_domain_service
    ):
        mock_stock_price_history_domain_service.sync_price_history.return_value = 1

        resp = await app_client.put(
            "/api/stocks/1/price-history/sync?interval=1D",
            json=[
                {
                    "time": "2026-05-01T10:00:00",
                    "interval": "1D",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 99.0,
                    "close": 103.0,
                    "volume": 1000000.0,
                    "stock_id": 1,
                }
            ],
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["synced"] == 1


@pytest.mark.asyncio
class TestListStockPriceHistory:
    async def test_list_price_history_200(
        self, app_client: AsyncClient, admin_auth_header, mock_stock_price_history_query_service
    ):
        from app.common.base_schema import PaginatedResponse

        entity = make_stock_price_history()
        mock_stock_price_history_query_service.find_page.return_value = PaginatedResponse(
            items=[entity], total=1, page=1, page_size=10, total_pages=1
        )

        resp = await app_client.get(
            "/api/stocks/1/price-history",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 1


@pytest.mark.asyncio
class TestGetPriceBars:
    async def test_get_bars_200(
        self, app_client: AsyncClient, admin_auth_header, mock_stock_price_history_query_service
    ):
        mock_stock_price_history_query_service.find_bars.return_value = [
            make_stock_price_history(id=i) for i in range(1, 4)
        ]

        resp = await app_client.get(
            "/api/stocks/1/price-history/bars?interval=1D&limit=3",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 3
