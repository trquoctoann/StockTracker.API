from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.common.enum import RecordStatus, RoleScope
from app.exception.exception import BusinessViolationException
from app.modules.user.application.command.user_command import CreateUserCommand, SetUserRolesCommand, UpdateUserCommand
from app.modules.user.application.user_domain_service import UserDomainService
from tests.support.factories import DEFAULT_USER_ID, make_role, make_user, make_user_role
from tests.support.fakes import FakeCacheService, FakeIdentityProvider, make_mock_async_session


@pytest.fixture()
def user_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture()
def user_role_repo():
    return AsyncMock()


@pytest.fixture()
def query_service():
    return AsyncMock()


@pytest.fixture()
def tenant_query_service():
    return AsyncMock()


@pytest.fixture()
def role_query_service():
    return AsyncMock()


@pytest.fixture()
def identity_provider():
    return FakeIdentityProvider(fixed_user_id=str(DEFAULT_USER_ID))


@pytest.fixture()
def cache():
    return FakeCacheService()


@pytest.fixture()
def session():
    return make_mock_async_session()


@pytest.fixture()
def service(
    session,
    user_repo,
    user_role_repo,
    query_service,
    tenant_query_service,
    role_query_service,
    identity_provider,
    cache,
):
    return UserDomainService(
        session=session,
        user_repository=user_repo,
        user_role_repository=user_role_repo,
        query_service=query_service,
        tenant_query_service=tenant_query_service,
        role_query_service=role_query_service,
        identity_provider=identity_provider,
        cache=cache,
    )


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_returns_entity(self, service, user_repo, query_service):
        query_service.username_exists.return_value = False
        query_service.email_exists.return_value = False

        created = make_user()
        user_repo.bulk_create.return_value = [created]

        cmd = CreateUserCommand(
            username="newuser",
            password="Strong1!pass",
            email="new@example.com",
            first_name="New",
            last_name="User",
        )
        result = await service.create(cmd)
        assert result.username == created.username
        user_repo.bulk_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_duplicate_username_raises(self, service, query_service):
        query_service.username_exists.return_value = True
        query_service.email_exists.return_value = False

        cmd = CreateUserCommand(
            username="taken",
            password="Strong1!pass",
            email="ok@example.com",
            first_name="First",
            last_name=None,
        )
        with pytest.raises(BusinessViolationException):
            await service.create(cmd)

    @pytest.mark.asyncio
    async def test_create_duplicate_email_raises(self, service, query_service):
        query_service.username_exists.return_value = False
        query_service.email_exists.return_value = True

        cmd = CreateUserCommand(
            username="unique",
            password="Strong1!pass",
            email="taken@example.com",
            first_name="First",
            last_name=None,
        )
        with pytest.raises(BusinessViolationException):
            await service.create(cmd)


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_returns_saved_entity(self, service, user_repo, query_service):
        existing = make_user()
        query_service.get_by_id.return_value = existing

        updated = make_user(first_name="Updated")
        user_repo.bulk_update.return_value = [updated]

        cmd = UpdateUserCommand(
            id=DEFAULT_USER_ID,
            username="testuser",
            password="Strong1!pass",
            email="test@example.com",
            first_name="Updated",
            last_name="User",
        )
        result = await service.update(cmd)
        assert result.first_name == "Updated"


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_soft_deletes(self, service, user_repo, query_service):
        existing = make_user()
        query_service.get_by_id.return_value = existing
        user_repo.bulk_update.return_value = [existing]

        await service.delete(DEFAULT_USER_ID)
        user_repo.bulk_update.assert_called_once()
        saved_entity = user_repo.bulk_update.call_args[0][0][0]
        assert saved_entity.record_status == RecordStatus.DELETED


class TestSetRoles:
    @pytest.mark.asyncio
    async def test_set_roles_admin_scope(self, service, query_service, role_query_service, user_role_repo):
        make_user()
        query_service.get_by_id.return_value = make_user(user_roles=[make_user_role()])

        roles = [make_role(id=1, scope=RoleScope.ADMIN)]
        role_query_service.find_all_by_ids.return_value = roles

        cmd = SetUserRolesCommand(id=DEFAULT_USER_ID, role_ids={1})
        await service.set_roles(cmd)
        user_role_repo.upsert_user_roles.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_roles_tenant_scope(
        self, service, query_service, tenant_query_service, role_query_service, user_role_repo
    ):
        query_service.get_by_id.return_value = make_user(
            user_roles=[make_user_role(scope=RoleScope.TENANT, tenant_id=1)]
        )
        tenant_query_service.get_by_id.return_value = True
        role_query_service.find_all_by_ids.return_value = [make_role(id=1, scope=RoleScope.TENANT)]

        cmd = SetUserRolesCommand(id=DEFAULT_USER_ID, tenant_id=1, role_ids={1})
        await service.set_roles(cmd)
        user_role_repo.upsert_user_roles.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_roles_missing_role_raises(self, service, query_service, role_query_service):
        query_service.get_by_id.return_value = make_user()
        role_query_service.find_all_by_ids.return_value = []

        cmd = SetUserRolesCommand(id=DEFAULT_USER_ID, role_ids={999})
        with pytest.raises(BusinessViolationException):
            await service.set_roles(cmd)

    @pytest.mark.asyncio
    async def test_set_roles_scope_mismatch_raises(self, service, query_service, role_query_service):
        query_service.get_by_id.return_value = make_user()
        role_query_service.find_all_by_ids.return_value = [make_role(id=1, scope=RoleScope.TENANT)]

        cmd = SetUserRolesCommand(id=DEFAULT_USER_ID, role_ids={1})
        with pytest.raises(BusinessViolationException):
            await service.set_roles(cmd)


class TestUpdateProfile:
    @pytest.mark.asyncio
    async def test_update_profile(self, service, user_repo, query_service):
        existing = make_user()
        query_service.get_by_id.return_value = existing
        user_repo.bulk_update.return_value = [make_user(first_name="NewFirst")]

        result = await service.update_profile(DEFAULT_USER_ID, first_name="NewFirst", last_name=None)
        assert result.first_name == "NewFirst"


class TestUpdatePassword:
    @pytest.mark.asyncio
    async def test_update_password(self, service, query_service):
        query_service.get_by_id.return_value = make_user()
        await service.update_password(DEFAULT_USER_ID, new_password="NewStr0ng!pass")
