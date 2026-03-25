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

    # Database
    DATABASE_URL: str

    # CORS
    ALLOWED_ORIGINS: list[str]

    # Pagination
    DEFAULT_PAGE_SIZE: int
    MAX_PAGE_SIZE: int

    # i18n
    DEFAULT_LOCALE: str
    SUPPORTED_LOCALES: list[str]

    @property
    def log_service_name(self) -> str:
        return (self.SERVICE_NAME or self.APP_NAME).strip()


settings = Settings()  # pyright: ignore[reportCallIssue]
