from app.common.auth.principals import AuthTokenType, ContextPrincipal, IdentityPrincipal
from app.common.enum import RoleScope


class TestAuthTokenType:
    def test_identity_value(self):
        assert AuthTokenType.IDENTITY == "identity"

    def test_context_value(self):
        assert AuthTokenType.CONTEXT == "context"


class TestIdentityPrincipal:
    def test_creation(self):
        p = IdentityPrincipal(subject="sub-123", username="user", email="u@example.com")
        assert p.token_type == AuthTokenType.IDENTITY
        assert p.subject == "sub-123"
        assert p.username == "user"
        assert p.email == "u@example.com"

    def test_optional_fields(self):
        p = IdentityPrincipal(subject="sub")
        assert p.username is None
        assert p.email is None


class TestContextPrincipal:
    def test_creation(self):
        p = ContextPrincipal(
            subject="sub-123",
            scope=RoleScope.ADMIN,
            user_version=1,
            user_roles_version=1,
            role_versions={1: 1},
            permissions_bitmap=7,
        )
        assert p.token_type == AuthTokenType.CONTEXT
        assert p.scope == RoleScope.ADMIN
        assert p.tenant_id is None

    def test_tenant_scope(self):
        p = ContextPrincipal(
            subject="sub",
            scope=RoleScope.TENANT,
            tenant_id=42,
            user_version=1,
            user_roles_version=1,
            role_versions={},
            permissions_bitmap=0,
        )
        assert p.tenant_id == 42
        assert p.scope == RoleScope.TENANT
