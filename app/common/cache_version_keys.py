from __future__ import annotations

import uuid


def get_user_cache_key(user_id: uuid.UUID | str) -> str:
    return f"user:{user_id}"


def get_user_version_cache_key(user_id: uuid.UUID | str) -> str:
    return f"user:{user_id}:version"


def get_user_role_version_cache_key(user_id: uuid.UUID, scope: str, tenant_id: int | None) -> str:
    tid = str(tenant_id) if tenant_id is not None else "null"
    return f"user_role:{user_id}:{scope}:{tid}:version"


def get_role_version_cache_key(role_id: int) -> str:
    return f"role:{role_id}:version"


def get_price_history_bars_cache_key(stock_id: int, interval: str, limit: int | None = None) -> str:
    if limit is not None:
        return f"stock_price_history:{stock_id}:{interval}:bars:{limit}"
    return f"stock_price_history:{stock_id}:{interval}:bars"
