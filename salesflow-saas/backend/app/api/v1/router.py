from fastapi import APIRouter
from app.api.v1 import auth, leads, deals, dashboard, tenants, users, ai_agents, webhooks
from app.api.v1 import conversations, campaigns, consents, forms, voice
from app.api.v1 import sequences, contracts, files, branding, tags

api_router = APIRouter()

# Core
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/tenant", tags=["Tenant"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(deals.router, prefix="/deals", tags=["Deals"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# AI Agents
api_router.include_router(ai_agents.router, prefix="/ai", tags=["AI Agents"])

# Conversations & Communication
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# Marketing & Attribution
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])

# Compliance
api_router.include_router(consents.router, prefix="/consents", tags=["Consents"])

# Voice AI
api_router.include_router(voice.router, prefix="/voice", tags=["Voice AI"])

# Sales Sequences
api_router.include_router(sequences.router, prefix="/sequences", tags=["Sequences"])

# Contracts & E-Sign
api_router.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])

# File Management
api_router.include_router(files.router, prefix="/files", tags=["Files"])

# Branding & Settings
api_router.include_router(branding.router, prefix="/branding", tags=["Branding"])

# Tags & Segments
api_router.include_router(tags.router, prefix="", tags=["Tags & Segments"])

# Public (no auth required)
api_router.include_router(forms.router, prefix="/forms", tags=["Forms"])
