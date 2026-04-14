from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.common.enum import RecordStatus
from app.modules.tenant.application.command.tenant_command import CreateTenantCommand, UpdateTenantCommand
from app.modules.tenant.application.tenant_domain_service import TenantDomainService
from tests.support.factories import make_tenant
from tests.support.fakes import make_mock_async_session


@pytest.fixture()
def session():
    return make_mock_async_session()


@pytest.fixture()
def tenant_repo():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def user_domain_service():
    return AsyncMock()


@pytest.fixture()
def service(session, tenant_repo, query_service, user_domain_service):
    return TenantDomainService(
        session=session,
        tenant_repository=tenant_repo,
        query_service=query_service,
        user_domain_service=user_domain_service,
    )


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_root_tenant(self, service, tenant_repo):
        created = make_tenant(id=10)
        tenant_repo.bulk_create.return_value = [created]
        tenant_repo.bulk_update.return_value = [make_tenant(id=10, path="10.")]

        cmd = CreateTenantCommand(name="Root Tenant")
        result = await service.create(cmd)
        assert result.id == 10
        tenant_repo.bulk_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_child_tenant(self, service, tenant_repo, query_service):
        parent = make_tenant(id=1, path="1.")
        query_service.get_by_id.return_value = parent

        child = make_tenant(id=5, parent_tenant_id=1)
        tenant_repo.bulk_create.return_value = [child]
        tenant_repo.bulk_update.return_value = [make_tenant(id=5, path="1.5.", parent_tenant_id=1)]

        cmd = CreateTenantCommand(name="Child", parent_tenant_id=1)
        await service.create(cmd)
        tenant_repo.bulk_create.assert_called_once()


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_tenant(self, service, tenant_repo, query_service):
        existing = make_tenant()
        query_service.get_by_id.return_value = existing
        updated = make_tenant(name="Renamed")
        tenant_repo.bulk_update.return_value = [updated]

        cmd = UpdateTenantCommand(id=1, name="Renamed")
        result = await service.update(cmd)
        assert result.name == "Renamed"


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_soft_deletes_and_cleans_user_roles(
        self, service, tenant_repo, query_service, user_domain_service
    ):
        existing = make_tenant()
        query_service.get_by_id.return_value = existing
        tenant_repo.bulk_update.return_value = [existing]

        await service.delete(1)
        saved = tenant_repo.bulk_update.call_args[0][0][0]
        assert saved.record_status == RecordStatus.DELETED
        user_domain_service.delete_user_roles_for_soft_deleted_tenant.assert_called_once_with(1)
