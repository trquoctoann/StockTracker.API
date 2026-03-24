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


settings = Settings()  # pyright: ignore[reportCallIssue]
