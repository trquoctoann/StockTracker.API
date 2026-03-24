from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any


def _get_nested(data: dict[str, Any], dotted_key: str) -> str | None:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current if isinstance(current, str) else None


@lru_cache(maxsize=8)
def _load_locale_file(locale: str) -> dict[str, Any]:
    try:
        pkg = resources.files("app.i18n.errors").joinpath(f"{locale}.json")
        raw = pkg.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


class ErrorMessageCatalog:
    def __init__(self, default_locale: str, supported_locales: frozenset[str]) -> None:
        self._default_locale = default_locale
        self._supported = supported_locales

    @property
    def default_locale(self) -> str:
        return self._default_locale

    def resolve_locale(self, requested: str | None) -> str:
        if not requested:
            return self._default_locale
        normalized = requested.replace("_", "-")
        primary = normalized.split("-", 1)[0].lower()
        full = normalized.lower()
        for loc in self._supported:
            loc_l = loc.lower()
            if loc_l in (full, primary):
                return loc
        return self._default_locale

    def get(self, locale: str, message_key: str, params: dict[str, Any] | None = None) -> str:
        resolved = self.resolve_locale(locale)
        text = _get_nested(_load_locale_file(resolved), message_key)
        if text is None and resolved != self._default_locale:
            text = _get_nested(_load_locale_file(self._default_locale), message_key)
        if text is None:
            text = _get_nested(_load_locale_file(self._default_locale), "errors.system.internal")
        if text is None:
            text = "An unexpected error occurred."
        if params:
            try:
                return text.format(**params)
            except (KeyError, ValueError):
                return text
        return text


_catalog: ErrorMessageCatalog | None = None


def get_error_catalog() -> ErrorMessageCatalog:
    global _catalog
    if _catalog is None:
        from app.core.config import settings

        supported = frozenset(settings.SUPPORTED_LOCALES)
        _catalog = ErrorMessageCatalog(settings.DEFAULT_LOCALE, supported)
    return _catalog
