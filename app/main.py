import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.common.auth.context_token_codec import get_context_token_codec
from app.common.auth.identity_token_codec import get_identity_token_codec
from app.core.logger import setup_logging

setup_logging()
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.api.v1.router import api_v1_router  # noqa: E402
from app.common.consumer_registry import start_all_consumers  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.database import dispose_engine  # noqa: E402
from app.core.logger import get_logger  # noqa: E402
from app.core.rabbitmq import connect_rabbitmq, dispose_rabbitmq  # noqa: E402
from app.core.redis import dispose_redis  # noqa: E402
from app.exception.handler import register_exception_handlers  # noqa: E402
from app.middleware.auth_context import AuthContextMiddleware  # noqa: E402
from app.middleware.request_context import RequestContextMiddleware  # noqa: E402

_LOG = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _LOG.info(
        "APPLICATION_STARTUP",
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    await connect_rabbitmq()
    consumer_tasks = await start_all_consumers()

    yield

    for task in consumer_tasks:
        task.cancel()
    await asyncio.gather(*consumer_tasks, return_exceptions=True)

    await dispose_rabbitmq()
    await dispose_engine()
    await dispose_redis()
    _LOG.info("APPLICATION_SHUTDOWN")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        AuthContextMiddleware, identity_codec=get_identity_token_codec(), context_codec=get_context_token_codec()
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router)

    register_exception_handlers(app)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
