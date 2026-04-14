from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.common.auth.context_token_codec import ContextTokenCodecImpl, ContextTokenPayload
from app.common.auth.permission_codes import PermissionBitmap, PermissionCode
from app.common.enum import RoleScope
from tests.support.factories import DEFAULT_USER_ID


def _build_token(*, permissions_bitmap: int = 0b11111111111111, scope: RoleScope = RoleScope.ADMIN) -> str:
    codec = ContextTokenCodecImpl()
    token, _ = codec.encode(
        ContextTokenPayload(
            subject=str(DEFAULT_USER_ID),
            scope=scope,
            tenant_id=None,
            user_version=1,
            user_roles_version=1,
            role_versions={1: 1},
            permissions_bitmap=permissions_bitmap,
        )
    )
    return token


@pytest.mark.asyncio
class TestNoAuthEndpoints:
    async def test_health_accessible_without_token(self, app_client: AsyncClient):
        resp = await app_client.get("/health")
        assert resp.status_code == 200

    async def test_nonexistent_path_returns_404(self, app_client: AsyncClient):
        resp = await app_client.get("/does-not-exist")
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestBearerTokenRequired:
    async def test_protected_endpoint_without_token_returns_401(self, app_client: AsyncClient):
        resp = await app_client.get("/api/users")
        assert resp.status_code == 401

    async def test_protected_endpoint_with_invalid_context_token_is_rejected(self, app_client: AsyncClient):
        from jose import jwt as jose_jwt

        from app.exception.exception import ContextTokenUnauthorizedException

        bad_token = jose_jwt.encode(
            {"token_type": "context", "sub": "x", "scope": "ADMIN"},
            "wrong-secret",
            algorithm="HS256",
        )
        with pytest.raises((ContextTokenUnauthorizedException, Exception)):
            await app_client.get(
                "/api/users",
                headers={"Authorization": f"Bearer {bad_token}"},
            )

    async def test_bearer_scheme_required(self, app_client: AsyncClient):
        token = _build_token()
        resp = await app_client.get(
            "/api/users",
            headers={"Authorization": f"Basic {token}"},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestPermissionEnforcement:
    async def test_no_permissions_returns_403(self, app_client: AsyncClient):
        token = _build_token(permissions_bitmap=0)
        resp = await app_client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    async def test_insufficient_permissions_returns_403(self, app_client: AsyncClient):
        bitmap = PermissionBitmap()
        bm = bitmap.to_bitmap({PermissionCode.ROLE_READ})
        token = _build_token(permissions_bitmap=bm)
        resp = await app_client.post(
            "/api/users",
            json={
                "username": "x",
                "password": "Strong1!pass",
                "email": "x@x.com",
                "first_name": "X",
                "last_name": None,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestScopeEnforcement:
    async def test_tenant_scope_denied_for_admin_only_route(self, app_client: AsyncClient):
        token = _build_token(scope=RoleScope.TENANT)
        resp = await app_client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
