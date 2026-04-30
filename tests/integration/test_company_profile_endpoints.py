from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.support.factories import make_company_profile


@pytest.mark.asyncio
class TestSyncCompanyProfile:
    async def test_sync_company_profile_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_profile_domain_service
    ):
        mock_company_profile_domain_service.upsert.return_value = make_company_profile()

        resp = await app_client.put(
            "/api/stocks/1/profile/sync",
            json={"symbol": "Test", "stock_id": 1},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetCompanyProfile:
    async def test_get_company_profile_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_profile_query_service
    ):
        mock_company_profile_query_service.find_by_stock_id.return_value = make_company_profile()
        resp = await app_client.get(
            "/api/stocks/1/profile",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
