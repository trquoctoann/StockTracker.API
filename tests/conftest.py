from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.main import app
from app.modules.user.model import User  # noqa: F401

TEST_DATABASE_URL = settings.DATABASE_URL.replace("/stocktracker", "/stocktracker_test")

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine_test) as session:
        yield session


@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_session():
        yield session

    app.dependency_overrides[get_session] = _override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
