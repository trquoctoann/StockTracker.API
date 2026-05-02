from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.support.factories import make_company_officer


@pytest.mark.asyncio
class TestSyncCompanyOfficer:
    async def test_sync_company_officer_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_officer_domain_service
    ):
        mock_company_officer_domain_service.sync_officers.return_value = [make_company_officer()]

        resp = await app_client.put(
            "/api/stocks/1/officers/sync",
            json={"items": [{"name": "Test"}]},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetCompanyOfficer:
    async def test_get_company_officer_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_officer_query_service
    ):
        mock_company_officer_query_service.find_all.return_value = [make_company_officer()]
        resp = await app_client.get(
            "/api/stocks/1/officers",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
