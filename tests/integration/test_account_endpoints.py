from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.common.current_user import CurrentUserService, get_current_user_service
from app.modules.account.account_dependency import get_account_domain_service, get_account_query_service
from app.modules.account.application.account_domain_service import AccountDomainService
from app.modules.account.application.account_query_service import AccountQueryService
from tests.support.factories import DEFAULT_USER_ID, make_user, make_user_role


@pytest.fixture()
def mock_current_user_service():
    svc = AsyncMock(spec=CurrentUserService)
    svc.get_current_user.return_value = make_user(user_roles=[make_user_role()])
    return svc


@pytest.fixture()
def mock_account_query_service():
    svc = AsyncMock(spec=AccountQueryService)
    svc.get_me.return_value = make_user(user_roles=[make_user_role()])
    return svc


@pytest.fixture()
def mock_account_domain_service():
    return AsyncMock(spec=AccountDomainService)


@pytest.fixture()
async def account_client(
    app_client,
    mock_current_user_service,
    mock_account_query_service,
    mock_account_domain_service,
):
    transport = app_client._transport
    app = transport.app  # type: ignore[attr-defined]

    app.dependency_overrides[get_current_user_service] = lambda: mock_current_user_service
    app.dependency_overrides[get_account_query_service] = lambda: mock_account_query_service
    app.dependency_overrides[get_account_domain_service] = lambda: mock_account_domain_service
    yield app_client


@pytest.mark.asyncio
class TestGetMyProfile:
    async def test_get_profile_200(self, account_client, admin_auth_header, mock_account_query_service):
        mock_account_query_service.get_me.return_value = make_user()
        resp = await account_client.get("/api/accounts", headers=admin_auth_header)
        assert resp.status_code == 200
        assert resp.json()["id"] == str(DEFAULT_USER_ID)

    async def test_get_profile_without_auth_401(self, account_client):
        resp = await account_client.get("/api/accounts")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestUpdateMyProfile:
    async def test_update_profile_200(self, account_client, admin_auth_header, mock_account_domain_service):
        mock_account_domain_service.update_profile.return_value = make_user(first_name="Updated")
        resp = await account_client.put(
            "/api/accounts/profile",
            json={"first_name": "Updated"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Updated"

    async def test_update_profile_missing_first_name_422(self, account_client, admin_auth_header):
        resp = await account_client.put(
            "/api/accounts/profile",
            json={},
            headers=admin_auth_header,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestUpdateMyPassword:
    async def test_update_password_204(self, account_client, admin_auth_header, mock_account_domain_service):
        mock_account_domain_service.update_password.return_value = None
        resp = await account_client.put(
            "/api/accounts/password",
            json={"new_password": "NewStr0ng!pass"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 204


@pytest.mark.asyncio
class TestSwitchContext:
    async def test_switch_context_200(self, account_client, admin_auth_header, mock_account_domain_service):
        mock_account_domain_service.switch_context.return_value = ("new.jwt.token", 300)
        resp = await account_client.post(
            "/api/accounts/switch-context",
            json={"scope": "ADMIN"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["token_type"] == "Bearer"
        assert body["access_token"] == "new.jwt.token"
        assert body["expires_in"] == 300

    async def test_switch_context_invalid_scope_422(self, account_client, admin_auth_header):
        resp = await account_client.post(
            "/api/accounts/switch-context",
            json={"scope": "INVALID"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 422
