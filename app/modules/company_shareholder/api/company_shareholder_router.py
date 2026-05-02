from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.company_shareholder.api.dto.company_shareholder_request import CompanyShareholderSyncRequest
from app.modules.company_shareholder.api.dto.company_shareholder_response import ResponseCompanyShareholder
from app.modules.company_shareholder.company_shareholder_dependency import CompanyShareholderDomainServiceDep
from app.modules.company_shareholder.company_shareholder_query_dependency import CompanyShareholderQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["company-shareholders"])


@router.put(
    "/{stock_id}/shareholders/sync", response_model=list[ResponseCompanyShareholder], status_code=status.HTTP_200_OK
)
async def sync_company_shareholders(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_SHAREHOLDER_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    body: Annotated[CompanyShareholderSyncRequest, Body()],
    domain_service: CompanyShareholderDomainServiceDep,
) -> list[ResponseCompanyShareholder]:
    _LOG.info("API_REQUEST_COMPANY_SHAREHOLDER_SYNC", stock_id=stock_id)
    entities = await domain_service.sync_shareholders(stock_id, body.items)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyShareholder) for e in entities]


@router.get("/{stock_id}/shareholders", response_model=list[ResponseCompanyShareholder])
async def get_company_shareholders(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_SHAREHOLDER_READ, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    query_service: CompanyShareholderQueryServiceDep,
) -> list[ResponseCompanyShareholder]:
    _LOG.info("API_REQUEST_COMPANY_SHAREHOLDER_GET_BY_STOCK", stock_id=stock_id)
    entities = await query_service.find_all_by_stock_id(stock_id)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyShareholder) for e in entities]
