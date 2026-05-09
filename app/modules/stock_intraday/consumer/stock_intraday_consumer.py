import time
from typing import Any, ClassVar

from aio_pika.abc import AbstractIncomingMessage

from app.common.base_consumer import BaseConsumer
from app.common.cache import get_cache_service
from app.core.database import async_session_factory
from app.core.logger import get_logger
from app.modules.industry.application.industry_query_service import IndustryQueryService
from app.modules.industry.infrastructure.persistence.industry_repository_impl import IndustryRepositoryImpl
from app.modules.stock.application.stock_query_service import StockQueryService
from app.modules.stock.infrastructure.persistence.stock_repository_impl import (
    StockIndustryRepositoryImpl,
    StockRepositoryImpl,
)
from app.modules.stock_intraday.application.command.stock_intraday_command import UpsertStockIntradayCommand
from app.modules.stock_intraday.application.stock_intraday_domain_service import StockIntradayDomainService
from app.modules.stock_intraday.infrastructure.persistence.stock_intraday_repository_impl import (
    StockIntradayRepositoryImpl,
)

_LOG = get_logger(__name__)


class StockIntradayConsumer(BaseConsumer):
    queue_name: ClassVar[str] = "stocktracker.stock_intraday.sync"
    routing_keys: ClassVar[list[str]] = ["stock_intraday.sync"]

    async def handle(self, payload: dict[str, Any], message: AbstractIncomingMessage) -> None:
        stock_id = payload.get("stock_id")
        records = payload.get("records", [])

        if not stock_id or not records:
            return

        start = time.monotonic()

        commands = [UpsertStockIntradayCommand.model_validate(rec) for rec in records]

        async with async_session_factory() as session:
            cache = get_cache_service()
            repo = StockIntradayRepositoryImpl(session)
            stock_repo = StockRepositoryImpl(session)
            stock_industry_repo = StockIndustryRepositoryImpl(session)
            industry_repo = IndustryRepositoryImpl(session)
            industry_query_service = IndustryQueryService(industry_repo)
            stock_query_service = StockQueryService(stock_repo, stock_industry_repo, industry_query_service)
            domain_service = StockIntradayDomainService(
                session=session,
                stock_intraday_repository=repo,
                stock_query_service=stock_query_service,
                cache_service=cache,
            )
            affected = await domain_service.sync_intraday(stock_id, commands)

        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        _LOG.debug(
            "STOCK_INTRADAY_CONSUMER_PROCESSED",
            queue=self.queue_name,
            stock_id=stock_id,
            record_count=len(records),
            affected_count=affected,
            elapsed_ms=elapsed_ms,
        )
