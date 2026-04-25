from __future__ import annotations

import os

os.environ.setdefault("APP_NAME", "StockTracker API Test")
os.environ.setdefault("APP_VERSION", "0.0.1-test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SERVICE_NAME", "API-test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("LOG_JSON", "false")
os.environ.setdefault("LOG_SQL", "false")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_db")
os.environ.setdefault("DATABASE_POOL_PRE_PING", "false")
os.environ.setdefault("DATABASE_POOL_SIZE", "1")
os.environ.setdefault("DATABASE_MAX_OVERFLOW", "0")
os.environ.setdefault("ALLOWED_ORIGINS", '["*"]')
os.environ.setdefault("DEFAULT_PAGE_SIZE", "10")
os.environ.setdefault("MAX_PAGE_SIZE", "100")
os.environ.setdefault("DEFAULT_LOCALE", "en")
os.environ.setdefault("SUPPORTED_LOCALES", '["en","vi"]')
os.environ.setdefault("OIDC_KEYCLOAK_SERVER_URL", "https://keycloak.test")
os.environ.setdefault("OIDC_KEYCLOAK_REALM", "test-realm")
os.environ.setdefault("OIDC_KEYCLOAK_CLIENT_ID", "test-client")
os.environ.setdefault("OIDC_KEYCLOAK_CLIENT_SECRET", "test-secret")
os.environ.setdefault("OIDC_KEYCLOAK_ADMIN_USERNAME", "admin")
os.environ.setdefault("OIDC_KEYCLOAK_ADMIN_PASSWORD", "admin")
os.environ.setdefault("OIDC_KEYCLOAK_VERIFY_TLS", "false")
os.environ.setdefault("AUTH_CONTEXT_TOKEN_SECRET", "super-secret-for-tests")
os.environ.setdefault("AUTH_CONTEXT_TOKEN_ALGORITHM", "HS256")
os.environ.setdefault("AUTH_CONTEXT_TOKEN_TTL_SECONDS", "300")
os.environ.setdefault("AUTH_CONTEXT_TOKEN_ISSUER", "http://test-issuer")
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("REDIS_MAX_CONNECTIONS", "1")
os.environ.setdefault("REDIS_SOCKET_CONNECT_TIMEOUT", "1")
os.environ.setdefault("REDIS_SOCKET_TIMEOUT", "1")
os.environ.setdefault("REDIS_KEY_PREFIX", "test")
os.environ.setdefault("REDIS_KEY_SERVICE_PREFIX", "api")
os.environ.setdefault("REDIS_DEFAULT_TTL_SECONDS", "60")
os.environ.setdefault("REDIS_CIRCUIT_BREAKER_SECONDS", "5")
os.environ.setdefault("RABBITMQ_ENABLED", "false")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
os.environ.setdefault("RABBITMQ_EXCHANGE_NAME", "stocktracker.topic")
os.environ.setdefault("RABBITMQ_EXCHANGE_TYPE", "topic")
os.environ.setdefault("RABBITMQ_PREFETCH_COUNT", "10")
os.environ.setdefault("RABBITMQ_RECONNECT_DELAY_SECONDS", "5")

import pytest

from tests.support.factories import (
    DEFAULT_USER_ID,
    make_context_principal,
    make_identity_principal,
    make_permission,
    make_role,
    make_tenant,
    make_user,
    make_user_role,
)


@pytest.fixture()
def user_entity():
    return make_user()


@pytest.fixture()
def user_role_entity():
    return make_user_role()


@pytest.fixture()
def role_entity():
    return make_role()


@pytest.fixture()
def tenant_entity():
    return make_tenant()


@pytest.fixture()
def permission_entity():
    return make_permission()


@pytest.fixture()
def context_principal():
    return make_context_principal()


@pytest.fixture()
def identity_principal():
    return make_identity_principal()


@pytest.fixture()
def default_user_id():
    return DEFAULT_USER_ID
