from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.common.base_schema import PaginatedResponse
from tests.support.factories import make_permission, make_role


@pytest.mark.asyncio
class TestCreateRole:
    async def test_create_role_201(self, app_client: AsyncClient, admin_auth_header, mock_role_domain_service):
        mock_role_domain_service.create.return_value = make_role()
        resp = await app_client.post(
            "/api/roles",
            json={"scope": "ADMIN", "name": "New Role"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Admin Role"
        assert body["scope"] == "ADMIN"

    async def test_create_role_without_auth_401(self, app_client: AsyncClient):
        resp = await app_client.post(
            "/api/roles",
            json={"scope": "ADMIN", "name": "Role"},
        )
        assert resp.status_code == 401

    async def test_create_role_missing_name_422(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.post(
            "/api/roles",
            json={"scope": "ADMIN"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestGetRole:
    async def test_get_role_200(self, app_client: AsyncClient, admin_auth_header, mock_role_query_service):
        mock_role_query_service.get_by_id.return_value = make_role(
            permissions=[make_permission()],
        )
        resp = await app_client.get("/api/roles/1", headers=admin_auth_header)
        assert resp.status_code == 200
        assert resp.json()["id"] == 1


@pytest.mark.asyncio
class TestGetPageRoles:
    async def test_get_page_roles_200(self, app_client: AsyncClient, admin_auth_header, mock_role_query_service):
        mock_role_query_service.find_page.return_value = PaginatedResponse(
            items=[make_role()],
            total=1,
            page=1,
            page_size=10,
            total_pages=1,
        )
        resp = await app_client.get("/api/roles", headers=admin_auth_header)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1


@pytest.mark.asyncio
class TestGetAllRoles:
    async def test_get_all_roles_200(self, app_client: AsyncClient, admin_auth_header, mock_role_query_service):
        mock_role_query_service.find_all.return_value = [make_role()]
        resp = await app_client.get("/api/roles/all", headers=admin_auth_header)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestUpdateRole:
    async def test_update_role_200(self, app_client: AsyncClient, admin_auth_header, mock_role_domain_service):
        mock_role_domain_service.update.return_value = make_role(name="Renamed")
        resp = await app_client.put(
            "/api/roles/1",
            json={"scope": "ADMIN", "name": "Renamed"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"


@pytest.mark.asyncio
class TestDeleteRole:
    async def test_delete_role_204(self, app_client: AsyncClient, admin_auth_header, mock_role_domain_service):
        mock_role_domain_service.delete.return_value = None
        resp = await app_client.delete("/api/roles/1", headers=admin_auth_header)
        assert resp.status_code == 204


@pytest.mark.asyncio
class TestSetRolePermissions:
    async def test_set_permissions_200(self, app_client: AsyncClient, admin_auth_header, mock_role_domain_service):
        mock_role_domain_service.set_permissions.return_value = make_role(
            permissions=[make_permission()],
        )
        resp = await app_client.put(
            "/api/roles/1/permissions",
            json={"permission_ids": [1, 2]},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
