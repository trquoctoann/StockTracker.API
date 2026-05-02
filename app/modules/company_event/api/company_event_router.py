from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.company_event.api.dto.company_event_request import CompanyEventSyncRequest
from app.modules.company_event.api.dto.company_event_response import ResponseCompanyEvent
from app.modules.company_event.company_event_dependency import CompanyEventDomainServiceDep
from app.modules.company_event.company_event_query_dependency import CompanyEventQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["company-events"])


@router.put("/{stock_id}/events/sync", response_model=list[ResponseCompanyEvent], status_code=status.HTTP_200_OK)
async def sync_company_events(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.COMPANY_EVENT_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    body: Annotated[CompanyEventSyncRequest, Body()],
    domain_service: CompanyEventDomainServiceDep,
) -> list[ResponseCompanyEvent]:
    _LOG.info("API_REQUEST_COMPANY_EVENT_SYNC", stock_id=stock_id)
    entities = await domain_service.sync_events(stock_id, body.items)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyEvent) for e in entities]


@router.get("/{stock_id}/events", response_model=list[ResponseCompanyEvent])
async def get_company_events(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.COMPANY_EVENT_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    stock_id: Annotated[int, Path()],
    query_service: CompanyEventQueryServiceDep,
) -> list[ResponseCompanyEvent]:
    _LOG.info("API_REQUEST_COMPANY_EVENT_GET_BY_STOCK", stock_id=stock_id)
    entities = await query_service.find_all_by_stock_id(stock_id)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyEvent) for e in entities]
