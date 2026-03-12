from fastapi import APIRouter

from app.modules.user.router import router as user_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(user_router)
