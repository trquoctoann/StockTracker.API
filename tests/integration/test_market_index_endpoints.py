from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.common.base_schema import PaginatedResponse
from tests.support.factories import make_market_index


@pytest.mark.asyncio
class TestCreateMarketIndex:
    async def test_create_market_index_201(
        self, app_client: AsyncClient, admin_auth_header, mock_market_index_domain_service
    ):
        mock_market_index_domain_service.create.return_value = make_market_index()

        resp = await app_client.post(
            "/api/market-indices",
            json={
                "symbol": "VNINDEX",
                "name": "VN-Index",
                "description": "Vietnam Ho Chi Minh Index",
                "group": "HOSE",
                "stock_ids": [1, 2],
            },
            headers=admin_auth_header,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["symbol"] == "VNINDEX"

    async def test_create_market_index_without_auth_returns_401(self, app_client: AsyncClient):
        resp = await app_client.post(
            "/api/market-indices",
            json={
                "symbol": "VNINDEX",
                "name": "VN-Index",
            },
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestGetMarketIndex:
    async def test_get_market_index_200(
        self, app_client: AsyncClient, admin_auth_header, mock_market_index_query_service
    ):
        mock_market_index_query_service.get_by_id.return_value = make_market_index()
        resp = await app_client.get(
            "/api/market-indices/1",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == 1


@pytest.mark.asyncio
class TestGetPageMarketIndexes:
    async def test_get_page_market_indexes_200(
        self, app_client: AsyncClient, admin_auth_header, mock_market_index_query_service
    ):
        mock_market_index_query_service.find_page.return_value = PaginatedResponse(
            items=[make_market_index()],
            total=1,
            page=1,
            page_size=10,
            total_pages=1,
        )
        resp = await app_client.get("/api/market-indices", headers=admin_auth_header)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1


@pytest.mark.asyncio
class TestGetAllMarketIndexes:
    async def test_get_all_market_indexes_200(
        self, app_client: AsyncClient, admin_auth_header, mock_market_index_query_service
    ):
        mock_market_index_query_service.find_all.return_value = [make_market_index()]
        resp = await app_client.get("/api/market-indices/all", headers=admin_auth_header)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestUpdateMarketIndex:
    async def test_update_market_index_200(
        self, app_client: AsyncClient, admin_auth_header, mock_market_index_domain_service
    ):
        mock_market_index_domain_service.update.return_value = make_market_index(name="Updated VN-Index")
        resp = await app_client.put(
            "/api/market-indices/1",
            json={
                "symbol": "VNINDEX",
                "name": "Updated VN-Index",
            },
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated VN-Index"


@pytest.mark.asyncio
class TestDeleteMarketIndex:
    async def test_delete_market_index_204(
        self, app_client: AsyncClient, admin_auth_header, mock_market_index_domain_service
    ):
        mock_market_index_domain_service.delete.return_value = None
        resp = await app_client.delete(
            "/api/market-indices/1",
            headers=admin_auth_header,
        )
        assert resp.status_code == 204
