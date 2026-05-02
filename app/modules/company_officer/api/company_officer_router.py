from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.company_officer.api.dto.company_officer_request import CompanyOfficerSyncRequest
from app.modules.company_officer.api.dto.company_officer_response import ResponseCompanyOfficer
from app.modules.company_officer.company_officer_dependency import CompanyOfficerDomainServiceDep
from app.modules.company_officer.company_officer_query_dependency import CompanyOfficerQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["company-officers"])


@router.put("/{stock_id}/officers/sync", response_model=list[ResponseCompanyOfficer], status_code=status.HTTP_200_OK)
async def sync_company_officers(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_OFFICER_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    body: Annotated[CompanyOfficerSyncRequest, Body()],
    domain_service: CompanyOfficerDomainServiceDep,
) -> list[ResponseCompanyOfficer]:
    _LOG.info("API_REQUEST_COMPANY_OFFICER_SYNC", stock_id=stock_id)
    entities = await domain_service.sync_officers(stock_id, body.items)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyOfficer) for e in entities]


@router.get("/{stock_id}/officers", response_model=list[ResponseCompanyOfficer])
async def get_company_officers(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_OFFICER_READ, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    query_service: CompanyOfficerQueryServiceDep,
) -> list[ResponseCompanyOfficer]:
    _LOG.info("API_REQUEST_COMPANY_OFFICER_GET_BY_STOCK", stock_id=stock_id)
    entities = await query_service.find_all_by_stock_id(stock_id)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyOfficer) for e in entities]
