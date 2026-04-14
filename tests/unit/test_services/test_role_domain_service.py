from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.common.enum import RecordStatus, RoleScope
from app.exception.exception import BusinessViolationException
from app.modules.role.application.command.role_command import (
    CreateRoleCommand,
    SetRolePermissionsCommand,
    UpdateRoleCommand,
)
from app.modules.role.application.role_domain_service import RoleDomainService
from tests.support.factories import make_permission, make_role
from tests.support.fakes import FakeCacheService, make_mock_async_session


@pytest.fixture()
def session():
    return make_mock_async_session()


@pytest.fixture()
def role_repo():
    return AsyncMock()


@pytest.fixture()
def role_perm_repo():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def permission_query_service():
    return AsyncMock()


@pytest.fixture()
def user_domain_service():
    return AsyncMock()


@pytest.fixture()
def cache():
    return FakeCacheService()


@pytest.fixture()
def service(session, role_repo, role_perm_repo, query_service, permission_query_service, user_domain_service, cache):
    return RoleDomainService(
        session=session,
        role_repository=role_repo,
        role_permission_repository=role_perm_repo,
        query_service=query_service,
        permission_query_service=permission_query_service,
        user_domain_service=user_domain_service,
        cache=cache,
    )


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_role_without_permissions(self, service, role_repo):
        created = make_role(id=1)
        role_repo.bulk_create.return_value = [created]

        cmd = CreateRoleCommand(scope=RoleScope.ADMIN, name="Test Role")
        result = await service.create(cmd)
        assert result.name == created.name
        role_repo.bulk_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_role_with_permissions(
        self, service, role_repo, role_perm_repo, query_service, permission_query_service
    ):
        created = make_role(id=1)
        role_repo.bulk_create.return_value = [created]
        query_service.get_by_id.return_value = created
        permission_query_service.find_all_by_ids.return_value = [
            make_permission(id=1, scope=RoleScope.ADMIN),
        ]

        cmd = CreateRoleCommand(scope=RoleScope.ADMIN, name="Test Role", permission_ids={1})
        result = await service.create(cmd)
        assert result.id == 1
        role_perm_repo.delete_by_role_id.assert_called_once()
        role_perm_repo.create_many_for_role.assert_called_once()


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_role_name(self, service, role_repo, query_service):
        existing = make_role(permissions=[])
        query_service.get_by_id.return_value = existing
        role_repo.bulk_update.return_value = [make_role(name="Renamed")]

        cmd = UpdateRoleCommand(id=1, scope=RoleScope.ADMIN, name="Renamed")
        result = await service.update(cmd)
        assert result.name == "Renamed"

    @pytest.mark.asyncio
    async def test_update_with_changed_permissions_increments_version(
        self, service, role_repo, query_service, role_perm_repo, permission_query_service
    ):
        existing = make_role(permissions=[make_permission(id=1)])
        query_service.get_by_id.return_value = existing
        permission_query_service.find_all_by_ids.return_value = [make_permission(id=2, scope=RoleScope.ADMIN)]
        role_repo.bulk_update.return_value = [make_role(version=2)]

        cmd = UpdateRoleCommand(id=1, scope=RoleScope.ADMIN, name="Test", permission_ids={2})
        result = await service.update(cmd)
        assert result.version == 2
        role_repo.bulk_update.assert_called_once()


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_soft_deletes_and_cleans_assignments(
        self, service, role_repo, query_service, user_domain_service
    ):
        existing = make_role()
        query_service.get_by_id.return_value = existing
        role_repo.bulk_update.return_value = [existing]

        await service.delete(1)
        role_repo.bulk_update.assert_called_once()
        saved = role_repo.bulk_update.call_args[0][0][0]
        assert saved.record_status == RecordStatus.DELETED
        user_domain_service.remove_soft_deleted_role_from_user_assignments.assert_called_once_with(1)


class TestSetPermissions:
    @pytest.mark.asyncio
    async def test_set_permissions_no_change(self, service, query_service, role_repo):
        existing = make_role(permissions=[make_permission(id=1)])
        query_service.get_by_id.return_value = existing

        cmd = SetRolePermissionsCommand(id=1, permission_ids={1})
        result = await service.set_permissions(cmd)
        assert result == existing
        role_repo.bulk_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_permissions_scope_mismatch_raises(
        self, service, query_service, role_perm_repo, permission_query_service
    ):
        existing = make_role(scope=RoleScope.ADMIN, permissions=[])
        query_service.get_by_id.return_value = existing
        role_perm_repo.find_all_by_role_ids = AsyncMock(return_value=[])
        permission_query_service.find_all_by_ids.return_value = [
            make_permission(id=10, scope=RoleScope.TENANT, code="TENANT_READ"),
        ]

        cmd = SetRolePermissionsCommand(id=1, permission_ids={10})
        with pytest.raises(BusinessViolationException):
            await service.set_permissions(cmd)
