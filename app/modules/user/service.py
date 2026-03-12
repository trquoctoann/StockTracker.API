import math
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_schema import PaginatedResponse
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.user.repository import UserRepository
from app.modules.user.schemas import LoginRequest, Token, UserCreate, UserRead, UserUpdate, UserUpdatePassword


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def create_user(self, data: UserCreate) -> UserRead:
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise ConflictError(detail="Email already registered")

        user = await self.repository.create(
            {
                "email": data.email,
                "hashed_password": hash_password(data.password),
                "full_name": data.full_name,
            }
        )
        return UserRead.model_validate(user)

    async def get_user(self, user_id: uuid.UUID) -> UserRead:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="User not found")
        return UserRead.model_validate(user)

    async def list_users(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[UserRead]:
        offset = (page - 1) * page_size
        users = await self.repository.get_all(offset=offset, limit=page_size)
        total = await self.repository.count()
        return PaginatedResponse(
            items=[UserRead.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> UserRead:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="User not found")

        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data:
            existing = await self.repository.get_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise ConflictError(detail="Email already registered")

        user = await self.repository.update(user, update_data)
        return UserRead.model_validate(user)

    async def update_password(self, user_id: uuid.UUID, data: UserUpdatePassword) -> None:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="User not found")

        if not verify_password(data.current_password, user.hashed_password):
            raise BadRequestError(detail="Incorrect current password")

        await self.repository.update(user, {"hashed_password": hash_password(data.new_password)})

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(detail="User not found")
        await self.repository.delete(user)

    async def authenticate(self, data: LoginRequest) -> Token:
        user = await self.repository.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise BadRequestError(detail="Incorrect email or password")

        if not user.is_active:
            raise BadRequestError(detail="Inactive user")

        access_token = create_access_token(subject=str(user.id))
        return Token(access_token=access_token)
