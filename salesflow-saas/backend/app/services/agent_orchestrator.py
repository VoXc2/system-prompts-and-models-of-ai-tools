"""
Dealix Agent Orchestrator — سرب الإيجنتس المحترفين
Coordinates all AI agents in a unified workflow.
"""
import asyncio
import logging
from enum import Enum
from datetime import datetime, timezone
from typing import Optional

from app.config import get_settings
from app.services.ai_brain import ai_brain
from app.services.lead_discovery import LeadDiscoveryAgent
from app.services.lead_enrichment import LeadEnrichmentService
from app.services.auto_outreach import AutoOutreachEngine
from app.services.voice_ai import VoiceAIService
from app.services.smart_sales import SmartSalesAgent
from app.services.whatsapp_human import WhatsAppHumanEngine

logger = logging.getLogger(__name__)
settings = get_settings()


class AgentType(str, Enum):
    """All available agent types in the Dealix swarm."""
    DATA_INTELLIGENCE = "data_intelligence"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    SOCIAL_MEDIA = "social_media"
    CONTENT = "content"
    RESEARCH = "research"
    FOLLOWUP = "followup"
    QUALIFICATION = "qualification"


# ── Agent registry: tracks running tasks per tenant ──────────────
_agent_registry: dict[str, dict] = {}


def _get_tenant_registry(tenant_id: str) -> dict:
    """Return (or create) the agent-task registry for a tenant."""
    if tenant_id not in _agent_registry:
        _agent_registry[tenant_id] = {
            "active_tasks": [],
            "completed_tasks": [],
            "queued_tasks": [],
            "stats": {
                agent.value: {"runs": 0, "successes": 0, "failures": 0}
                for agent in AgentType
            },
        }
    return _agent_registry[tenant_id]


