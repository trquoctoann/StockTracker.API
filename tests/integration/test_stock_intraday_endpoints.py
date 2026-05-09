from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.support.factories import make_stock_intraday


@pytest.mark.asyncio
class TestSyncStockIntraday:
    async def test_sync_intraday_200(
        self, app_client: AsyncClient, admin_auth_header, mock_stock_intraday_domain_service
    ):
        mock_stock_intraday_domain_service.sync_intraday.return_value = 1

        resp = await app_client.put(
            "/api/stocks/1/intraday/sync",
            json=[
                {
                    "time": "2026-05-01T10:00:00",
                    "price": 100.0,
                    "volume": 500.0,
                    "match_type": "BUY",
                    "stock_id": 1,
                }
            ],
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["synced"] == 1


@pytest.mark.asyncio
class TestListStockIntraday:
    async def test_list_intraday_200(
        self, app_client: AsyncClient, admin_auth_header, mock_stock_intraday_query_service
    ):
        from app.common.base_schema import PaginatedResponse

        entity = make_stock_intraday()
        mock_stock_intraday_query_service.find_page.return_value = PaginatedResponse(
            items=[entity], total=1, page=1, page_size=10, total_pages=1
        )

        resp = await app_client.get(
            "/api/stocks/1/intraday",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
