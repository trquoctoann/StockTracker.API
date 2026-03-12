from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
