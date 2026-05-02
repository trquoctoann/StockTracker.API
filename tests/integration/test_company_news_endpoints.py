from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.support.factories import make_company_news


@pytest.mark.asyncio
class TestSyncCompanyNews:
    async def test_sync_company_news_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_news_domain_service
    ):
        mock_company_news_domain_service.sync_news.return_value = [make_company_news()]

        resp = await app_client.put(
            "/api/stocks/1/news/sync",
            json={"items": [{"title": "Test"}]},
            headers=admin_auth_header,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestGetCompanyNews:
    async def test_get_company_news_200(
        self, app_client: AsyncClient, admin_auth_header, mock_company_news_query_service
    ):
        mock_company_news_query_service.find_all.return_value = [make_company_news()]
        resp = await app_client.get(
            "/api/stocks/1/news",
            headers=admin_auth_header,
        )
        assert resp.status_code == 200
