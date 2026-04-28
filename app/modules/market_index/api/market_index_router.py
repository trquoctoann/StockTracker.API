from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.base_mapper import SchemaMapper
from app.common.base_schema import PaginatedResponse, build_query_param_dependency, get_model_fields
from app.common.enum import RoleScope
from app.core.logger import get_logger
from app.modules.market_index.api.dto.market_index_request import MarketIndexCreateRequest, MarketIndexUpdateRequest
from app.modules.market_index.api.dto.market_index_response import ResponseMarketIndex
from app.modules.market_index.application.command.market_index_command import UpdateMarketIndexCommand
from app.modules.market_index.application.market_index_query_service import MarketIndexFetchSpec
from app.modules.market_index.application.query.market_index_query import (
    MarketIndexFilterParameter,
    MarketIndexPaginationParameter,
)
from app.modules.market_index.market_index_dependency import MarketIndexDomainServiceDep
from app.modules.market_index.market_index_query_dependency import MarketIndexQueryServiceDep

_LOG = get_logger(__name__)

router = APIRouter(prefix="/market-indices", tags=["market-indices"])

PaginationQueryParamDep = build_query_param_dependency(
    MarketIndexPaginationParameter,
    include_fields=get_model_fields(MarketIndexPaginationParameter),
)

FilterQueryParamDep = build_query_param_dependency(
    MarketIndexFilterParameter,
    exclude_fields=get_model_fields(MarketIndexPaginationParameter),
)


@router.post("", response_model=ResponseMarketIndex, status_code=status.HTTP_201_CREATED)
async def create_market_index(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.MARKET_INDEX_CREATE, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    body: Annotated[MarketIndexCreateRequest, Body()],
    domain_service: MarketIndexDomainServiceDep,
) -> ResponseMarketIndex:
    _LOG.info("API_REQUEST_MARKET_INDEX_CREATE", command=body)
    entity = await domain_service.create(body)
    return SchemaMapper.entity_to_response(entity, ResponseMarketIndex)


@router.put("/{market_index_id}", response_model=ResponseMarketIndex, status_code=status.HTTP_200_OK)
async def update_market_index(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.MARKET_INDEX_UPDATE, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    market_index_id: Annotated[int, Path()],
    body: Annotated[MarketIndexUpdateRequest, Body()],
    domain_service: MarketIndexDomainServiceDep,
) -> ResponseMarketIndex:
    _LOG.info("API_REQUEST_MARKET_INDEX_UPDATE", market_index_id=market_index_id, command=body)
    entity = await domain_service.update(UpdateMarketIndexCommand(id=market_index_id, **body.model_dump()))
    return SchemaMapper.entity_to_response(entity, ResponseMarketIndex)


@router.delete("/{market_index_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_market_index(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.MARKET_INDEX_DELETE, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    market_index_id: Annotated[int, Path()],
    domain_service: MarketIndexDomainServiceDep,
) -> None:
    _LOG.info("API_REQUEST_MARKET_INDEX_DELETE", market_index_id=market_index_id)
    await domain_service.delete(market_index_id)


@router.get("", response_model=PaginatedResponse[ResponseMarketIndex])
async def get_page_market_indices(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.MARKET_INDEX_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    filter_params: Annotated[MarketIndexFilterParameter, Depends(FilterQueryParamDep)],
    pagination: Annotated[MarketIndexPaginationParameter, Depends(PaginationQueryParamDep)],
    query_service: MarketIndexQueryServiceDep,
) -> PaginatedResponse[ResponseMarketIndex]:
    _LOG.info("API_REQUEST_MARKET_INDEX_PAGE", offset=pagination.offset, limit=pagination.limit)
    page = await query_service.find_page(filter_params, pagination, fetch_spec=MarketIndexFetchSpec(stocks=True))
    return PaginatedResponse(
        items=[SchemaMapper.entity_to_response(i, ResponseMarketIndex) for i in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )


@router.get("/all", response_model=list[ResponseMarketIndex])
async def get_all_market_indices(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.MARKET_INDEX_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    filter_params: Annotated[MarketIndexFilterParameter, Depends(FilterQueryParamDep)],
    query_service: MarketIndexQueryServiceDep,
) -> list[ResponseMarketIndex]:
    _LOG.info("API_REQUEST_MARKET_INDEX_LIST_ALL")
    indices = await query_service.find_all(filter_params, fetch_spec=MarketIndexFetchSpec(stocks=True))
    return [SchemaMapper.entity_to_response(i, ResponseMarketIndex) for i in indices]


@router.get("/{market_index_id}", response_model=ResponseMarketIndex)
async def get_market_index(
    _auth: Annotated[
        object,
        Depends(
            require_context_permissions(PermissionCode.MARKET_INDEX_READ, allowed_scopes=frozenset({RoleScope.ADMIN}))
        ),
    ],
    market_index_id: Annotated[int, Path()],
    query_service: MarketIndexQueryServiceDep,
) -> ResponseMarketIndex:
    _LOG.info("API_REQUEST_MARKET_INDEX_GET", market_index_id=market_index_id)
    entity = await query_service.get_by_id(market_index_id, fetch_spec=MarketIndexFetchSpec(stocks=True))
    return SchemaMapper.entity_to_response(entity, ResponseMarketIndex)