def _log_task(tenant_id: str, agent_type: str, status: str, detail: str = "") -> dict:
    """Record an agent task in the registry."""
    registry = _get_tenant_registry(tenant_id)
    entry = {
        "agent": agent_type if isinstance(agent_type, str) else agent_type.value,
        "status": status,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if status == "running":
        registry["active_tasks"].append(entry)
    elif status == "completed":
        registry["active_tasks"] = [
            t for t in registry["active_tasks"] if t["agent"] != entry["agent"]
        ]
        registry["completed_tasks"].append(entry)
        stats = registry["stats"].setdefault(
            entry["agent"], {"runs": 0, "successes": 0, "failures": 0}
        )
        stats["runs"] += 1
        stats["successes"] += 1
    elif status == "failed":
        registry["active_tasks"] = [
            t for t in registry["active_tasks"] if t["agent"] != entry["agent"]
        ]
        registry["completed_tasks"].append(entry)
        stats = registry["stats"].setdefault(
            entry["agent"], {"runs": 0, "successes": 0, "failures": 0}
        )
        stats["runs"] += 1
        stats["failures"] += 1
    elif status == "queued":
        registry["queued_tasks"].append(entry)
    return entry


class AgentOrchestrator:
    """Central brain that coordinates every Dealix AI agent.

    Workflow:
        discover_prospects() -> enrich_data() -> qualify_leads()
        -> engage() -> follow_up() -> convert()
    """

    def __init__(self):
        self.enrichment = LeadEnrichmentService()
        self.whatsapp_engine = WhatsAppHumanEngine()

    # ------------------------------------------------------------------
    # 1. Full pipeline
    # ------------------------------------------------------------------

    async def run_full_pipeline(
        self,
        tenant_id: str,
        industry: str,
        location: str = "الرياض",
        config: Optional[dict] = None,
    ) -> dict:
        """Orchestrate the complete agent flow: discover -> enrich -> qualify -> engage.

        Args:
            tenant_id: Tenant identifier.
            industry:  Target industry (e.g. ``healthcare``, ``real_estate``).
            location:  Target city / region.
            config:    Optional overrides — keys include ``max_leads``,
                       ``channel``, ``owner_name``, ``auto_engage``,
                       ``sequence_length``.

        Returns:
            Summary dict with counts and details for every stage.
        """
        config = config or {}
        max_leads = config.get("max_leads", 30)
        channel = config.get("channel", "whatsapp")
        owner_name = config.get("owner_name", "فريق ديليكس")
        auto_engage = config.get("auto_engage", False)
        sequence_length = config.get("sequence_length", 5)

        summary: dict = {
            "tenant_id": tenant_id,
            "industry": industry,
            "location": location,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "stages": {},
        }

        _log_task(tenant_id, AgentType.DATA_INTELLIGENCE, "running", "Full pipeline started")

        # Stage 1: Discover & Enrich ──────────────────────────────────
        try:
            prospects = await self.discover_and_enrich(industry, location, count=max_leads)
            summary["stages"]["discover_enrich"] = {
                "status": "completed",
                "prospects_found": len(prospects),
            }
        except Exception as exc:
            logger.error("Pipeline discover/enrich failed for %s: %s", tenant_id, exc)
            prospects = []
            summary["stages"]["discover_enrich"] = {"status": "failed", "error": str(exc)}

        # Stage 2: Qualify ─────────────────────────────────────────────
        qualified = []
        try:
            for prospect in prospects:
                qualification = await ai_brain.qualify_lead(prospect)
                prospect["ai_score"] = qualification.get("score", 50)
                prospect["ai_status"] = qualification.get("status", "new")
                prospect["ai_priority"] = qualification.get("priority", "medium")
                prospect["ai_next_action"] = qualification.get("next_action", "")
                qualified.append(prospect)

            # Sort by score descending
            qualified.sort(key=lambda p: p.get("ai_score", 0), reverse=True)
            summary["stages"]["qualification"] = {
                "status": "completed",
                "qualified_count": len(qualified),
                "high_priority": sum(1 for p in qualified if p.get("ai_priority") == "high"),
            }
        except Exception as exc:
            logger.error("Pipeline qualification failed for %s: %s", tenant_id, exc)
            qualified = prospects  # fall through with unscored leads
            summary["stages"]["qualification"] = {"status": "failed", "error": str(exc)}

        # Stage 3: Engage (optional) ──────────────────────────────────
        if auto_engage and qualified:
            try:
                outreach = AutoOutreachEngine(tenant_id, industry)
                campaign = await outreach.launch_campaign(
                    leads=qualified,
                    campaign_type="cold_outreach",
                    channel=channel,
                    sequence_length=sequence_length,
                )
                summary["stages"]["engagement"] = {
                    "status": "completed",
                    "campaign_id": campaign.get("campaign_id"),
                    "messages_sent": campaign.get("messages_sent", 0),
                    "messages_failed": campaign.get("messages_failed", 0),
                }
            except Exception as exc:
                logger.error("Pipeline engagement failed for %s: %s", tenant_id, exc)
                summary["stages"]["engagement"] = {"status": "failed", "error": str(exc)}
        else:
            summary["stages"]["engagement"] = {"status": "skipped", "reason": "auto_engage disabled"}

        summary["completed_at"] = datetime.now(timezone.utc).isoformat()
        summary["total_prospects"] = len(qualified)

        _log_task(
            tenant_id, AgentType.DATA_INTELLIGENCE, "completed",
            f"{len(qualified)} prospects processed",
        )

        return summary

    # ------------------------------------------------------------------
    # 2. Discover & Enrich
    # ------------------------------------------------------------------

    async def discover_and_enrich(
        self,
        industry: str,
        location: str = "الرياض",
        count: int = 30,
    ) -> list[dict]:
        """Find prospects via DataIntelligence, then enrich each one.

        Calls :class:`LeadDiscoveryAgent` to find raw prospects, then
        runs :class:`LeadEnrichmentService` on every result in concurrent
        batches.  Results are scored and ranked.

        Args:
            industry: Target industry.
            location: Target city / region.
            count:    Maximum number of prospects to return.

        Returns:
            List of enriched, scored prospect dicts sorted by score.
        """
        # Step 1: Discover
        discovery_agent = LeadDiscoveryAgent(
            tenant_id="system",
            industry=industry,
            location=location,
        )
        raw_leads = await discovery_agent.run_full_discovery(max_leads=count)
        logger.info("Discovered %d raw leads for %s in %s", len(raw_leads), industry, location)

        # Step 2: Enrich each (concurrently in small batches)
        enriched: list[dict] = []
        batch_size = 5
        for i in range(0, len(raw_leads), batch_size):
            batch = raw_leads[i : i + batch_size]
            tasks = [self.enrichment.enrich_lead(lead) for lead in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.warning("Enrichment failed for a lead: %s", result)
                    continue
                enriched.append(result)

        # Step 3: Score and rank
        enriched.sort(key=lambda p: p.get("lead_score", 0), reverse=True)
        return enriched[:count]

    # ------------------------------------------------------------------
    # 3. Engage prospect
    # ------------------------------------------------------------------

    async def engage_prospect(
        self,
        lead_data: dict,
        channel: str = "whatsapp",
        owner_name: str = "فريق ديليكس",
    ) -> dict:
        """Engage a single prospect via the appropriate agent.

        Routes to WhatsApp, Voice, or Social Media channels.  For
        WhatsApp the message is generated via
        :class:`WhatsAppHumanEngine` so it reads like a real person
        texting.

        Args:
            lead_data:  The enriched lead dict (must include ``phone`` for
                        WhatsApp / voice channels).
            channel:    ``whatsapp``, ``voice``, or ``social_media``.
            owner_name: Sender display name.

        Returns:
            Dict with ``success``, ``channel``, and ``message`` / ``details``.
        """
        tenant_id = lead_data.get("tenant_id", settings.DEFAULT_TENANT_ID)
        industry = lead_data.get("industry", "general")
        name = lead_data.get("name", "العميل")
        company = lead_data.get("company_name", lead_data.get("company", {}).get("name", ""))

        _log_task(tenant_id, channel, "running", f"Engaging {name}")

        try:
            if channel == "whatsapp":
                # Generate personalised WhatsApp message via human engine
                bubbles = self.whatsapp_engine.generate_human_message(
                    lead_data=lead_data,
                    message_type="first_contact",
                    owner_name=owner_name,
                    company=company,
                    industry=industry,
                )
                # Also create an AI-powered personalised version
                ai_message = await ai_brain.write_personalized_message(
                    name=name,
                    business=company,
                    industry=industry,
                    city=lead_data.get("city", "الرياض"),
                    source="واتساب",
                    message_type="أول تواصل",
                )
                humanised = self.whatsapp_engine.humanize_message(
                    ai_message, owner_name=owner_name, company=company, lead_name=name,
                )

                # Send via outreach engine
                outreach = AutoOutreachEngine(tenant_id, industry)
                result = await outreach._cold_outreach(lead_data, "whatsapp")
                _log_task(tenant_id, channel, "completed", f"WhatsApp sent to {name}")
                return {
                    "success": result.get("success", False),
                    "channel": "whatsapp",
                    "message_bubbles": bubbles,
                    "message_humanised": humanised,
                    "details": result,
                }

            elif channel == "voice":
                voice = VoiceAIService(tenant_id)
                result = await voice.create_assistant(
                    name=f"Dealix Voice - {name}",
                    industry=industry,
                )
                _log_task(tenant_id, channel, "completed", f"Voice agent prepared for {name}")
                return {
                    "success": "error" not in result,
                    "channel": "voice",
                    "message": "Voice agent ready",
                    "details": result,
                }

            elif channel == "social_media":
                # Generate a DM-style message for social outreach
                message = await ai_brain.write_personalized_message(
                    name=name,
                    business=company,
                    industry=industry,
                    city=lead_data.get("city", "الرياض"),
                    source="وسائل التواصل",
                    message_type="أول تواصل",
                )
                _log_task(tenant_id, channel, "completed", f"Social message drafted for {name}")
                return {
                    "success": True,
                    "channel": "social_media",
                    "message": message,
                    "details": {
                        "note": "Message drafted — manual send required for social platforms",
                        "instagram": lead_data.get("instagram_url", ""),
                        "twitter": lead_data.get("twitter_handle", ""),
                        "linkedin": lead_data.get("linkedin_url", ""),
                    },
                }

            else:
                return {"success": False, "channel": channel, "message": f"Unsupported channel: {channel}"}

        except Exception as exc:
            logger.error("Engagement failed for %s via %s: %s", name, channel, exc)
            _log_task(tenant_id, channel, "failed", str(exc))
            return {"success": False, "channel": channel, "error": str(exc)}

    # ------------------------------------------------------------------
    # 4. Follow-up cycle
    # ------------------------------------------------------------------

    async def run_followup_cycle(self, tenant_id: str) -> dict:
        """Execute all due follow-up steps for a tenant.

        Iterates active sequences, checks which steps are due, and
        dispatches each via the appropriate channel.  For WhatsApp
        follow-ups the :class:`WhatsAppHumanEngine` is used to generate
        realistic message bubbles.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            Summary with ``executed``, ``skipped``, and ``failed`` counts.
        """
        _log_task(tenant_id, AgentType.FOLLOWUP, "running", "Follow-up cycle started")

        summary = {
            "tenant_id": tenant_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "executed": 0,
            "skipped": 0,
            "failed": 0,
            "details": [],
        }

        try:
            # Placeholder: fetch active sequences from DB
            # active_sequences = await db.fetch_due_sequence_steps(tenant_id)
            active_sequences: list[dict] = []

            for step in active_sequences:
                lead_data = step.get("lead_data", {})
                channel = step.get("channel", "whatsapp")
                step_type = step.get("type", "followup")
                step_number = step.get("step_number", 1)

                try:
                    if step_type == "followup":
                        # Map step number to follow-up template
                        if channel == "whatsapp":
                            template_map = {
                                1: "followup_1day",
                                2: "followup_3days",
                                3: "followup_7days",
                            }
                            msg_type = template_map.get(step_number, "followup_7days")
                            bubbles = self.whatsapp_engine.generate_human_message(
                                lead_data=lead_data,
                                message_type=msg_type,
                                owner_name=step.get("owner_name", "فريق ديليكس"),
                                company=step.get("company", "ديليكس"),
                                industry=lead_data.get("industry", "general"),
                            )
                            # Send via outreach engine
                            outreach = AutoOutreachEngine(tenant_id, lead_data.get("industry", "general"))
                            result = await outreach._warm_followup(lead_data, channel)
                            result["message_bubbles"] = bubbles
                        else:
                            outreach = AutoOutreachEngine(tenant_id, lead_data.get("industry", "general"))
                            result = await outreach._warm_followup(lead_data, channel)

                    elif step_type == "reactivation":
                        outreach = AutoOutreachEngine(tenant_id, lead_data.get("industry", "general"))
                        result = await outreach._reactivation(lead_data, channel)

                    elif step_type == "voice_call":
                        voice = VoiceAIService(tenant_id)
                        result = await voice.create_assistant(
                            industry=lead_data.get("industry", "general"),
                        )

                    else:
                        result = {"success": False, "reason": f"Unknown step type: {step_type}"}

                    if result.get("success"):
                        summary["executed"] += 1
                    else:
                        summary["failed"] += 1

                    summary["details"].append({
                        "lead": lead_data.get("name", "unknown"),
                        "step_type": step_type,
                        "step_number": step_number,
                        "channel": channel,
                        "result": "success" if result.get("success") else "failed",
                    })

                except Exception as step_exc:
                    logger.warning("Follow-up step failed: %s", step_exc)
                    summary["failed"] += 1
                    summary["details"].append({
                        "lead": lead_data.get("name", "unknown"),
                        "step_type": step_type,
                        "result": "error",
                        "error": str(step_exc),
                    })

        except Exception as exc:
            logger.error("Follow-up cycle error for %s: %s", tenant_id, exc)
            _log_task(tenant_id, AgentType.FOLLOWUP, "failed", str(exc))
            summary["error"] = str(exc)
            return summary

        summary["completed_at"] = datetime.now(timezone.utc).isoformat()
        _log_task(
            tenant_id, AgentType.FOLLOWUP, "completed",
            f"Executed {summary['executed']}, failed {summary['failed']}",
        )
        return summary

    # ------------------------------------------------------------------
    # 5. Agent status
    # ------------------------------------------------------------------

    async def get_agent_status(self, tenant_id: str) -> dict:
        """Return the status of all agents for a tenant.

        Returns:
            Dict keyed by agent type with ``active``, ``queued``,
            ``completed`` task lists and cumulative ``stats``.
        """
        registry = _get_tenant_registry(tenant_id)

        agents_status: dict = {}
        for agent in AgentType:
            agent_key = agent.value
            agents_status[agent_key] = {
                "active": [t for t in registry["active_tasks"] if t["agent"] == agent_key],
                "queued": [t for t in registry["queued_tasks"] if t["agent"] == agent_key],
                "completed": [
                    t for t in registry["completed_tasks"] if t["agent"] == agent_key
                ][-10:],  # last 10
                "stats": registry["stats"].get(
                    agent_key, {"runs": 0, "successes": 0, "failures": 0},
                ),
            }

        return {
            "tenant_id": tenant_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents": agents_status,
            "summary": {
                "total_active": len(registry["active_tasks"]),
                "total_queued": len(registry["queued_tasks"]),
                "total_completed": len(registry["completed_tasks"]),
            },
        }

    # ------------------------------------------------------------------
    # 6. Manual assignment
    # ------------------------------------------------------------------

    async def assign_to_agent(self, lead_id: str, agent_type: str) -> dict:
        """Manually assign a lead to a specific agent type.

        Args:
            lead_id:    Identifier of the lead to assign.
            agent_type: One of the ``AgentType`` values.

        Returns:
            Confirmation dict with assignment details.
        """
        valid_types = {a.value for a in AgentType}
        if agent_type not in valid_types:
            return {
                "success": False,
                "error": (
                    f"Invalid agent_type '{agent_type}'. "
                    f"Must be one of: {', '.join(sorted(valid_types))}"
                ),
            }

        _log_task("system", agent_type, "queued", f"Lead {lead_id} queued for {agent_type}")

        return {
            "success": True,
            "lead_id": lead_id,
            "agent_type": agent_type,
            "status": "queued",
            "assigned_at": datetime.now(timezone.utc).isoformat(),
            "message": f"Lead {lead_id} assigned to {agent_type} agent",
        }


# Module-level singleton
agent_orchestrator = AgentOrchestrator()
