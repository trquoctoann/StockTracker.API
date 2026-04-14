from app.exception.exception import (
    AppException,
    BadRequestException,
    BusinessViolationException,
    ContextTokenUnauthorizedException,
    ErrorCode,
    ForbiddenException,
    IdentityTokenUnauthorizedException,
    InternalException,
    NotFoundException,
    PayloadTooLargeException,
    RateLimitedException,
    ServiceUnavailableException,
    UnauthorizedException,
    UnsupportedMediaTypeException,
    ValidationException,
)


class TestAppException:
    def test_base_attributes(self):
        exc = AppException(ErrorCode.BAD_REQUEST, "key", status_code=400, developer_message="dev")
        assert exc.code == ErrorCode.BAD_REQUEST
        assert exc.message_key == "key"
        assert exc.status_code == 400
        assert exc.developer_message == "dev"

    def test_optional_fields_default_none(self):
        exc = AppException(ErrorCode.BAD_REQUEST, "key")
        assert exc.params is None
        assert exc.details is None
        assert exc.headers is None


class TestConcreteExceptions:
    def test_validation_exception(self):
        exc = ValidationException("err.key", details=[{"field": "x"}])
        assert exc.status_code == 422
        assert exc.code == ErrorCode.VALIDATION_ERROR

    def test_unauthorized(self):
        exc = UnauthorizedException(headers={"WWW-Authenticate": "Bearer"})
        assert exc.status_code == 401
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_identity_token_unauthorized(self):
        exc = IdentityTokenUnauthorizedException()
        assert exc.status_code == 401
        assert exc.code == ErrorCode.IDENTITY_TOKEN_UNAUTHORIZED

    def test_context_token_unauthorized(self):
        exc = ContextTokenUnauthorizedException()
        assert exc.status_code == 401
        assert exc.code == ErrorCode.CONTEXT_TOKEN_UNAUTHORIZED

    def test_forbidden(self):
        exc = ForbiddenException()
        assert exc.status_code == 403

    def test_not_found(self):
        exc = NotFoundException("errors.not_found", params={"id": "1"})
        assert exc.status_code == 404
        assert exc.params == {"id": "1"}

    def test_bad_request(self):
        exc = BadRequestException()
        assert exc.status_code == 400

    def test_payload_too_large(self):
        exc = PayloadTooLargeException()
        assert exc.status_code == 413

    def test_unsupported_media_type(self):
        exc = UnsupportedMediaTypeException()
        assert exc.status_code == 415

    def test_business_violation(self):
        exc = BusinessViolationException("err.biz", params={"field": "x"})
        assert exc.status_code == 400
        assert exc.code == ErrorCode.BUSINESS_VIOLATION

    def test_rate_limited(self):
        exc = RateLimitedException()
        assert exc.status_code == 429

    def test_internal(self):
        exc = InternalException(developer_message="oops")
        assert exc.status_code == 500
        assert exc.developer_message == "oops"

    def test_service_unavailable(self):
        exc = ServiceUnavailableException()
        assert exc.status_code == 503


class TestExceptionInheritance:
    def test_all_inherit_from_app_exception(self):
        classes = [
            ValidationException,
            UnauthorizedException,
            IdentityTokenUnauthorizedException,
            ContextTokenUnauthorizedException,
            ForbiddenException,
            NotFoundException,
            BusinessViolationException,
            InternalException,
            ServiceUnavailableException,
        ]
        for cls in classes:
            assert issubclass(cls, AppException)

    def test_app_exception_is_python_exception(self):
        assert issubclass(AppException, Exception)
