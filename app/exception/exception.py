from __future__ import annotations

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    IDENTITY_TOKEN_UNAUTHORIZED = "IDENTITY_TOKEN_UNAUTHORIZED"
    CONTEXT_TOKEN_UNAUTHORIZED = "CONTEXT_TOKEN_UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
    BUSINESS_VIOLATION = "BUSINESS_VIOLATION"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class AppException(Exception):  # noqa: N818
    def __init__(
        self,
        code: ErrorCode,
        message_key: str,
        *,
        status_code: int = 400,
        params: dict[str, Any] | None = None,
        details: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
        developer_message: str | None = None,
    ) -> None:
        super().__init__(message_key)
        self.code = code
        self.message_key = message_key
        self.status_code = status_code
        self.params = params
        self.details = details
        self.headers = headers
        self.developer_message = developer_message


class ValidationException(AppException):
    def __init__(
        self,
        message_key: str,
        *,
        params: dict[str, Any] | None = None,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            ErrorCode.VALIDATION_ERROR,
            message_key,
            status_code=422,
            params=params,
            details=details,
        )


class UnauthorizedException(AppException):
    def __init__(self, *, headers: dict[str, str] | None = None) -> None:
        super().__init__(ErrorCode.UNAUTHORIZED, "errors.auth.unauthorized", status_code=401, headers=headers)


class IdentityTokenUnauthorizedException(AppException):
    def __init__(self, *, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            ErrorCode.IDENTITY_TOKEN_UNAUTHORIZED,
            "errors.auth.identity_token_unauthorized",
            status_code=401,
            headers=headers,
        )


class ContextTokenUnauthorizedException(AppException):
    def __init__(self, *, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            ErrorCode.CONTEXT_TOKEN_UNAUTHORIZED,
            "errors.auth.context_token_unauthorized",
            status_code=401,
            headers=headers,
        )


class ForbiddenException(AppException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.FORBIDDEN, "errors.auth.forbidden", status_code=403)


class BadRequestException(AppException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.BAD_REQUEST, "errors.client.bad_request", status_code=400)


class PayloadTooLargeException(AppException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.PAYLOAD_TOO_LARGE, "errors.client.payload_too_large", status_code=413)


class UnsupportedMediaTypeException(AppException):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UNSUPPORTED_MEDIA_TYPE, "errors.client.unsupported_media_type", status_code=415)


class NotFoundException(AppException):
    def __init__(
        self,
        message_key: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(ErrorCode.NOT_FOUND, message_key, status_code=404, params=params)


class BusinessViolationException(AppException):
    def __init__(
        self,
        message_key: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(ErrorCode.BUSINESS_VIOLATION, message_key, status_code=400, params=params)


class RateLimitedException(AppException):
    def __init__(self, *, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            ErrorCode.RATE_LIMITED,
            "errors.rate_limit.too_many_requests",
            status_code=429,
            headers=headers,
        )


class InternalException(AppException):
    def __init__(self, *, developer_message: str | None = None) -> None:
        super().__init__(
            ErrorCode.INTERNAL_ERROR,
            "errors.system.internal",
            status_code=500,
            developer_message=developer_message,
        )


class ServiceUnavailableException(AppException):
    def __init__(self, *, headers: dict[str, str] | None = None) -> None:
        super().__init__(ErrorCode.SERVICE_UNAVAILABLE, "errors.system.unavailable", status_code=503, headers=headers)
