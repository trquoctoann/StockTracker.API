import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.modules.user.model import User
from app.modules.user.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login", auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    session: SessionDep,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> User:
    if token is None:
        raise UnauthorizedError()

    user_id = decode_access_token(token)
    if user_id is None:
        raise UnauthorizedError(detail="Invalid token")

    repo = UserRepository(session)
    try:
        user = await repo.get_by_id(uuid.UUID(user_id))
    except ValueError:
        raise UnauthorizedError(detail="Invalid token") from None

    if not user:
        raise UnauthorizedError(detail="User not found")

    if not user.is_active:
        raise UnauthorizedError(detail="Inactive user")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
