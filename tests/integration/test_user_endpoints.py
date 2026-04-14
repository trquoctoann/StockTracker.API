from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.common.base_schema import PaginatedResponse
from tests.support.factories import DEFAULT_USER_ID, make_user, make_user_role


def _user_response_body(**overrides):
    base = {
        "id": str(DEFAULT_USER_ID),
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "status": "ACTIVE",
        "record_status": "ENABLED",
        "version": 1,
        "created_at": "2025-01-15T12:00:00",
        "created_by": "system",
        "updated_at": "2025-01-15T12:00:00",
        "updated_by": "system",
        "user_roles": None,
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
class TestCreateUser:
    async def test_create_user_201(self, app_client: AsyncClient, admin_auth_header, mock_user_domain_service):
        mock_user_domain_service.create.return_value = make_user()

        resp = await app_client.post(
            "/api/users",
            json={
                "username": "newuser",
                "password": "Strong1!pass",
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "User",
            },
            headers=admin_auth_header,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["username"] == "testuser"
        assert body["id"] == str(DEFAULT_USER_ID)

    async def test_create_user_without_auth_returns_401(self, app_client: AsyncClient):
        resp = await app_client.post(
            "/api/users",
            json={
                "username": "x",
                "password": "Strong1!pass",
                "email": "x@example.com",
                "first_name": "X",
                "last_name": None,
            },
        )
        assert resp.status_code == 401

    async def test_create_user_missing_fields_returns_422(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.post(
            "/api/users",
            json={"username": "x"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestGetUser:
    async def test_get_user_200(self, app_client: AsyncClient, admin_auth_header, mock_user_query_service):
        mock_user_query_service.get_by_id.return_value = make_user()
        resp = await app_client.get(
            f"/api/users/{DEFAULT_USER_ID}",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == str(DEFAULT_USER_ID)

    async def test_get_user_invalid_uuid_returns_422(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.get(
            "/api/users/not-a-uuid",
            headers=admin_auth_header,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestGetPageUsers:
    async def test_get_page_users_200(self, app_client: AsyncClient, admin_auth_header, mock_user_query_service):
        mock_user_query_service.find_page.return_value = PaginatedResponse(
            items=[make_user()],
            total=1,
            page=1,
            page_size=10,
            total_pages=1,
        )
        resp = await app_client.get("/api/users", headers=admin_auth_header)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1


@pytest.mark.asyncio
class TestGetAllUsers:
    async def test_get_all_users_200(self, app_client: AsyncClient, admin_auth_header, mock_user_query_service):
        mock_user_query_service.find_all.return_value = [make_user()]
        resp = await app_client.get("/api/users/all", headers=admin_auth_header)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestUpdateUser:
    async def test_update_user_200(self, app_client: AsyncClient, admin_auth_header, mock_user_domain_service):
        mock_user_domain_service.update.return_value = make_user(first_name="Updated")
        resp = await app_client.put(
            f"/api/users/{DEFAULT_USER_ID}",
            json={
                "username": "testuser",
                "password": "Strong1!pass",
                "email": "test@example.com",
                "first_name": "Updated",
                "last_name": "User",
            },
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Updated"


@pytest.mark.asyncio
class TestDeleteUser:
    async def test_delete_user_204(self, app_client: AsyncClient, admin_auth_header, mock_user_domain_service):
        mock_user_domain_service.delete.return_value = None
        resp = await app_client.delete(
            f"/api/users/{DEFAULT_USER_ID}",
            headers=admin_auth_header,
        )
        assert resp.status_code == 204


@pytest.mark.asyncio
class TestSetUserRoles:
    async def test_set_roles_200(self, app_client: AsyncClient, admin_auth_header, mock_user_domain_service):
        mock_user_domain_service.set_roles.return_value = make_user(
            user_roles=[make_user_role()],
        )
        resp = await app_client.put(
            f"/api/users/{DEFAULT_USER_ID}/roles",
            json={"role_ids": [1, 2]},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
