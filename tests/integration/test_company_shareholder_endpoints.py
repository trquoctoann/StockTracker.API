from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.support.factories import make_company_shareholder


@pytest.mark.asyncio
class TestSyncCompanyShareholder:
    async def test_sync_company_shareholder_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_shareholder_domain_service
    ):
        mock_company_shareholder_domain_service.sync_shareholders.return_value = [make_company_shareholder()]

        resp = await app_client.put(
            "/api/stocks/1/shareholders/sync",
            json={"items": [{"name": "Test"}]},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetCompanyShareholder:
    async def test_get_company_shareholder_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_shareholder_query_service
    ):
        mock_company_shareholder_query_service.find_all.return_value = [make_company_shareholder()]
        resp = await app_client.get(
            "/api/stocks/1/shareholders",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
