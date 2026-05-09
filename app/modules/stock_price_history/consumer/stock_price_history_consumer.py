import time
from typing import Any, ClassVar

from aio_pika.abc import AbstractIncomingMessage

from app.common.base_consumer import BaseConsumer
from app.common.cache import get_cache_service
from app.common.enum import PriceInterval
from app.core.database import async_session_factory
from app.core.logger import get_logger
from app.modules.industry.application.industry_query_service import IndustryQueryService
from app.modules.industry.infrastructure.persistence.industry_repository_impl import IndustryRepositoryImpl
from app.modules.stock.application.stock_query_service import StockQueryService
from app.modules.stock.infrastructure.persistence.stock_repository_impl import (
    StockIndustryRepositoryImpl,
    StockRepositoryImpl,
)
from app.modules.stock_price_history.application.command.stock_price_history_command import (
    UpsertStockPriceHistoryCommand,
)
from app.modules.stock_price_history.application.stock_price_history_domain_service import (
    StockPriceHistoryDomainService,
)
from app.modules.stock_price_history.infrastructure.persistence.stock_price_history_repository_impl import (
    StockPriceHistoryRepositoryImpl,
)

_LOG = get_logger(__name__)


class StockPriceHistoryConsumer(BaseConsumer):
    queue_name: ClassVar[str] = "stocktracker.stock_price_history.sync"
    routing_keys: ClassVar[list[str]] = ["stock_price_history.sync"]

    async def handle(self, payload: dict[str, Any], message: AbstractIncomingMessage) -> None:
        stock_id = payload.get("stock_id")
        interval_raw = payload.get("interval")
        records = payload.get("records", [])

        if not stock_id or not interval_raw or not records:
            return

        interval = PriceInterval(interval_raw)
        start = time.monotonic()

        commands = [UpsertStockPriceHistoryCommand.model_validate(rec) for rec in records]
        async with async_session_factory() as session:
            cache = get_cache_service()
            repo = StockPriceHistoryRepositoryImpl(session)
            stock_repo = StockRepositoryImpl(session)
            stock_industry_repo = StockIndustryRepositoryImpl(session)
            industry_repo = IndustryRepositoryImpl(session)
            industry_query_service = IndustryQueryService(industry_repo)
            stock_query_service = StockQueryService(stock_repo, stock_industry_repo, industry_query_service)
            domain_service = StockPriceHistoryDomainService(
                session=session,
                stock_price_history_repository=repo,
                stock_query_service=stock_query_service,
                cache_service=cache,
            )
            affected = await domain_service.sync_price_history(stock_id, interval, commands)

        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        _LOG.debug(
            "STOCK_PRICE_HISTORY_CONSUMER_PROCESSED",
            queue=self.queue_name,
            stock_id=stock_id,
            interval=interval_raw,
            record_count=len(records),
            affected_count=affected,
            elapsed_ms=elapsed_ms,
        )
