from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.support.factories import make_company_event


@pytest.mark.asyncio
class TestSyncCompanyEvent:
    async def test_sync_company_event_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_event_domain_service
    ):
        mock_company_event_domain_service.sync_events.return_value = [make_company_event()]

        resp = await app_client.put(
            "/api/stocks/1/events/sync",
            json={"items": [{"title": "Test"}]},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetCompanyEvent:
    async def test_get_company_event_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_event_query_service
    ):
        mock_company_event_query_service.find_all.return_value = [make_company_event()]
        resp = await app_client.get(
            "/api/stocks/1/events",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
