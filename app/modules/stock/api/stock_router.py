from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.base_schema import PaginatedResponse, build_query_param_dependency, get_model_fields
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.stock.api.dto.stock_request import StockCreateRequest, StockUpdateRequest
from app.modules.stock.api.dto.stock_response import ResponseStock
from app.modules.stock.application.command.stock_command import UpdateStockCommand
from app.modules.stock.application.query.stock_query import StockFilterParameter, StockPaginationParameter
from app.modules.stock.application.stock_query_service import StockFetchSpec
from app.modules.stock.stock_dependency import StockDomainServiceDep
from app.modules.stock.stock_query_dependency import StockQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["stocks"])

PaginationQueryParamDep = build_query_param_dependency(
    StockPaginationParameter,
    include_fields=get_model_fields(StockPaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    StockFilterParameter,
    exclude_fields=get_model_fields(StockPaginationParameter),
)


@router.post("", response_model=ResponseStock, status_code=status.HTTP_201_CREATED)
async def create_stock(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.STOCK_CREATE, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    body: Annotated[StockCreateRequest, Body()],
    domain_service: StockDomainServiceDep,
) -> ResponseStock:
    _LOG.info("API_REQUEST_STOCK_CREATE", command=body)
    entity = await domain_service.create(body)
    return SchemaMapper.entity_to_response(entity, ResponseStock)


@router.put("/{stock_id}", response_model=ResponseStock, status_code=status.HTTP_200_OK)
async def update_stock(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.STOCK_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    stock_id: Annotated[int, Path()],
    body: Annotated[StockUpdateRequest, Body()],
    domain_service: StockDomainServiceDep,
) -> ResponseStock:
    _LOG.info("API_REQUEST_STOCK_UPDATE", stock_id=stock_id, command=body)
    entity = await domain_service.update(UpdateStockCommand(id=stock_id, **body.model_dump()))
    return SchemaMapper.entity_to_response(entity, ResponseStock)


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.STOCK_DELETE, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    stock_id: Annotated[int, Path()],
    domain_service: StockDomainServiceDep,
) -> None:
    _LOG.info("API_REQUEST_STOCK_DELETE", stock_id=stock_id)
    await domain_service.delete(stock_id)


@router.get("", response_model=PaginatedResponse[ResponseStock])
async def get_page_stocks(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.STOCK_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    filter_params: Annotated[StockFilterParameter, Depends(FilterQueryParamDep)],
    pagination: Annotated[StockPaginationParameter, Depends(PaginationQueryParamDep)],
    query_service: StockQueryServiceDep,
) -> PaginatedResponse[ResponseStock]:
    _LOG.info("API_REQUEST_STOCK_PAGE", offset=pagination.offset, limit=pagination.limit)
    page = await query_service.find_page(filter_params, pagination, fetch_spec=StockFetchSpec(industries=True))
    return PaginatedResponse(
        items=[SchemaMapper.entity_to_response(s, ResponseStock) for s in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )


@router.get("/all", response_model=list[ResponseStock])
async def get_all_stocks(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.STOCK_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    filter_params: Annotated[StockFilterParameter, Depends(FilterQueryParamDep)],
    query_service: StockQueryServiceDep,
) -> list[ResponseStock]:
    _LOG.info("API_REQUEST_STOCK_LIST_ALL")
    stocks = await query_service.find_all(filter_params, fetch_spec=StockFetchSpec(industries=True))
    return [SchemaMapper.entity_to_response(s, ResponseStock) for s in stocks]


@router.get("/{stock_id}", response_model=ResponseStock)
async def get_stock(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(PermissionCode.STOCK_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))),
    ],
    stock_id: Annotated[int, Path()],
    query_service: StockQueryServiceDep,
) -> ResponseStock:
    _LOG.info("API_REQUEST_STOCK_GET", stock_id=stock_id)
    entity = await query_service.get_by_id(stock_id, fetch_spec=StockFetchSpec(industries=True))
    return SchemaMapper.entity_to_response(entity, ResponseStock)
