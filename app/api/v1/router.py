from fastapi import APIRouter

from app.modules.role.api.role_router import router as role_router

api_v1_router = APIRouter(prefix="/api")

api_v1_router.include_router(role_router)
