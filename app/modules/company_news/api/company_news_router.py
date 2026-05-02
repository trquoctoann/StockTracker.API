from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.company_news.api.dto.company_news_request import CompanyNewsSyncRequest
from app.modules.company_news.api.dto.company_news_response import ResponseCompanyNews
from app.modules.company_news.company_news_dependency import CompanyNewsDomainServiceDep
from app.modules.company_news.company_news_query_dependency import CompanyNewsQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["company-news"])


@router.put("/{stock_id}/news/sync", response_model=list[ResponseCompanyNews], status_code=status.HTTP_200_OK)
async def sync_company_news(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.COMPANY_NEWS_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    stock_id: Annotated[int, Path()],
    body: Annotated[CompanyNewsSyncRequest, Body()],
    domain_service: CompanyNewsDomainServiceDep,
) -> list[ResponseCompanyNews]:
    _LOG.info("API_REQUEST_COMPANY_NEWS_SYNC", stock_id=stock_id)
    entities = await domain_service.sync_news(stock_id, body.items)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyNews) for e in entities]


@router.get("/{stock_id}/news", response_model=list[ResponseCompanyNews])
async def get_company_news(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.COMPANY_NEWS_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    stock_id: Annotated[int, Path()],
    query_service: CompanyNewsQueryServiceDep,
) -> list[ResponseCompanyNews]:
    _LOG.info("API_REQUEST_COMPANY_NEWS_GET_BY_STOCK", stock_id=stock_id)
    entities = await query_service.find_all_by_stock_id(stock_id)
    return [SchemaMapper.entity_to_response(e, ResponseCompanyNews) for e in entities]
