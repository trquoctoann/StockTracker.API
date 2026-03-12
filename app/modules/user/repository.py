from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import BaseRepository
from app.modules.user.model import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        results = await self.session.exec(statement)
        return results.first()
