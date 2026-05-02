from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.company_affiliation.api.dto.company_affiliation_request import CompanyAffiliationSyncRequest
from app.modules.company_affiliation.api.dto.company_affiliation_response import ResponseCompanyAffiliation
from app.modules.company_affiliation.company_affiliation_dependency import CompanyAffiliationDomainServiceDep
from app.modules.company_affiliation.company_affiliation_query_dependency import CompanyAffiliationQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["company-affiliations"])


@router.put(
    "/{stock_id}/affiliations/sync", response_model=list[ResponseCompanyAffiliation], status_code=status.HTTP_200_OK
)
async def sync_company_affiliations(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_AFFILIATION_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    body: Annotated[CompanyAffiliationSyncRequest, Body()],
    domain_service: CompanyAffiliationDomainServiceDep,
) -> list[ResponseCompanyAffiliation]:
    _LOG.info("API_REQUEST_COMPANY_AFFILIATION_SYNC", stock_id=stock_id)
    entities = await domain_service.sync_affiliations(stock_id, body.items)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyAffiliation) for e in entities]


@router.get("/{stock_id}/affiliations", response_model=list[ResponseCompanyAffiliation])
async def get_company_affiliations(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_AFFILIATION_READ, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    query_service: CompanyAffiliationQueryServiceDep,
) -> list[ResponseCompanyAffiliation]:
    _LOG.info("API_REQUEST_COMPANY_AFFILIATION_GET_BY_STOCK", stock_id=stock_id)
    entities = await query_service.find_all_by_stock_id(stock_id)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyAffiliation) for e in entities]
