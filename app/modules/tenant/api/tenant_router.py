from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.base_schema import PaginatedResponse, build_query_param_dependency, get_model_fields
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.tenant.api.dto.tenant_request import TenantCreateRequest, TenantUpdateRequest
from app.modules.tenant.api.dto.tenant_response import ResponseTenant
from app.modules.tenant.application.command.tenant_command import UpdateTenantCommand
from app.modules.tenant.application.query.tenant_query import TenantFilterParameter, TenantPaginationParameter
from app.modules.tenant.application.tenant_query_service import TenantFetchSpec
from app.modules.tenant.tenant_dependency import TenantDomainServiceDep
from app.modules.tenant.tenant_query_dependency import TenantQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/tenants", tags=["tenants"])

PaginationQueryParamDep = build_query_param_dependency(
    TenantPaginationParameter,
    include_fields=get_model_fields(TenantPaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    TenantFilterParameter,
    exclude_fields=get_model_fields(TenantPaginationParameter),
)


@router.post("", response_model=ResponseTenant, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.TENANT_CREATE, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    body: Annotated[TenantCreateRequest, Body()],
    domain_service: TenantDomainServiceDep,
) -> ResponseTenant:
    _LOG.info("API_REQUEST_TENANT_CREATE", command=body)
    entity = await domain_service.create(body)
    return SchemaMapper.entity_to_response(entity, ResponseTenant)


@router.put("/{tenant_id}", response_model=ResponseTenant, status_code=status.HTTP_200_OK)
async def update_tenant(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.TENANT_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    tenant_id: Annotated[int, Path()],
    body: Annotated[TenantUpdateRequest, Body()],
    domain_service: TenantDomainServiceDep,
) -> ResponseTenant:
    _LOG.info("API_REQUEST_TENANT_UPDATE", tenant_id=tenant_id, command=body)
    entity = await domain_service.update(UpdateTenantCommand(id=tenant_id, **body.model_dump()))
    return SchemaMapper.entity_to_response(entity, ResponseTenant)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.TENANT_DELETE, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    tenant_id: Annotated[int, Path()],
    domain_service: TenantDomainServiceDep,
) -> None:
    _LOG.info("API_REQUEST_TENANT_DELETE", tenant_id=tenant_id)
    await domain_service.delete(tenant_id)


@router.get("", response_model=PaginatedResponse[ResponseTenant])
async def get_page_tenants(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.TENANT_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    filter_params: Annotated[TenantFilterParameter, Depends(FilterQueryParamDep)],
    pagination: Annotated[TenantPaginationParameter, Depends(PaginationQueryParamDep)],
    query_service: TenantQueryServiceDep,
) -> PaginatedResponse[ResponseTenant]:
    _LOG.info("API_REQUEST_TENANT_PAGE", offset=pagination.offset, limit=pagination.limit)
    page = await query_service.find_page(
        filter_params,
        pagination,
        fetch_spec=TenantFetchSpec(parent_tenant=True),
    )
    return PaginatedResponse(
        items=[SchemaMapper.entity_to_response(t, ResponseTenant) for t in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )


@router.get("/all", response_model=list[ResponseTenant])
async def get_all_tenants(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.TENANT_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    filter_params: Annotated[TenantFilterParameter, Depends(FilterQueryParamDep)],
    query_service: TenantQueryServiceDep,
) -> list[ResponseTenant]:
    _LOG.info("API_REQUEST_TENANT_LIST_ALL", filter_params=filter_params)
    tenants = await query_service.find_all(filter_params, fetch_spec=TenantFetchSpec(parent_tenant=True))
    return [SchemaMapper.entity_to_response(t, ResponseTenant) for t in tenants]


@router.get("/{tenant_id}", response_model=ResponseTenant)
async def get_tenant(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.TENANT_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    tenant_id: Annotated[int, Path()],
    query_service: TenantQueryServiceDep,
) -> ResponseTenant:
    _LOG.info("API_REQUEST_TENANT_GET", tenant_id=tenant_id)
    entity = await query_service.get_by_id(
        tenant_id,
        fetch_spec=TenantFetchSpec(parent_tenant=True, children_tenants=True),
    )
    return SchemaMapper.entity_to_response(entity, ResponseTenant)
