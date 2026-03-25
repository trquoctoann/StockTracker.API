from __future__ import annotations

import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logger import get_logger
from app.exception.exception import AppException, ErrorCode
from app.i18n.catalog import get_error_catalog
from app.i18n.locale import get_current_locale

_LOG = get_logger(__name__)


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None
    developer_message: str | None = Field(default=None)


def _error_json_response(
    *,
    status_code: int,
    code: ErrorCode | str,
    message: str,
    details: list[dict[str, Any]] | None = None,
    developer_message: str | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = ErrorEnvelope(
        code=str(code),
        message=message,
        details=details,
        developer_message=developer_message if settings.DEBUG else None,
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(body.model_dump(exclude_none=True)),
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    catalog = get_error_catalog()

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        _LOG.warning(
            "APP_EXCEPTION",
            code=str(exc.code),
            status_code=exc.status_code,
            message_key=exc.message_key,
        )
        locale = get_current_locale()
        message = catalog.get(locale, exc.message_key, exc.params)
        dev_msg = _app_exception_developer_message(exc)
        return _error_json_response(
            status_code=exc.status_code,
            code=exc.code,
            message=message,
            details=exc.details,
            developer_message=dev_msg,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        _LOG.info("VALIDATION_ERROR", errors_count=len(exc.errors()))
        locale = get_current_locale()
        message = catalog.get(locale, "errors.validation.field_errors", None)
        details = jsonable_encoder(exc.errors())
        return _error_json_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            developer_message=None,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code >= 500:
            _LOG.error("HTTP_EXCEPTION", status_code=exc.status_code, detail=str(exc.detail))
        elif exc.status_code >= 400:
            _LOG.info("HTTP_EXCEPTION", status_code=exc.status_code, detail=str(exc.detail))
        locale = get_current_locale()
        error_code, message_key = _get_error_code_and_message_key(exc.status_code)
        message = catalog.get(locale, message_key, None)
        dev_detail = str(exc.detail) if exc.detail else None
        return _error_json_response(
            status_code=exc.status_code,
            code=error_code,
            message=message,
            developer_message=dev_detail if settings.DEBUG else None,
            headers=dict(exc.headers) if exc.headers else None,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        _LOG.error(
            "UNHANDLED_EXCEPTION",
            error_type=type(exc).__name__,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        locale = get_current_locale()
        message = catalog.get(locale, "errors.system.internal", None)
        dev_msg = None
        if settings.DEBUG:
            dev_msg = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return _error_json_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.INTERNAL_ERROR,
            message=message,
            developer_message=dev_msg,
        )


def _get_error_code_and_message_key(status_code: int) -> tuple[ErrorCode, str]:
    mapping: dict[int, tuple[ErrorCode, str]] = {
        status.HTTP_400_BAD_REQUEST: (ErrorCode.BAD_REQUEST, "errors.client.bad_request"),
        status.HTTP_401_UNAUTHORIZED: (ErrorCode.UNAUTHORIZED, "errors.auth.unauthorized"),
        status.HTTP_403_FORBIDDEN: (ErrorCode.FORBIDDEN, "errors.auth.forbidden"),
        status.HTTP_404_NOT_FOUND: (ErrorCode.NOT_FOUND, "errors.resource.not_found"),
        status.HTTP_409_CONFLICT: (ErrorCode.BAD_REQUEST, "errors.resource.conflict"),
        status.HTTP_410_GONE: (ErrorCode.BAD_REQUEST, "errors.resource.gone"),
        status.HTTP_412_PRECONDITION_FAILED: (ErrorCode.BUSINESS_VIOLATION, "errors.business.precondition_failed"),
        status.HTTP_413_CONTENT_TOO_LARGE: (ErrorCode.PAYLOAD_TOO_LARGE, "errors.client.payload_too_large"),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: (
            ErrorCode.UNSUPPORTED_MEDIA_TYPE,
            "errors.client.unsupported_media_type",
        ),
        status.HTTP_422_UNPROCESSABLE_CONTENT: (ErrorCode.VALIDATION_ERROR, "errors.validation.failed"),
        status.HTTP_429_TOO_MANY_REQUESTS: (ErrorCode.RATE_LIMITED, "errors.rate_limit.too_many_requests"),
        status.HTTP_503_SERVICE_UNAVAILABLE: (ErrorCode.SERVICE_UNAVAILABLE, "errors.system.unavailable"),
    }
    return mapping.get(status_code, (ErrorCode.BAD_REQUEST, "errors.client.bad_request"))


def _merge_developer_messages(*parts: str | None) -> str | None:
    merged = "\n\n".join(p.strip() for p in parts if p and str(p).strip())
    return merged or None


def _app_exception_developer_message(exc: AppException) -> str | None:
    if not settings.DEBUG:
        return None
    cause_tb = "".join(traceback.format_exception(exc.__cause__)) if exc.__cause__ is not None else None
    return _merge_developer_messages(exc.developer_message, cause_tb)
