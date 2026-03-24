from __future__ import annotations

from app.i18n.catalog import get_error_catalog


def get_current_locale() -> str:
    # catalog = get_error_catalog()
    # raw = current_user_locale.get()
    # if raw is None or (isinstance(raw, str) and not raw.strip()):
    #     return catalog.default_locale
    # return catalog.resolve_locale(raw)
    catalog = get_error_catalog()
    return catalog.default_locale
