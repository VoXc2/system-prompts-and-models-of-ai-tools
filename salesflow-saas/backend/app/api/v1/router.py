from fastapi import APIRouter
from app.api.v1 import auth, leads, deals, dashboard, tenants, users, ai_agents, webhooks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/tenant", tags=["Tenant"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(deals.router, prefix="/deals", tags=["Deals"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(ai_agents.router, prefix="/ai", tags=["AI Agents"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
