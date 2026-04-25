from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from aio_pika.abc import AbstractIncomingMessage

from app.core.logger import get_logger
from app.core.rabbitmq import get_channel, get_exchange

_LOG = get_logger(__name__)


class BaseConsumer(ABC):
    queue_name: ClassVar[str]
    routing_keys: ClassVar[list[str]]
    durable: ClassVar[bool] = True

    async def start(self) -> None:
        channel = get_channel()
        exchange = get_exchange()

        queue = await channel.declare_queue(self.queue_name, durable=self.durable)

        for routing_key in self.routing_keys:
            await queue.bind(exchange, routing_key=routing_key)

        await queue.consume(self._on_message)

        _LOG.info(
            "CONSUMER_STARTED",
            queue=self.queue_name,
            routing_keys=self.routing_keys,
        )

    async def _on_message(self, message: AbstractIncomingMessage) -> None:
        _LOG.debug(
            "CONSUMER_MESSAGE_RECEIVED",
            queue=self.queue_name,
            routing_key=message.routing_key,
            message_id=message.message_id,
            content_length=len(message.body),
        )

        try:
            async with message.process(requeue=True):
                payload = json.loads(message.body.decode())
                await self.handle(payload, message)

            _LOG.info(
                "CONSUMER_MESSAGE_PROCESSED",
                queue=self.queue_name,
                routing_key=message.routing_key,
                message_id=message.message_id,
            )
        except json.JSONDecodeError:
            _LOG.error(
                "CONSUMER_MESSAGE_INVALID_JSON",
                queue=self.queue_name,
                routing_key=message.routing_key,
                message_id=message.message_id,
                exc_info=True,
            )
            await message.reject(requeue=False)
        except Exception:
            _LOG.error(
                "CONSUMER_MESSAGE_FAILED",
                queue=self.queue_name,
                routing_key=message.routing_key,
                message_id=message.message_id,
                exc_info=True,
            )

    @abstractmethod
    async def handle(self, payload: dict[str, Any], message: AbstractIncomingMessage) -> None:
        pass
