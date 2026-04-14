from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.exception.exception import BusinessViolationException, NotFoundException
from tests.support.factories import DEFAULT_USER_ID


@pytest.mark.asyncio
class TestValidationErrorHandling:
    async def test_invalid_json_returns_422(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.post(
            "/api/users",
            content=b"not json",
            headers={**admin_auth_header, "Content-Type": "application/json"},
        )
        assert resp.status_code == 422

    async def test_validation_error_has_code_field(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.post(
            "/api/users",
            json={"username": "x"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 422
        body = resp.json()
        assert "code" in body
        assert body["code"] == "VALIDATION_ERROR"

    async def test_validation_error_has_details(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.post(
            "/api/roles",
            json={"scope": "ADMIN"},
            headers=admin_auth_header,
        )
        assert resp.status_code == 422
        body = resp.json()
        assert "details" in body
        assert isinstance(body["details"], list)


@pytest.mark.asyncio
class TestNotFoundHandling:
    async def test_not_found_from_service(self, app_client: AsyncClient, admin_auth_header, mock_user_query_service):
        mock_user_query_service.get_by_id.side_effect = NotFoundException(
            "errors.business.user.not_found", params={"id": str(DEFAULT_USER_ID)}
        )
        resp = await app_client.get(
            f"/api/users/{DEFAULT_USER_ID}",
            headers=admin_auth_header,
        )
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == "NOT_FOUND"


@pytest.mark.asyncio
class TestBusinessViolationHandling:
    async def test_business_violation_returns_400(
        self, app_client: AsyncClient, admin_auth_header, mock_user_domain_service
    ):
        mock_user_domain_service.create.side_effect = BusinessViolationException(
            "errors.business.user.username_taken", params={"username": "x"}
        )
        resp = await app_client.post(
            "/api/users",
            json={
                "username": "x",
                "password": "Strong1!pass",
                "email": "x@example.com",
                "first_name": "X",
                "last_name": None,
            },
            headers=admin_auth_header,
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["code"] == "BUSINESS_VIOLATION"


@pytest.mark.asyncio
class TestHttpExceptionHandling:
    async def test_404_for_unknown_route(self, app_client: AsyncClient):
        resp = await app_client.get("/api/nonexistent")
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == "NOT_FOUND"

    async def test_405_method_not_allowed(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.patch("/api/users", headers=admin_auth_header)
        assert resp.status_code in (404, 405)


@pytest.mark.asyncio
class TestErrorEnvelopeStructure:
    async def test_error_envelope_has_required_fields(self, app_client: AsyncClient, admin_auth_header):
        resp = await app_client.post(
            "/api/users",
            json={"username": "x"},
            headers=admin_auth_header,
        )
        body = resp.json()
        assert "code" in body
        assert "message" in body
        assert isinstance(body["message"], str)
