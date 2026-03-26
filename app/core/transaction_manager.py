from contextlib import AbstractAsyncContextManager

from sqlmodel.ext.asyncio.session import AsyncSession


class TransactionManager(AbstractAsyncContextManager):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._transaction = None

    async def __aenter__(self):
        self._transaction = await self.session.begin()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._transaction is not None:
            if exc_type:
                await self._transaction.rollback()
            else:
                await self._transaction.commit()
            self._transaction = None
