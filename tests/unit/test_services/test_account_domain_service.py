from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.common.auth.context_token_codec import ContextTokenCodecImpl
from app.common.enum import RoleScope
from app.exception.exception import BusinessViolationException, ForbiddenException
from app.modules.account.application.account_domain_service import AccountDomainService
from app.modules.account.application.account_query_service import AccountQueryService
from tests.support.factories import DEFAULT_USER_ID, make_permission, make_role, make_user, make_user_role


@pytest.fixture()
def user_domain_service():
    return AsyncMock()


@pytest.fixture()
def user_query_service():
    return AsyncMock()


@pytest.fixture()
def role_query_service():
    return AsyncMock()


@pytest.fixture()
def context_codec():
    return ContextTokenCodecImpl()


@pytest.fixture()
def service(user_domain_service, user_query_service, role_query_service, context_codec):
    return AccountDomainService(
        user_domain_service=user_domain_service,
        user_query_service=user_query_service,
        role_query_service=role_query_service,
        context_token_codec=context_codec,
    )


class TestUpdateProfile:
    @pytest.mark.asyncio
    async def test_delegates_to_user_domain_service(self, service, user_domain_service):
        current_user = make_user()
        user_domain_service.update_profile.return_value = make_user(first_name="New")

        result = await service.update_profile(current_user, first_name="New", last_name=None)
        user_domain_service.update_profile.assert_called_once_with(current_user.id, first_name="New", last_name=None)
        assert result.first_name == "New"


class TestUpdatePassword:
    @pytest.mark.asyncio
    async def test_delegates_to_user_domain_service(self, service, user_domain_service):
        current_user = make_user()
        await service.update_password(current_user, new_password="NewStr0ng!")
        user_domain_service.update_password.assert_called_once_with(current_user.id, new_password="NewStr0ng!")


class TestSwitchContext:
    @pytest.mark.asyncio
    async def test_admin_scope_returns_token(self, service, user_query_service, role_query_service):
        user = make_user(user_roles=[make_user_role(scope=RoleScope.ADMIN, role_ids=[1])])
        user_query_service.get_by_id.return_value = user
        role_query_service.find_all_by_ids.return_value = [
            make_role(id=1, scope=RoleScope.ADMIN, permissions=[make_permission()]),
        ]

        token, ttl = await service.switch_context(user_id=DEFAULT_USER_ID, scope=RoleScope.ADMIN, tenant_id=None)
        assert isinstance(token, str)
        assert ttl > 0

    @pytest.mark.asyncio
    async def test_tenant_scope_without_tenant_id_raises(self, service):
        with pytest.raises(BusinessViolationException):
            await service.switch_context(user_id=DEFAULT_USER_ID, scope=RoleScope.TENANT, tenant_id=None)

    @pytest.mark.asyncio
    async def test_admin_scope_with_tenant_id_raises(self, service):
        with pytest.raises(BusinessViolationException):
            await service.switch_context(user_id=DEFAULT_USER_ID, scope=RoleScope.ADMIN, tenant_id=1)

    @pytest.mark.asyncio
    async def test_no_matching_user_role_raises_forbidden(self, service, user_query_service):
        user_query_service.get_by_id.return_value = make_user(user_roles=[])
        with pytest.raises(ForbiddenException):
            await service.switch_context(user_id=DEFAULT_USER_ID, scope=RoleScope.ADMIN, tenant_id=None)

    @pytest.mark.asyncio
    async def test_no_roles_found_raises_forbidden(self, service, user_query_service, role_query_service):
        user_query_service.get_by_id.return_value = make_user(
            user_roles=[make_user_role(scope=RoleScope.ADMIN, role_ids=[1])]
        )
        role_query_service.find_all_by_ids.return_value = []
        with pytest.raises(ForbiddenException):
            await service.switch_context(user_id=DEFAULT_USER_ID, scope=RoleScope.ADMIN, tenant_id=None)


class TestAccountQueryService:
    @pytest.mark.asyncio
    async def test_get_me_returns_current_user(self):
        svc = AccountQueryService()
        user = make_user()
        result = await svc.get_me(user)
        assert result is user
