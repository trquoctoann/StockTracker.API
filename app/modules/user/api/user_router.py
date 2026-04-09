from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.base_schema import PaginatedResponse, build_query_param_dependency, get_model_fields
from app.core.logger import get_logger
from app.modules.user.api.dto.user_request import UserCreateRequest, UserSetRolesRequest, UserUpdateRequest
from app.modules.user.api.dto.user_response import ResponseUser
from app.modules.user.application.command.user_command import SetUserRolesCommand, UpdateUserCommand
from app.modules.user.application.query.user_query import UserFilterParameter, UserPaginationParameter
from app.modules.user.application.user_query_service import UserFetchSpec
from app.modules.user.user_dependency import UserDomainServiceDep
from app.modules.user.user_query_dependency import UserQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

PaginationQueryParamDep = build_query_param_dependency(
    UserPaginationParameter,
    include_fields=get_model_fields(UserPaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    UserFilterParameter,
    exclude_fields=get_model_fields(UserPaginationParameter),
)


@router.post("", response_model=ResponseUser, status_code=status.HTTP_201_CREATED)
async def create_user(
    _auth: Annotated[object, Depends(require_context_permissions(PermissionCode.USER_CREATE))],
    body: Annotated[UserCreateRequest, Body()],
    domain_service: UserDomainServiceDep,
) -> ResponseUser:
    _LOG.info("API_REQUEST_USER_CREATE", command=body)
    entity = await domain_service.create(body)
    return SchemaMapper.entity_to_response(entity, ResponseUser)


@router.put("/{user_id}", response_model=ResponseUser, status_code=status.HTTP_200_OK)
async def update_user(
    _auth: Annotated[object, Depends(require_context_permissions(PermissionCode.USER_UPDATE))],
    user_id: Annotated[UUID, Path()],
    body: Annotated[UserUpdateRequest, Body()],
    domain_service: UserDomainServiceDep,
) -> ResponseUser:
    _LOG.info("API_REQUEST_USER_UPDATE", command=body)
    entity = await domain_service.update(UpdateUserCommand(id=user_id, **body.model_dump()))
    return SchemaMapper.entity_to_response(entity, ResponseUser)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    _auth: Annotated[object, Depends(require_context_permissions(PermissionCode.USER_DELETE))],
    user_id: Annotated[UUID, Path()],
    domain_service: UserDomainServiceDep,
) -> None:
    _LOG.info("API_REQUEST_USER_DELETE", id=user_id)
    await domain_service.delete(user_id)


@router.get("", response_model=PaginatedResponse[ResponseUser])
async def get_page_users(
    _auth: Annotated[object, Depends(require_context_permissions(PermissionCode.USER_READ))],
    filter_params: Annotated[UserFilterParameter, Depends(FilterQueryParamDep)],
    pagination: Annotated[UserPaginationParameter, Depends(PaginationQueryParamDep)],
    query_service: UserQueryServiceDep,
) -> PaginatedResponse[ResponseUser]:
    _LOG.info(
        "API_REQUEST_USER_PAGE",
        offset=pagination.offset,
        limit=pagination.limit,
    )
    page = await query_service.find_page(filter_params, pagination, fetch_spec=UserFetchSpec(user_roles=True))
    return PaginatedResponse(
        items=[SchemaMapper.entity_to_response(u, ResponseUser) for u in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )


@router.get("/all", response_model=list[ResponseUser])
async def get_all_users(
    _auth: Annotated[object, Depends(require_context_permissions(PermissionCode.USER_READ))],
    filter_params: Annotated[UserFilterParameter, Depends(FilterQueryParamDep)],
    query_service: UserQueryServiceDep,
) -> list[ResponseUser]:
    _LOG.info("API_REQUEST_USER_LIST_ALL", filter_params=filter_params)
    users = await query_service.find_all(filter_params)
    return [SchemaMapper.entity_to_response(u, ResponseUser) for u in users]


@router.get("/{user_id}", response_model=ResponseUser)
async def get_user(
    _auth: Annotated[object, Depends(require_context_permissions(PermissionCode.USER_READ))],
    user_id: Annotated[UUID, Path()],
    query_service: UserQueryServiceDep,
) -> ResponseUser:
    _LOG.info("API_REQUEST_USER_GET", id=user_id)
    entity = await query_service.get_by_id(user_id, fetch_spec=UserFetchSpec(user_roles=True))
    return SchemaMapper.entity_to_response(entity, ResponseUser)


@router.put("/{user_id}/roles", response_model=ResponseUser, status_code=status.HTTP_200_OK)
async def set_user_roles(
    _auth: Annotated[object, Depends(require_context_permissions(PermissionCode.USER_MANAGE_ROLES))],
    user_id: Annotated[UUID, Path()],
    body: Annotated[UserSetRolesRequest, Body()],
    domain_service: UserDomainServiceDep,
) -> ResponseUser:
    _LOG.info("API_REQUEST_USER_SET_ROLES", id=user_id, command=body)
    entity = await domain_service.set_roles(SetUserRolesCommand(id=user_id, **body.model_dump(exclude={"id"})))
    return SchemaMapper.entity_to_response(entity, ResponseUser)
