from fastapi import APIRouter

from app.modules.account.api.account_router import router as account_router
from app.modules.company_affiliation.api.company_affiliation_router import router as company_affiliation_router
from app.modules.company_event.api.company_event_router import router as company_event_router
from app.modules.company_news.api.company_news_router import router as company_news_router
from app.modules.company_officer.api.company_officer_router import router as company_officer_router
from app.modules.company_profile.api.company_profile_router import router as company_profile_router
from app.modules.company_shareholder.api.company_shareholder_router import router as company_shareholder_router
from app.modules.industry.api.industry_router import router as industry_router
from app.modules.market_index.api.market_index_router import router as market_index_router
from app.modules.role.api.role_router import router as role_router
from app.modules.stock.api.stock_router import router as stock_router
from app.modules.stock_price_history.api.stock_price_history_router import router as stock_price_history_router
from app.modules.tenant.api.tenant_router import router as tenant_router
from app.modules.user.api.user_router import router as user_router

api_v1_router = APIRouter(prefix="/api")

api_v1_router.include_router(role_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(tenant_router)
api_v1_router.include_router(account_router)
api_v1_router.include_router(industry_router)
api_v1_router.include_router(stock_router)
api_v1_router.include_router(market_index_router)
api_v1_router.include_router(company_profile_router)
api_v1_router.include_router(company_shareholder_router)
api_v1_router.include_router(company_officer_router)
api_v1_router.include_router(company_affiliation_router)
api_v1_router.include_router(company_event_router)
api_v1_router.include_router(company_news_router)
api_v1_router.include_router(stock_price_history_router)
