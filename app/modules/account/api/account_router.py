from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from app.common.auth.auth_access import get_authenticated_principal
from app.common.base_mapper import SchemaMapper
from app.common.current_user import CurrentUserServiceDep
from app.core.logger import get_logger
from app.modules.account.account_dependency import AccountDomainServiceDep, AccountQueryServiceDep
from app.modules.account.api.dto.account_request import (
    AccountSwitchContextRequest,
    AccountUpdatePasswordRequest,
    AccountUpdateProfileRequest,
)
from app.modules.account.api.dto.account_response import AccountSwitchContextResponse
from app.modules.user.api.dto.user_response import ResponseUser

_LOG = get_logger(__name__)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=ResponseUser, status_code=status.HTTP_200_OK)
async def get_my_profile(
    _auth: Annotated[object, Depends(get_authenticated_principal)],
    current_user_service: CurrentUserServiceDep,
    query_service: AccountQueryServiceDep,
) -> ResponseUser:
    current_user = await current_user_service.get_current_user()
    _LOG.info("API_REQUEST_ACCOUNT_GET", user_id=current_user.id)
    me = await query_service.get_me(current_user)
    return SchemaMapper.entity_to_response(me, ResponseUser)


@router.put("/profile", response_model=ResponseUser, status_code=status.HTTP_200_OK)
async def update_my_profile(
    _auth: Annotated[object, Depends(get_authenticated_principal)],
    body: Annotated[AccountUpdateProfileRequest, Body()],
    current_user_service: CurrentUserServiceDep,
    domain_service: AccountDomainServiceDep,
) -> ResponseUser:
    current_user = await current_user_service.get_current_user()
    _LOG.info("API_REQUEST_ACCOUNT_UPDATE_PROFILE", user_id=current_user.id)
    updated = await domain_service.update_profile(current_user, first_name=body.first_name, last_name=body.last_name)
    return SchemaMapper.entity_to_response(updated, ResponseUser)


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_password(
    _auth: Annotated[object, Depends(get_authenticated_principal)],
    body: Annotated[AccountUpdatePasswordRequest, Body()],
    current_user_service: CurrentUserServiceDep,
    domain_service: AccountDomainServiceDep,
) -> None:
    current_user = await current_user_service.get_current_user()
    _LOG.info("API_REQUEST_ACCOUNT_UPDATE_PASSWORD", user_id=current_user.id)
    await domain_service.update_password(current_user, new_password=body.new_password)


@router.post("/switch-context", status_code=status.HTTP_200_OK)
async def switch_context(
    _auth: Annotated[object, Depends(get_authenticated_principal)],
    body: Annotated[AccountSwitchContextRequest, Body()],
    current_user_service: CurrentUserServiceDep,
    domain_service: AccountDomainServiceDep,
) -> AccountSwitchContextResponse:
    current_user = await current_user_service.get_current_user()
    _LOG.info(
        "API_REQUEST_ACCOUNT_SWITCH_CONTEXT",
        user_id=current_user.id,
        scope=body.scope.value,
        tenant_id=body.tenant_id,
    )
    access_token, expires_in = await domain_service.switch_context(
        user_id=current_user.id, scope=body.scope, tenant_id=body.tenant_id
    )
    return AccountSwitchContextResponse(
        token_type="Bearer",
        access_token=access_token,
        expires_in=expires_in,
        scope=body.scope,
        tenant_id=body.tenant_id,
    )
