from __future__ import annotations

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
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
        message_key: str = "errors.validation.failed",
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
    def __init__(
        self,
        message_key: str = "errors.auth.unauthorized",
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            ErrorCode.UNAUTHORIZED,
            message_key,
            status_code=401,
            params=params,
            headers=headers,
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        message_key: str = "errors.auth.forbidden",
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(ErrorCode.FORBIDDEN, message_key, status_code=403, params=params)


class BadRequestException(AppException):
    def __init__(
        self,
        message_key: str = "errors.client.bad_request",
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(ErrorCode.BAD_REQUEST, message_key, status_code=400, params=params)


class PayloadTooLargeException(AppException):
    def __init__(
        self,
        message_key: str = "errors.client.payload_too_large",
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            ErrorCode.PAYLOAD_TOO_LARGE,
            message_key,
            status_code=413,
            params=params,
        )


class UnsupportedMediaTypeException(AppException):
    def __init__(
        self,
        message_key: str = "errors.client.unsupported_media_type",
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            ErrorCode.UNSUPPORTED_MEDIA_TYPE,
            message_key,
            status_code=415,
            params=params,
        )


class NotFoundException(AppException):
    def __init__(
        self,
        message_key: str = "errors.resource.not_found",
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(ErrorCode.NOT_FOUND, message_key, status_code=404, params=params)


class BusinessViolationException(AppException):
    def __init__(
        self,
        message_key: str = "errors.business.violation",
        *,
        params: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(ErrorCode.BUSINESS_VIOLATION, message_key, status_code=400, params=params)


class RateLimitedException(AppException):
    def __init__(
        self,
        message_key: str = "errors.rate_limit.too_many_requests",
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            ErrorCode.RATE_LIMITED,
            message_key,
            status_code=429,
            params=params,
            headers=headers,
        )


class InternalException(AppException):
    def __init__(
        self,
        *,
        message_key: str = "errors.system.internal",
        params: dict[str, Any] | None = None,
        developer_message: str | None = None,
    ) -> None:
        super().__init__(
            ErrorCode.INTERNAL_ERROR,
            message_key,
            status_code=500,
            params=params,
            developer_message=developer_message,
        )


class ServiceUnavailableException(AppException):
    def __init__(
        self,
        message_key: str = "errors.system.unavailable",
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            ErrorCode.SERVICE_UNAVAILABLE,
            message_key,
            status_code=503,
            params=params,
            headers=headers,
        )
