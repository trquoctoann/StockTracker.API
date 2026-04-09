from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            retry_on_timeout=False,
        )
    return _pool


def get_redis() -> Redis | None:
    if not settings.REDIS_ENABLED:
        return None
    return Redis(connection_pool=_get_pool())


async def dispose_redis() -> None:
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
