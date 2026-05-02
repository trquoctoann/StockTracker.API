from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.support.factories import make_company_affiliation


@pytest.mark.asyncio
class TestSyncCompanyAffiliation:
    async def test_sync_company_affiliation_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_affiliation_domain_service
    ):
        mock_company_affiliation_domain_service.sync_affiliations.return_value = [make_company_affiliation()]

        resp = await app_client.put(
            "/api/stocks/1/affiliations/sync",
            json={"items": [{"name": "Test"}]},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetCompanyAffiliation:
    async def test_get_company_affiliation_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_affiliation_query_service
    ):
        mock_company_affiliation_query_service.find_all.return_value = [make_company_affiliation()]
        resp = await app_client.get(
            "/api/stocks/1/affiliations",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
