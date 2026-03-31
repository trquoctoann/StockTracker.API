from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.base_mapper import SchemaMapper
from app.common.base_schema import PaginatedResponse, build_query_param_dependency, get_model_fields
from app.core.logger import get_logger
from app.modules.role.api.dto.role_request import RoleCreateRequest, RoleSetPermissionsRequest, RoleUpdateRequest
from app.modules.role.api.dto.role_response import ResponseRole
from app.modules.role.application.command.role_command import SetRolePermissionsCommand, UpdateRoleCommand
from app.modules.role.application.query.role_query import RoleFilterParameter, RolePaginationParameter
from app.modules.role.application.role_query_service import RoleFetchSpec
from app.modules.role.role_dependency import RoleDomainServiceDep, RoleQueryServiceDep

logger = get_logger(__name__)

router = APIRouter(prefix="/roles", tags=["roles"])

PaginationQueryParamDep = build_query_param_dependency(
    RolePaginationParameter,
    include_fields=get_model_fields(RolePaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    RoleFilterParameter,
    exclude_fields=get_model_fields(RolePaginationParameter),
)


@router.post("", response_model=ResponseRole, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: Annotated[RoleCreateRequest, Body()],
    domain_service: RoleDomainServiceDep,
) -> ResponseRole:
    logger.info("API_REQUEST_ROLE_CREATE", command=body)
    entity = await domain_service.create(body)
    return SchemaMapper.entity_to_response(entity, ResponseRole)


@router.put("/{role_id}", response_model=ResponseRole, status_code=status.HTTP_200_OK)
async def update_role(
    role_id: Annotated[int, Path()],
    body: Annotated[RoleUpdateRequest, Body()],
    domain_service: RoleDomainServiceDep,
) -> ResponseRole:
    logger.info("API_REQUEST_ROLE_UPDATE", role_id=role_id, command=body)
    entity = await domain_service.update(UpdateRoleCommand(id=role_id, **body.model_dump()))
    return SchemaMapper.entity_to_response(entity, ResponseRole)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: Annotated[int, Path()],
    domain_service: RoleDomainServiceDep,
) -> None:
    logger.info("API_REQUEST_ROLE_DELETE", role_id=role_id)
    await domain_service.delete(role_id)


@router.get("", response_model=PaginatedResponse[ResponseRole])
async def get_page_roles(
    filter_params: Annotated[RoleFilterParameter, Depends(FilterQueryParamDep)],
    pagination: Annotated[RolePaginationParameter, Depends(PaginationQueryParamDep)],
    query_service: RoleQueryServiceDep,
) -> PaginatedResponse[ResponseRole]:
    logger.info("API_REQUEST_ROLE_PAGE", offset=pagination.offset, limit=pagination.limit)
    page = await query_service.find_page(filter_params, pagination, fetch_spec=RoleFetchSpec(permissions=True))
    return PaginatedResponse(
        items=[SchemaMapper.entity_to_response(r, ResponseRole) for r in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )


@router.get("/all", response_model=list[ResponseRole])
async def get_all_roles(
    filter_params: Annotated[RoleFilterParameter, Depends(FilterQueryParamDep)],
    query_service: RoleQueryServiceDep,
) -> list[ResponseRole]:
    logger.info("API_REQUEST_ROLE_LIST_ALL", filter_params=filter_params)
    roles = await query_service.find_all(filter_params)
    return [SchemaMapper.entity_to_response(r, ResponseRole) for r in roles]


@router.get("/{role_id}", response_model=ResponseRole)
async def get_role(
    role_id: Annotated[int, Path()],
    query_service: RoleQueryServiceDep,
) -> ResponseRole:
    logger.info("API_REQUEST_ROLE_GET", role_id=role_id)
    entity = await query_service.get_by_id(role_id, fetch_spec=RoleFetchSpec(permissions=True))
    return SchemaMapper.entity_to_response(entity, ResponseRole)


@router.put("/{role_id}/permissions", response_model=ResponseRole, status_code=status.HTTP_200_OK)
async def set_role_permissions(
    role_id: Annotated[int, Path()],
    body: Annotated[RoleSetPermissionsRequest, Body()],
    domain_service: RoleDomainServiceDep,
) -> ResponseRole:
    logger.info("API_REQUEST_ROLE_SET_PERMISSIONS", role_id=role_id, command=body)
    entity = await domain_service.set_permissions(SetRolePermissionsCommand(id=role_id, **body.model_dump()))
    return SchemaMapper.entity_to_response(entity, ResponseRole)
