from fastapi import APIRouter

from app.modules.role.api.role_router import router as role_router
from app.modules.tenant.api.tenant_router import router as tenant_router
from app.modules.user.api.user_router import router as user_router

api_v1_router = APIRouter(prefix="/api")

api_v1_router.include_router(role_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(tenant_router)
