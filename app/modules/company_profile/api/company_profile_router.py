from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.base_schema import build_query_param_dependency, get_model_fields
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.company_profile.api.dto.company_profile_request import CompanyProfileSyncRequest
from app.modules.company_profile.api.dto.company_profile_response import ResponseCompanyProfile
from app.modules.company_profile.application.query.company_profile_query import (
    CompanyProfileFilterParameter,
    CompanyProfilePaginationParameter,
)
from app.modules.company_profile.company_profile_dependency import CompanyProfileDomainServiceDep
from app.modules.company_profile.company_profile_query_dependency import CompanyProfileQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["company-profiles"])

PaginationQueryParamDep = build_query_param_dependency(
    CompanyProfilePaginationParameter,
    include_fields=get_model_fields(CompanyProfilePaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    CompanyProfileFilterParameter,
    exclude_fields=get_model_fields(CompanyProfilePaginationParameter),
)


@router.put("/{stock_id}/profile/sync", response_model=ResponseCompanyProfile, status_code=status.HTTP_200_OK)
async def sync_company_profile(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_PROFILE_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    body: Annotated[CompanyProfileSyncRequest, Body()],
    domain_service: CompanyProfileDomainServiceDep,
) -> ResponseCompanyProfile:
    _LOG.info("API_REQUEST_COMPANY_PROFILE_SYNC", stock_id=stock_id)
    body.stock_id = stock_id
    entity = await domain_service.upsert(body)
    return SchemaMapper.entity_to_response(entity, ResponseCompanyProfile)


@router.get("/{stock_id}/profile", response_model=ResponseCompanyProfile | None)
async def get_company_profile(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_PROFILE_READ, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    query_service: CompanyProfileQueryServiceDep,
) -> ResponseCompanyProfile | None:
    _LOG.info("API_REQUEST_COMPANY_PROFILE_GET", stock_id=stock_id)
    entity = await query_service.find_by_stock_id(stock_id)
    if not entity:
        return None
    return SchemaMapper.entity_to_response(entity, ResponseCompanyProfile)
