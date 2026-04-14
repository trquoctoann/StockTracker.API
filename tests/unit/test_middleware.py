import uuid

from app.common.current_user import get_current_user_id, reset_current_user_id, set_current_user_id
from app.middleware.auth_context import AuthContextMiddleware
from app.middleware.request_context import RequestContextMiddleware


class TestExtractBearerToken:
    def test_valid_bearer_token(self):
        result = AuthContextMiddleware._extract_bearer_token("Bearer my-jwt-token")
        assert result == "my-jwt-token"

    def test_bearer_case_insensitive(self):
        result = AuthContextMiddleware._extract_bearer_token("bearer my-token")
        assert result == "my-token"

    def test_no_space_returns_none(self):
        result = AuthContextMiddleware._extract_bearer_token("BearerNoSpace")
        assert result is None

    def test_wrong_scheme_returns_none(self):
        result = AuthContextMiddleware._extract_bearer_token("Basic dXNlcjpwYXNz")
        assert result is None

    def test_empty_token_returns_none(self):
        result = AuthContextMiddleware._extract_bearer_token("Bearer ")
        assert result is None

    def test_empty_string_returns_none(self):
        result = AuthContextMiddleware._extract_bearer_token("")
        assert result is None

    def test_whitespace_trimmed(self):
        result = AuthContextMiddleware._extract_bearer_token("  Bearer   my-token  ")
        assert result == "my-token"


class TestExtractRequestId:
    def test_from_traceparent(self):
        trace_id = "a" * 32
        headers = {b"traceparent": f"00-{trace_id}-0000000000000001-01".encode()}
        result = RequestContextMiddleware._extract_request_id(headers)
        assert result == trace_id

    def test_from_x_request_id(self):
        headers = {b"x-request-id": b"my-request-id"}
        result = RequestContextMiddleware._extract_request_id(headers)
        assert result == "my-request-id"

    def test_from_x_correlation_id(self):
        headers = {b"x-correlation-id": b"corr-123"}
        result = RequestContextMiddleware._extract_request_id(headers)
        assert result == "corr-123"

    def test_traceparent_takes_priority(self):
        trace_id = "b" * 32
        headers = {
            b"traceparent": f"00-{trace_id}-0000000000000001-01".encode(),
            b"x-request-id": b"ignored",
        }
        result = RequestContextMiddleware._extract_request_id(headers)
        assert result == trace_id

    def test_fallback_generates_uuid(self):
        result = RequestContextMiddleware._extract_request_id({})
        parsed = uuid.UUID(result)
        assert parsed.version == 4

    def test_invalid_traceparent_falls_through(self):
        headers = {b"traceparent": b"invalid", b"x-request-id": b"fallback"}
        result = RequestContextMiddleware._extract_request_id(headers)
        assert result == "fallback"


class TestCurrentUserContextVar:
    def test_set_and_get(self):
        token = set_current_user_id("user-123")
        assert get_current_user_id() == "user-123"
        reset_current_user_id(token)

    def test_default_is_empty(self):
        assert get_current_user_id() == ""

    def test_reset_restores_previous(self):
        original_token = set_current_user_id("first")
        nested_token = set_current_user_id("second")
        assert get_current_user_id() == "second"
        reset_current_user_id(nested_token)
        assert get_current_user_id() == "first"
        reset_current_user_id(original_token)
