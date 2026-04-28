from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.common.base_schema import PaginatedResponse
from app.common.enum import StockExchange, StockType
from tests.support.factories import make_stock


@pytest.mark.asyncio
class TestCreateStock:
    async def test_create_stock_201(self, app_client: AsyncClient, admin_auth_header, mock_stock_domain_service):
        mock_stock_domain_service.create.return_value = make_stock()

        resp = await app_client.post(
            "/api/stocks",
            json={
                "symbol": "FPT",
                "name": "FPT Corporation",
                "short_name": "FPT",
                "exchange": StockExchange.HSX.value,
                "type": StockType.STOCK.value,
                "industry_ids": [1, 2],
            },
            headers=admin_auth_header,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["symbol"] == "FPT"

    async def test_create_stock_without_auth_returns_401(self, app_client: AsyncClient):
        resp = await app_client.post(
            "/api/stocks",
            json={
                "symbol": "FPT",
                "name": "FPT Corporation",
                "exchange": StockExchange.HSX.value,
                "type": StockType.STOCK.value,
            },
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestGetStock:
    async def test_get_stock_200(self, app_client: AsyncClient, admin_auth_header, mock_stock_query_service):
        mock_stock_query_service.get_by_id.return_value = make_stock()
        resp = await app_client.get(
            "/api/stocks/1",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == 1


@pytest.mark.asyncio
class TestGetPageStocks:
    async def test_get_page_stocks_200(self, app_client: AsyncClient, admin_auth_header, mock_stock_query_service):
        mock_stock_query_service.find_page.return_value = PaginatedResponse(
            items=[make_stock()],
            total=1,
            page=1,
            page_size=10,
            total_pages=1,
        )
        resp = await app_client.get("/api/stocks", headers=admin_auth_header)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1


@pytest.mark.asyncio
class TestGetAllStocks:
    async def test_get_all_stocks_200(self, app_client: AsyncClient, admin_auth_header, mock_stock_query_service):
        mock_stock_query_service.find_all.return_value = [make_stock()]
        resp = await app_client.get("/api/stocks/all", headers=admin_auth_header)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestUpdateStock:
    async def test_update_stock_200(self, app_client: AsyncClient, admin_auth_header, mock_stock_domain_service):
        mock_stock_domain_service.update.return_value = make_stock(name="Updated FPT")
        resp = await app_client.put(
            "/api/stocks/1",
            json={
                "symbol": "FPT",
                "name": "Updated FPT",
                "exchange": StockExchange.HSX.value,
                "type": StockType.STOCK.value,
            },
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated FPT"


@pytest.mark.asyncio
class TestDeleteStock:
    async def test_delete_stock_204(self, app_client: AsyncClient, admin_auth_header, mock_stock_domain_service):
        mock_stock_domain_service.delete.return_value = None
        resp = await app_client.delete(
            "/api/stocks/1",
            headers=admin_auth_header,
        )
        assert resp.status_code == 204
