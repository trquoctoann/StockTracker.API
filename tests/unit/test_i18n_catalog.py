from app.i18n.catalog import ErrorMessageCatalog, _get_nested


class TestGetNested:
    def test_single_key(self):
        data = {"message": "hello"}
        assert _get_nested(data, "message") == "hello"

    def test_dotted_key(self):
        data = {"errors": {"auth": {"forbidden": "Access denied"}}}
        assert _get_nested(data, "errors.auth.forbidden") == "Access denied"

    def test_missing_key_returns_none(self):
        data = {"a": {"b": 1}}
        assert _get_nested(data, "a.c") is None

    def test_non_string_value_returns_none(self):
        data = {"a": {"b": 123}}
        assert _get_nested(data, "a.b") is None

    def test_empty_data(self):
        assert _get_nested({}, "any.key") is None


class TestErrorMessageCatalog:
    def _make_catalog(self) -> ErrorMessageCatalog:
        return ErrorMessageCatalog(
            default_locale="en",
            supported_locales=frozenset({"en", "vi"}),
        )

    def test_resolve_locale_default(self):
        catalog = self._make_catalog()
        assert catalog.resolve_locale(None) == "en"
        assert catalog.resolve_locale("") == "en"

    def test_resolve_locale_supported(self):
        catalog = self._make_catalog()
        assert catalog.resolve_locale("vi") == "vi"

    def test_resolve_locale_unsupported_falls_back(self):
        catalog = self._make_catalog()
        assert catalog.resolve_locale("fr") == "en"

    def test_resolve_locale_with_region(self):
        catalog = self._make_catalog()
        assert catalog.resolve_locale("en-US") == "en"

    def test_resolve_locale_underscore_variant(self):
        catalog = self._make_catalog()
        assert catalog.resolve_locale("en_GB") == "en"

    def test_get_returns_fallback_for_missing_key(self):
        catalog = self._make_catalog()
        result = catalog.get("en", "totally.nonexistent.key", None)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_with_params(self):
        catalog = self._make_catalog()
        result = catalog.get("en", "errors.system.internal", None)
        assert isinstance(result, str)

    def test_default_locale_property(self):
        catalog = self._make_catalog()
        assert catalog.default_locale == "en"
