from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.common.base_schema import PaginatedResponse
from tests.support.factories import make_tenant


@pytest.mark.asyncio
class TestCreateTenant:
    async def test_create_tenant_201(self, app_client: AsyncClient, admin_auth_header, mock_tenant_domain_service):
        mock_tenant_domain_service.create.return_value = make_tenant()
        resp = await app_client.post(
            "/api/tenants",
            json={"name": "Acme Corp"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Test Tenant"

    async def test_create_tenant_without_auth_401(self, app_client: AsyncClient):
        resp = await app_client.post("/api/tenants", json={"name": "X"})
        assert resp.status_code == 401

    async def test_create_tenant_missing_name_422(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.post(
            "/api/tenants",
            json={},
            headers=admin_auth_header,
        )
        assert resp.status_code == 422

    async def test_create_tenant_with_parent(
        self, app_client: AsyncClient, admin_auth_header, mock_tenant_domain_service
    ):
        mock_tenant_domain_service.create.return_value = make_tenant(parent_tenant_id=1)
        resp = await app_client.post(
            "/api/tenants",
            json={"name": "Child", "parent_tenant_id": 1},
            headers=admin_auth_header,
        )
        assert resp.status_code == 201


@pytest.mark.asyncio
class TestGetTenant:
    async def test_get_tenant_200(self, app_client: AsyncClient, admin_auth_header, mock_tenant_query_service):
        mock_tenant_query_service.get_by_id.return_value = make_tenant()
        resp = await app_client.get("/api/tenants/1", headers=admin_auth_header)
        assert resp.status_code == 200
        assert resp.json()["id"] == 1


@pytest.mark.asyncio
class TestGetPageTenants:
    async def test_get_page_tenants_200(self, app_client: AsyncClient, admin_auth_header, mock_tenant_query_service):
        mock_tenant_query_service.find_page.return_value = PaginatedResponse(
            items=[make_tenant()],
            total=1,
            page=1,
            page_size=10,
            total_pages=1,
        )
        resp = await app_client.get("/api/tenants", headers=admin_auth_header)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1


@pytest.mark.asyncio
class TestGetAllTenants:
    async def test_get_all_tenants_200(self, app_client: AsyncClient, admin_auth_header, mock_tenant_query_service):
        mock_tenant_query_service.find_all.return_value = [make_tenant()]
        resp = await app_client.get("/api/tenants/all", headers=admin_auth_header)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestUpdateTenant:
    async def test_update_tenant_200(self, app_client: AsyncClient, admin_auth_header, mock_tenant_domain_service):
        mock_tenant_domain_service.update.return_value = make_tenant(name="Renamed")
        resp = await app_client.put(
            "/api/tenants/1",
            json={"name": "Renamed"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"


@pytest.mark.asyncio
class TestDeleteTenant:
    async def test_delete_tenant_204(self, app_client: AsyncClient, admin_auth_header, mock_tenant_domain_service):
        mock_tenant_domain_service.delete.return_value = None
        resp = await app_client.delete("/api/tenants/1", headers=admin_auth_header)
        assert resp.status_code == 204
