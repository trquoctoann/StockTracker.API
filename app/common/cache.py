from __future__ import annotations

import asyncio
import time
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis import get_redis

_LOG = get_logger(__name__)

_circuit_open_until: float = 0.0


def _trip_redis_circuit() -> None:
    global _circuit_open_until
    _circuit_open_until = time.monotonic() + settings.REDIS_CIRCUIT_BREAKER_SECONDS


def _redis_circuit_allows_call() -> bool:
    return time.monotonic() >= _circuit_open_until


def _is_transient_redis_failure(exc: BaseException) -> bool:
    return isinstance(
        exc,
        (RedisConnectionError | RedisTimeoutError | ConnectionError | TimeoutError | OSError | asyncio.TimeoutError),
    )


class CacheService[T: BaseModel]:
    def __init__(self, client: Redis | None, *, key_prefix: str = "") -> None:
        self._client = client
        self._prefix = settings.REDIS_KEY_PREFIX
        self._service_prefix = settings.REDIS_KEY_SERVICE_PREFIX
        self._default_ttl = settings.REDIS_DEFAULT_TTL_SECONDS

    def _use_redis(self) -> bool:
        return self._client is not None and _redis_circuit_allows_call()

    def _key(self, key: str, is_service_level_cache: bool) -> str:
        return f"{self._prefix}:{self._service_prefix}:{key}" if is_service_level_cache else f"{self._prefix}:{key}"

    async def get(self, key: str, *, is_service_level_cache: bool = False) -> str | None:
        if not self._use_redis():
            return None
        try:
            return await self._client.get(self._key(key, is_service_level_cache))  # type: ignore[union-attr]
        except Exception as e:
            if _is_transient_redis_failure(e):
                _trip_redis_circuit()
            _LOG.warning("CACHE_GET_FAILED", cache_key=key, exc_info=True)
            return None

    async def get_model(self, key: str, model_type: type[T], *, is_service_level_cache: bool = False) -> T | None:
        raw = await self.get(key, is_service_level_cache=is_service_level_cache)
        if raw is None:
            return None
        try:
            return model_type.model_validate_json(raw)
        except Exception:
            _LOG.warning("CACHE_DESERIALIZE_FAILED", cache_key=key, exc_info=True)
            await self.delete(key)
            return None

    async def get_int(self, key: str, *, is_service_level_cache: bool = False) -> int | None:
        raw = await self.get(key, is_service_level_cache=is_service_level_cache)
        if raw is None:
            return None
        try:
            return int(raw)
        except (ValueError, TypeError):
            return None

    async def get_many(self, *keys: str, is_service_level_cache: bool = False) -> list[str | None]:
        if not keys:
            return []
        if not self._use_redis():
            return [None] * len(keys)
        try:
            full_keys = [self._key(k, is_service_level_cache) for k in keys]
            return await self._client.mget(full_keys)  # type: ignore[union-attr,return-value]
        except Exception as e:
            if _is_transient_redis_failure(e):
                _trip_redis_circuit()
            _LOG.warning("CACHE_MGET_FAILED", cache_keys=keys, exc_info=True)
            return [None] * len(keys)

    async def set(self, key: str, value: str, *, ttl: int | None = None, is_service_level_cache: bool = False) -> None:
        if not self._use_redis():
            return
        try:
            await self._client.set(self._key(key, is_service_level_cache), value, ex=ttl or self._default_ttl)  # type: ignore[union-attr]
        except Exception as e:
            if _is_transient_redis_failure(e):
                _trip_redis_circuit()
            _LOG.warning("CACHE_SET_FAILED", cache_key=key, exc_info=True)

    async def set_model(
        self, key: str, value: BaseModel, *, ttl: int | None = None, is_service_level_cache: bool = False
    ) -> None:
        await self.set(key, value.model_dump_json(), ttl=ttl, is_service_level_cache=is_service_level_cache)

    async def set_int(
        self, key: str, value: int, *, ttl: int | None = None, is_service_level_cache: bool = False
    ) -> None:
        await self.set(key, str(value), ttl=ttl, is_service_level_cache=is_service_level_cache)

    async def set_many(
        self, mapping: dict[str, str], *, ttl: int | None = None, is_service_level_cache: bool = False
    ) -> None:
        if not mapping:
            return
        if not self._use_redis():
            return
        try:
            effective_ttl = ttl or self._default_ttl
            async with self._client.pipeline(transaction=True) as pipe:  # type: ignore[union-attr]
                for key, value in mapping.items():
                    pipe.set(self._key(key, is_service_level_cache), value, ex=effective_ttl)
                await pipe.execute()
        except Exception as e:
            if _is_transient_redis_failure(e):
                _trip_redis_circuit()
            _LOG.warning("CACHE_SET_MANY_FAILED", cache_keys=list(mapping.keys()), exc_info=True)

    async def delete(self, *keys: str, is_service_level_cache: bool = False) -> None:
        if not keys:
            return
        if not self._use_redis():
            return
        try:
            full_keys = [self._key(k, is_service_level_cache) for k in keys]
            await self._client.delete(*full_keys)  # type: ignore[union-attr]
        except Exception as e:
            if _is_transient_redis_failure(e):
                _trip_redis_circuit()
            _LOG.warning("CACHE_DELETE_FAILED", cache_keys=keys, exc_info=True)


def get_cache_service() -> CacheService:
    return CacheService(get_redis())


CacheServiceDep = Annotated[CacheService, Depends(get_cache_service)]
