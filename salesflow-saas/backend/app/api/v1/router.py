from fastapi import APIRouter
from app.api.v1 import auth, leads, deals, dashboard, tenants, users, ai_agents, webhooks
from app.api.v1 import conversations, campaigns, consents, forms, voice
from app.api.v1 import sequences, contracts, files, branding, tags
from app.api.v1 import analytics, custom_fields, notifications, appointments, proposals
from app.api.v1 import suppression, social_listening
from app.api.v1 import customers, activities, ai_traces, audit_logs
from app.api.v1 import growth_events, integrations, subscriptions
from app.api.v1 import messages_api
from app.api.v1 import playbooks, sla

api_router = APIRouter()

# Core
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/tenant", tags=["Tenant"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(deals.router, prefix="/deals", tags=["Deals"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# Activities
api_router.include_router(activities.router, prefix="/activities", tags=["Activities"])

# AI Agents & Governance
api_router.include_router(ai_agents.router, prefix="/ai", tags=["AI Agents"])
api_router.include_router(ai_traces.router, prefix="/ai", tags=["AI Governance"])

# Conversations & Communication
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(messages_api.router, prefix="/messages", tags=["Messages"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# Marketing & Attribution
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(growth_events.router, prefix="/growth-events", tags=["Growth Events"])

# Compliance
api_router.include_router(consents.router, prefix="/consents", tags=["Consents"])
api_router.include_router(suppression.router, prefix="/suppression", tags=["Suppression List"])

# Social Listening
api_router.include_router(social_listening.router, prefix="/social", tags=["Social Listening"])

# Voice AI
api_router.include_router(voice.router, prefix="/voice", tags=["Voice AI"])

# Sales Sequences
api_router.include_router(sequences.router, prefix="/sequences", tags=["Sequences"])

# Contracts & E-Sign
api_router.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])

# Integrations
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])

# Subscriptions
api_router.include_router(subscriptions.router, prefix="/subscription", tags=["Subscriptions"])

# File Management
api_router.include_router(files.router, prefix="/files", tags=["Files"])

# Branding & Settings
api_router.include_router(branding.router, prefix="/branding", tags=["Branding"])

# Tags & Segments
api_router.include_router(tags.router, prefix="", tags=["Tags & Segments"])

# Analytics & Reporting
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Custom Fields
api_router.include_router(custom_fields.router, prefix="/custom-fields", tags=["Custom Fields"])

# Notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Appointments
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])

# Proposals
api_router.include_router(proposals.router, prefix="/proposals", tags=["Proposals"])

# Audit Logs
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])

# Industry Playbooks (Revenue Engine)
api_router.include_router(playbooks.router, prefix="/playbooks", tags=["Playbooks"])

# SLA Tracking
api_router.include_router(sla.router, prefix="/sla", tags=["SLA"])

# Public (no auth required)
api_router.include_router(forms.router, prefix="/forms", tags=["Forms"])
