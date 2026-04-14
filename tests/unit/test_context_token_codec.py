import pytest
from jose import jwt

from app.common.auth.context_token_codec import ContextTokenCodecImpl, ContextTokenPayload
from app.common.auth.principals import AuthTokenType
from app.common.enum import RoleScope
from app.core.config import settings
from app.exception.exception import ContextTokenUnauthorizedException


@pytest.fixture()
def codec():
    return ContextTokenCodecImpl()


@pytest.fixture()
def sample_payload():
    return ContextTokenPayload(
        subject="00000000-0000-0000-0000-000000000001",
        scope=RoleScope.ADMIN,
        tenant_id=None,
        user_version=3,
        user_roles_version=2,
        role_versions={1: 5, 2: 3},
        permissions_bitmap=7,
    )


class TestEncode:
    def test_returns_token_and_ttl(self, codec: ContextTokenCodecImpl, sample_payload):
        token, ttl = codec.encode(sample_payload)
        assert isinstance(token, str)
        assert ttl == settings.AUTH_CONTEXT_TOKEN_TTL_SECONDS

    def test_encoded_claims_contain_required_fields(self, codec: ContextTokenCodecImpl, sample_payload):
        token, _ = codec.encode(sample_payload)
        claims = jwt.get_unverified_claims(token)
        assert claims["token_type"] == AuthTokenType.CONTEXT.value
        assert claims["sub"] == sample_payload.subject
        assert claims["scope"] == sample_payload.scope.value
        assert claims["uv"] == sample_payload.user_version
        assert claims["urv"] == sample_payload.user_roles_version
        assert claims["pbm"] == sample_payload.permissions_bitmap
        assert claims["iss"] == settings.AUTH_CONTEXT_TOKEN_ISSUER
        assert "exp" in claims
        assert "iat" in claims

    def test_tenant_id_none_encoded_as_null(self, codec: ContextTokenCodecImpl, sample_payload):
        token, _ = codec.encode(sample_payload)
        claims = jwt.get_unverified_claims(token)
        assert claims["tid"] is None

    def test_tenant_id_present(self, codec: ContextTokenCodecImpl):
        payload = ContextTokenPayload(
            subject="sub",
            scope=RoleScope.TENANT,
            tenant_id=42,
            user_version=1,
            user_roles_version=1,
            role_versions={},
            permissions_bitmap=0,
        )
        token, _ = codec.encode(payload)
        claims = jwt.get_unverified_claims(token)
        assert claims["tid"] == 42


class TestDecode:
    def test_decode_roundtrip(self, codec: ContextTokenCodecImpl, sample_payload):
        token, _ = codec.encode(sample_payload)
        principal = codec.decode(token)
        assert principal.subject == sample_payload.subject
        assert principal.scope == sample_payload.scope
        assert principal.user_version == sample_payload.user_version
        assert principal.user_roles_version == sample_payload.user_roles_version
        assert principal.permissions_bitmap == sample_payload.permissions_bitmap

    def test_role_versions_preserved(self, codec: ContextTokenCodecImpl, sample_payload):
        token, _ = codec.encode(sample_payload)
        principal = codec.decode(token)
        assert principal.role_versions == sample_payload.role_versions

    def test_invalid_token_raises_unauthorized(self, codec: ContextTokenCodecImpl):
        with pytest.raises(ContextTokenUnauthorizedException):
            codec.decode("invalid.jwt.token")

    def test_wrong_secret_raises_unauthorized(self, codec: ContextTokenCodecImpl, sample_payload):
        wrong_token = jwt.encode(
            {"token_type": "context", "sub": "x"},
            "wrong-secret",
            algorithm="HS256",
        )
        with pytest.raises(ContextTokenUnauthorizedException):
            codec.decode(wrong_token)

    def test_missing_claims_raises_unauthorized(self, codec: ContextTokenCodecImpl):
        token = jwt.encode(
            {
                "token_type": AuthTokenType.CONTEXT.value,
                "iss": settings.AUTH_CONTEXT_TOKEN_ISSUER,
            },
            settings.AUTH_CONTEXT_TOKEN_SECRET,
            algorithm=settings.AUTH_CONTEXT_TOKEN_ALGORITHM,
        )
        with pytest.raises(ContextTokenUnauthorizedException):
            codec.decode(token)

    def test_wrong_token_type_raises_unauthorized(self, codec: ContextTokenCodecImpl):
        token = jwt.encode(
            {
                "token_type": "identity",
                "sub": "x",
                "scope": "ADMIN",
                "uv": 1,
                "urv": 1,
                "rvs": {},
                "pbm": 0,
                "iss": settings.AUTH_CONTEXT_TOKEN_ISSUER,
            },
            settings.AUTH_CONTEXT_TOKEN_SECRET,
            algorithm=settings.AUTH_CONTEXT_TOKEN_ALGORITHM,
        )
        with pytest.raises(ContextTokenUnauthorizedException):
            codec.decode(token)


class TestIsContextToken:
    def test_context_token_detected(self, codec: ContextTokenCodecImpl, sample_payload):
        token, _ = codec.encode(sample_payload)
        assert ContextTokenCodecImpl.is_context_token(token) is True

    def test_non_context_jwt_returns_false(self):
        token = jwt.encode({"token_type": "identity"}, "any-secret", algorithm="HS256")
        assert ContextTokenCodecImpl.is_context_token(token) is False

    def test_garbage_string_returns_false(self):
        assert ContextTokenCodecImpl.is_context_token("not-a-jwt") is False

    def test_empty_string_returns_false(self):
        assert ContextTokenCodecImpl.is_context_token("") is False

    def test_jwt_without_token_type_returns_false(self):
        token = jwt.encode({"sub": "test"}, "secret", algorithm="HS256")
        assert ContextTokenCodecImpl.is_context_token(token) is False
