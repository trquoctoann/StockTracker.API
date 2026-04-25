import asyncio

from app.common.base_consumer import BaseConsumer
from app.core.logger import get_logger

_LOG = get_logger(__name__)

_consumers: list[BaseConsumer] = []


def register_consumer(consumer: BaseConsumer) -> None:
    _consumers.append(consumer)


async def start_all_consumers() -> list[asyncio.Task]:
    tasks = []
    if not _consumers:
        _LOG.info("CONSUMER_REGISTRY_EMPTY")
        return tasks

    for consumer in _consumers:
        try:
            task = asyncio.create_task(consumer.start())
            tasks.append(task)
        except Exception:
            _LOG.warning("CONSUMER_START_FAILED", consumer=type(consumer).__name__)

    _LOG.info("ALL_CONSUMERS_STARTED", count=len(_consumers))
    return tasks


def get_registered_consumers() -> list[BaseConsumer]:
    return list(_consumers)
