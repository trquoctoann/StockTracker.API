from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    # Logging
    ENVIRONMENT: str
    SERVICE_NAME: str | None
    LOG_LEVEL: str
    LOG_JSON: bool
    LOG_SQL: bool

    # Database
    DATABASE_URL: str
    DATABASE_POOL_PRE_PING: bool
    DATABASE_POOL_SIZE: int
    DATABASE_MAX_OVERFLOW: int

    # CORS
    ALLOWED_ORIGINS: list[str]

    # Pagination
    DEFAULT_PAGE_SIZE: int
    MAX_PAGE_SIZE: int

    # i18n
    DEFAULT_LOCALE: str
    SUPPORTED_LOCALES: list[str]

    # OIDC Keycloak
    OIDC_KEYCLOAK_SERVER_URL: str
    OIDC_KEYCLOAK_REALM: str
    OIDC_KEYCLOAK_CLIENT_ID: str
    OIDC_KEYCLOAK_CLIENT_SECRET: str
    OIDC_KEYCLOAK_ADMIN_USERNAME: str
    OIDC_KEYCLOAK_ADMIN_PASSWORD: str
    OIDC_KEYCLOAK_VERIFY_TLS: bool

    # Context token
    AUTH_CONTEXT_TOKEN_SECRET: str
    AUTH_CONTEXT_TOKEN_ALGORITHM: str
    AUTH_CONTEXT_TOKEN_TTL_SECONDS: int
    AUTH_CONTEXT_TOKEN_ISSUER: str

    # Redis
    REDIS_ENABLED: bool
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int
    REDIS_SOCKET_CONNECT_TIMEOUT: int
    REDIS_SOCKET_TIMEOUT: int
    REDIS_KEY_PREFIX: str
    REDIS_KEY_SERVICE_PREFIX: str
    REDIS_DEFAULT_TTL_SECONDS: int
    REDIS_CIRCUIT_BREAKER_SECONDS: int

    # RabbitMQ
    RABBITMQ_ENABLED: bool
    RABBITMQ_URL: str
    RABBITMQ_EXCHANGE_NAME: str
    RABBITMQ_EXCHANGE_TYPE: str
    RABBITMQ_PREFETCH_COUNT: int
    RABBITMQ_RECONNECT_DELAY_SECONDS: int

    @property
    def log_service_name(self) -> str:
        return (self.SERVICE_NAME or self.APP_NAME).strip()


settings = Settings()  # pyright: ignore[reportCallIssue]
