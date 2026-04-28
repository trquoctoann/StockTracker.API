from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.common.base_schema import PaginatedResponse
from tests.support.factories import make_industry


@pytest.mark.asyncio
class TestCreateIndustry:
    async def test_create_industry_201(self, app_client: AsyncClient, admin_auth_header, mock_industry_domain_service):
        mock_industry_domain_service.create.return_value = make_industry()

        resp = await app_client.post(
            "/api/industries",
            json={"code": "IND_001", "name": "Technology", "level": 1},
            headers=admin_auth_header,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["code"] == "IND_001"

    async def test_create_industry_without_auth_returns_401(self, app_client: AsyncClient):
        resp = await app_client.post(
            "/api/industries",
            json={"code": "IND_001", "name": "Technology", "level": 1},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestGetIndustry:
    async def test_get_industry_200(self, app_client: AsyncClient, admin_auth_header, mock_industry_query_service):
        mock_industry_query_service.get_by_id.return_value = make_industry()
        resp = await app_client.get(
            "/api/industries/1",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == 1


@pytest.mark.asyncio
class TestGetPageIndustries:
    async def test_get_page_industries_200(
        self, app_client: AsyncClient, admin_auth_header, mock_industry_query_service
    ):
        mock_industry_query_service.find_page.return_value = PaginatedResponse(
            items=[make_industry()],
            total=1,
            page=1,
            page_size=10,
            total_pages=1,
        )
        resp = await app_client.get("/api/industries", headers=admin_auth_header)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1


@pytest.mark.asyncio
class TestGetAllIndustries:
    async def test_get_all_industries_200(
        self, app_client: AsyncClient, admin_auth_header, mock_industry_query_service
    ):
        mock_industry_query_service.find_all.return_value = [make_industry()]
        resp = await app_client.get("/api/industries/all", headers=admin_auth_header)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestUpdateIndustry:
    async def test_update_industry_200(self, app_client: AsyncClient, admin_auth_header, mock_industry_domain_service):
        mock_industry_domain_service.update.return_value = make_industry(name="Updated Technology")
        resp = await app_client.put(
            "/api/industries/1",
            json={"code": "IND_001", "name": "Updated Technology", "level": 1},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Technology"


@pytest.mark.asyncio
class TestDeleteIndustry:
    async def test_delete_industry_204(self, app_client: AsyncClient, admin_auth_header, mock_industry_domain_service):
        mock_industry_domain_service.delete.return_value = None
        resp = await app_client.delete(
            "/api/industries/1",
            headers=admin_auth_header,
        )
        assert resp.status_code == 204
