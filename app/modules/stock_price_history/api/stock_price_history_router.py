from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.base_schema import PaginatedResponse, build_query_param_dependency, get_model_fields
from app.common.enum import PriceInterval, RoleScope
from app.core.logger import get_logger
from app.modules.stock_price_history.api.dto.stock_price_history_request import StockPriceHistorySyncRequest
from app.modules.stock_price_history.api.dto.stock_price_history_response import ResponseStockPriceHistory
from app.modules.stock_price_history.application.query.stock_price_history_query import (
    StockPriceHistoryFilterParameter,
    StockPriceHistoryPaginationParameter,
)
from app.modules.stock_price_history.stock_price_history_dependency import StockPriceHistoryDomainServiceDep
from app.modules.stock_price_history.stock_price_history_query_dependency import StockPriceHistoryQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["stock-price-history"])

PaginationQueryParamDep = build_query_param_dependency(
    StockPriceHistoryPaginationParameter,
    include_fields=get_model_fields(StockPriceHistoryPaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    StockPriceHistoryFilterParameter,
    exclude_fields=get_model_fields(StockPriceHistoryPaginationParameter),
)


@router.put(
    "/{stock_id}/price-history/sync",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def sync_stock_price_history(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.STOCK_PRICE_HISTORY_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    interval: Annotated[PriceInterval, Query()],
    body: Annotated[list[StockPriceHistorySyncRequest], Body()],
    domain_service: StockPriceHistoryDomainServiceDep,
) -> dict:
    _LOG.info("API_REQUEST_STOCK_PRICE_HISTORY_SYNC", stock_id=stock_id, interval=interval, count=len(body))
    count = await domain_service.sync_price_history(stock_id, interval, body)
    return {"synced": count}


@router.get(
    "/{stock_id}/price-history",
    response_model=PaginatedResponse[ResponseStockPriceHistory],
)
async def list_stock_price_history(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.STOCK_PRICE_HISTORY_READ, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    query_service: StockPriceHistoryQueryServiceDep,
    filter_params: Annotated[StockPriceHistoryFilterParameter, Depends(FilterQueryParamDep)],
    pagination_params: Annotated[StockPriceHistoryPaginationParameter, Depends(PaginationQueryParamDep)],
) -> PaginatedResponse[ResponseStockPriceHistory]:
    _LOG.info("API_REQUEST_STOCK_PRICE_HISTORY_LIST", stock_id=stock_id)
    merged_filter = StockPriceHistoryFilterParameter.merge_ops(filter_params, eq={"stock_id": stock_id})
    page = await query_service.find_page(merged_filter, pagination_params)
    return PaginatedResponse[ResponseStockPriceHistory](
        items=[SchemaMapper.entity_to_response(e, ResponseStockPriceHistory) for e in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )


@router.get(
    "/{stock_id}/price-history/bars",
    response_model=list[ResponseStockPriceHistory],
)
async def get_price_bars(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(
                PermissionCode.STOCK_PRICE_HISTORY_READ, allowed_scopes=frozenset({RoleScope.ADMIN})
            )
        ),
    ],
    stock_id: Annotated[int, Path()],
    interval: Annotated[PriceInterval, Query()],
    query_service: StockPriceHistoryQueryServiceDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 60,
) -> list[ResponseStockPriceHistory]:
    _LOG.info("API_REQUEST_STOCK_PRICE_HISTORY_BARS", stock_id=stock_id, interval=interval, limit=limit)
    entities = await query_service.find_bars(stock_id, interval, limit=limit)
    return [SchemaMapper.entity_to_response(e, ResponseStockPriceHistory) for e in entities]
