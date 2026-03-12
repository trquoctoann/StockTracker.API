import uuid

from fastapi import APIRouter, Query

from app.common.base_schema import MessageResponse, PaginatedResponse
from app.core.config import settings
from app.modules.user.dependencies import CurrentUserDep, SessionDep
from app.modules.user.schemas import LoginRequest, Token, UserCreate, UserRead, UserUpdate, UserUpdatePassword
from app.modules.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


# ──── Auth ────


@router.post("/register", response_model=UserRead, status_code=201)
async def register(session: SessionDep, data: UserCreate):
    service = UserService(session)
    return await service.create_user(data)


@router.post("/login", response_model=Token)
async def login(session: SessionDep, data: LoginRequest):
    service = UserService(session)
    return await service.authenticate(data)


# ──── Profile ────


@router.get("/me", response_model=UserRead)
async def get_current_user(current_user: CurrentUserDep):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_current_user(
    session: SessionDep,
    current_user: CurrentUserDep,
    data: UserUpdate,
):
    service = UserService(session)
    return await service.update_user(current_user.id, data)


@router.patch("/me/password", response_model=MessageResponse)
async def update_password(
    session: SessionDep,
    current_user: CurrentUserDep,
    data: UserUpdatePassword,
):
    service = UserService(session)
    await service.update_password(current_user.id, data)
    return MessageResponse(message="Password updated successfully")


# ──── User Management ────


@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
):
    service = UserService(session)
    return await service.list_users(page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    session: SessionDep,
    current_user: CurrentUserDep,
    user_id: uuid.UUID,
):
    service = UserService(session)
    return await service.get_user(user_id)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    session: SessionDep,
    current_user: CurrentUserDep,
    user_id: uuid.UUID,
):
    service = UserService(session)
    await service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")
