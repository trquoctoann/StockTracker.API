from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.base_schema import PaginatedResponse, build_query_param_dependency, get_model_fields
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.stock_intraday.api.dto.stock_intraday_request import StockIntradaySyncRequest
from app.modules.stock_intraday.api.dto.stock_intraday_response import ResponseStockIntraday
from app.modules.stock_intraday.application.query.stock_intraday_query import (
    StockIntradayFilterParameter,
    StockIntradayPaginationParameter,
)
from app.modules.stock_intraday.stock_intraday_dependency import StockIntradayDomainServiceDep
from app.modules.stock_intraday.stock_intraday_query_dependency import StockIntradayQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["stock-intraday"])

PaginationQueryParamDep = build_query_param_dependency(
    StockIntradayPaginationParameter,
    include_fields=get_model_fields(StockIntradayPaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    StockIntradayFilterParameter,
    exclude_fields=get_model_fields(StockIntradayPaginationParameter),
)


@router.put(
    "/{stock_id}/intraday/sync",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def sync_stock_intraday(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.STOCK_INTRADAY_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    body: Annotated[list[StockIntradaySyncRequest], Body()],
    domain_service: StockIntradayDomainServiceDep,
) -> dict:
    _LOG.info("API_REQUEST_STOCK_INTRADAY_SYNC", stock_id=stock_id, count=len(body))
    count = await domain_service.sync_intraday(stock_id, body)
    return {"synced": count}


@router.get(
    "/{stock_id}/intraday",
    response_model=PaginatedResponse[ResponseStockIntraday],
)
async def list_stock_intraday(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.STOCK_INTRADAY_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    stock_id: Annotated[int, Path()],
    query_service: StockIntradayQueryServiceDep,
    filter_params: Annotated[StockIntradayFilterParameter, Depends(FilterQueryParamDep)],
    pagination_params: Annotated[StockIntradayPaginationParameter, Depends(PaginationQueryParamDep)],
) -> PaginatedResponse[ResponseStockIntraday]:
    _LOG.info("API_REQUEST_STOCK_INTRADAY_LIST", stock_id=stock_id)
    merged_filter = StockIntradayFilterParameter.merge_ops(filter_params, eq={"stock_id": stock_id})
    page = await query_service.find_page(merged_filter, pagination_params)
    return PaginatedResponse[ResponseStockIntraday](
        items=[SchemaMapper.entity_to_response(e, ResponseStockIntraday) for e in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )
