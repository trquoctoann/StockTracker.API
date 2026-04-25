from aio_pika import ExchangeType, connect_robust
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractRobustConnection

from app.core.config import settings
from app.core.logger import get_logger
from app.exception.exception import InternalException, ServiceUnavailableException

_LOG = get_logger(__name__)

_connection: AbstractRobustConnection | None = None
_channel: AbstractChannel | None = None
_exchange: AbstractExchange | None = None


def _parse_exchange_type(value: str) -> ExchangeType:
    mapping = {
        "topic": ExchangeType.TOPIC,
        "direct": ExchangeType.DIRECT,
        "fanout": ExchangeType.FANOUT,
        "headers": ExchangeType.HEADERS,
    }
    result = mapping.get(value.lower())
    if result is None:
        raise InternalException(
            developer_message=f"Unsupported RABBITMQ_EXCHANGE_TYPE: {value!r}. Expected one of {list(mapping.keys())}",
        )
    return result


async def connect_rabbitmq() -> None:
    global _connection, _channel, _exchange

    if not settings.RABBITMQ_ENABLED:
        _LOG.info("RABBITMQ_DISABLED")
        return

    _connection = await connect_robust(
        settings.RABBITMQ_URL,
        timeout=settings.RABBITMQ_RECONNECT_DELAY_SECONDS,
    )

    _channel = await _connection.channel()
    await _channel.set_qos(prefetch_count=settings.RABBITMQ_PREFETCH_COUNT)

    exchange_type = _parse_exchange_type(settings.RABBITMQ_EXCHANGE_TYPE)
    _exchange = await _channel.declare_exchange(
        settings.RABBITMQ_EXCHANGE_NAME,
        type=exchange_type,
        durable=True,
    )

    _LOG.info(
        "RABBITMQ_CONNECTED",
        exchange=settings.RABBITMQ_EXCHANGE_NAME,
        exchange_type=settings.RABBITMQ_EXCHANGE_TYPE,
    )


def get_channel() -> AbstractChannel:
    if _channel is None:
        raise ServiceUnavailableException()
    return _channel


def get_exchange() -> AbstractExchange:
    if _exchange is None:
        raise ServiceUnavailableException()
    return _exchange


async def dispose_rabbitmq() -> None:
    global _connection, _channel, _exchange

    if _channel is not None:
        await _channel.close()
        _channel = None
        _exchange = None

    if _connection is not None:
        await _connection.close()
        _connection = None

    _LOG.info("RABBITMQ_DISCONNECTED")
