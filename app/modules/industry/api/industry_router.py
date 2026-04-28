from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.base_schema import PaginatedResponse, build_query_param_dependency, get_model_fields
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.industry.api.dto.industry_request import IndustryCreateRequest, IndustryUpdateRequest
from app.modules.industry.api.dto.industry_response import ResponseIndustry
from app.modules.industry.application.command.industry_command import UpdateIndustryCommand
from app.modules.industry.application.query.industry_query import IndustryFilterParameter, IndustryPaginationParameter
from app.modules.industry.industry_dependency import IndustryDomainServiceDep
from app.modules.industry.industry_query_dependency import IndustryQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/industries", tags=["industries"])

PaginationQueryParamDep = build_query_param_dependency(
    IndustryPaginationParameter,
    include_fields=get_model_fields(IndustryPaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    IndustryFilterParameter,
    exclude_fields=get_model_fields(IndustryPaginationParameter),
)


@router.post("", response_model=ResponseIndustry, status_code=status.HTTP_201_CREATED)
async def create_industry(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.INDUSTRY_CREATE, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    body: Annotated[IndustryCreateRequest, Body()],
    domain_service: IndustryDomainServiceDep,
) -> ResponseIndustry:
    _LOG.info("API_REQUEST_INDUSTRY_CREATE", command=body)
    entity = await domain_service.create(body)
    return SchemaMapper.entity_to_response(entity, ResponseIndustry)


@router.put("/{industry_id}", response_model=ResponseIndustry, status_code=status.HTTP_200_OK)
async def update_industry(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.INDUSTRY_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    industry_id: Annotated[int, Path()],
    body: Annotated[IndustryUpdateRequest, Body()],
    domain_service: IndustryDomainServiceDep,
) -> ResponseIndustry:
    _LOG.info("API_REQUEST_INDUSTRY_UPDATE", industry_id=industry_id, command=body)
    entity = await domain_service.update(UpdateIndustryCommand(id=industry_id, **body.model_dump()))
    return SchemaMapper.entity_to_response(entity, ResponseIndustry)


@router.delete("/{industry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_industry(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.INDUSTRY_DELETE, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    industry_id: Annotated[int, Path()],
    domain_service: IndustryDomainServiceDep,
) -> None:
    _LOG.info("API_REQUEST_INDUSTRY_DELETE", industry_id=industry_id)
    await domain_service.delete(industry_id)


@router.get("", response_model=PaginatedResponse[ResponseIndustry])
async def get_page_industries(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.INDUSTRY_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    filter_params: Annotated[IndustryFilterParameter, Depends(FilterQueryParamDep)],
    pagination: Annotated[IndustryPaginationParameter, Depends(PaginationQueryParamDep)],
    query_service: IndustryQueryServiceDep,
) -> PaginatedResponse[ResponseIndustry]:
    _LOG.info("API_REQUEST_INDUSTRY_PAGE", offset=pagination.offset, limit=pagination.limit)
    page = await query_service.find_page(filter_params, pagination)
    return PaginatedResponse(
        items=[SchemaMapper.entity_to_response(i, ResponseIndustry) for i in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )


@router.get("/all", response_model=list[ResponseIndustry])
async def get_all_industries(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.INDUSTRY_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    filter_params: Annotated[IndustryFilterParameter, Depends(FilterQueryParamDep)],
    query_service: IndustryQueryServiceDep,
) -> list[ResponseIndustry]:
    _LOG.info("API_REQUEST_INDUSTRY_LIST_ALL")
    industries = await query_service.find_all(filter_params)
    return [SchemaMapper.entity_to_response(i, ResponseIndustry) for i in industries]


@router.get("/{industry_id}", response_model=ResponseIndustry)
async def get_industry(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.INDUSTRY_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    industry_id: Annotated[int, Path()],
    query_service: IndustryQueryServiceDep,
) -> ResponseIndustry:
    _LOG.info("API_REQUEST_INDUSTRY_GET", industry_id=industry_id)
    entity = await query_service.get_by_id(industry_id)
    return SchemaMapper.entity_to_response(entity, ResponseIndustry)
