from contextlib import AbstractAsyncContextManager

from sqlmodel.ext.asyncio.session import AsyncSession


class TransactionManager(AbstractAsyncContextManager):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._transaction = None
        self._nested = False

    async def __aenter__(self):
        if self.session.in_transaction():
            self._transaction = await self.session.begin_nested()
            self._nested = True
        else:
            self._transaction = await self.session.begin()
            self._nested = False
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._transaction is None:
            return None

        if exc_type:
            if self._nested:
                await self.session.rollback()
            else:
                await self._transaction.rollback()
        else:
            await self._transaction.commit()
            if self._nested:
                await self.session.commit()

        self._transaction = None
        self._nested = False
        return None
