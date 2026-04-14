import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health_returns_200(self, app_client: AsyncClient):
        resp = await app_client.get("/health")
        assert resp.status_code == 200

    async def test_health_response_body(self, app_client: AsyncClient):
        resp = await app_client.get("/health")
        body = resp.json()
        assert body == {"status": "ok"}

    async def test_health_no_auth_required(self, app_client: AsyncClient):
        resp = await app_client.get("/health")
        assert resp.status_code == 200
