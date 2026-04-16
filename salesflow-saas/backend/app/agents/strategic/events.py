"""
Strategic Growth Event Taxonomy — Dealix Autonomous Revenue OS
══════════════════════════════════════════════════════════════
Defines typed event contracts for all strategic operations:
  - Partnerships
  - M&A (Mergers & Acquisitions)
  - Market Expansion
  - Governance & Execution

Every event is:
  - Pydantic-validated
  - Tenant-scoped
  - Timestamped
  - Auditable (immutable once emitted)
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────

class EventDomain(str, enum.Enum):
    PARTNERSHIP = "partnership"
    MA = "ma"
    GROWTH = "growth"
    GOVERNANCE = "governance"
    EXECUTION = "execution"


class PartnershipEventType(str, enum.Enum):
    OPPORTUNITY_DETECTED = "partnership.opportunity_detected"
    PARTNER_SCORED = "partnership.partner_scored"
    MODEL_RECOMMENDED = "partnership.model_recommended"
    TERM_SHEET_READY = "partnership.term_sheet_ready"
    APPROVAL_REQUESTED = "partnership.approval_requested"
    SIGNED = "partnership.signed"
    PERFORMANCE_REVIEWED = "partnership.performance_reviewed"


class MAEventType(str, enum.Enum):
    TARGET_DETECTED = "ma.target_detected"
    SCREENING_COMPLETED = "ma.screening_completed"
    DD_STARTED = "ma.dd_started"
    DD_RISK_FLAGGED = "ma.dd_risk_flagged"
    VALUATION_READY = "ma.valuation_ready"
    OFFER_STRATEGY_READY = "ma.offer_strategy_ready"
    BOARD_DECISION_REQUIRED = "ma.board_decision_required"
    DEAL_SIGNED = "ma.deal_signed"
    INTEGRATION_KICKOFF = "ma.integration_kickoff"
    INTEGRATION_MILESTONE = "ma.integration_milestone"


class GrowthEventType(str, enum.Enum):
    MARKET_EXPANSION_CANDIDATE = "growth.market_expansion_candidate"
    PLAYBOOK_GENERATED = "growth.playbook_generated"
    CAPEX_OPEX_MODELED = "growth.capex_opex_modeled"
    EXECUTION_BLOCKER_DETECTED = "growth.execution_blocker_detected"
    EXECUTIVE_ESCALATION = "growth.executive_escalation"
    MILESTONE_ACHIEVED = "growth.milestone_achieved"


class GovernanceEventType(str, enum.Enum):
    POLICY_VIOLATION_DETECTED = "governance.policy_violation_detected"
    HITL_OVERRIDE_APPLIED = "governance.hitl_override_applied"
    AUDIT_SNAPSHOT_CREATED = "governance.audit_snapshot_created"
    APPROVAL_GRANTED = "governance.approval_granted"
    APPROVAL_DENIED = "governance.approval_denied"


class ExecutionEventType(str, enum.Enum):
    INITIATIVE_CREATED = "execution.initiative_created"
    INITIATIVE_BLOCKED = "execution.initiative_blocked"
    ROLLBACK_INITIATED = "execution.rollback_initiated"
    SLA_BREACHED = "execution.sla_breached"


class ApprovalLevel(str, enum.Enum):
    AGENT = "agent"           # Agent can auto-approve
    MANAGER = "manager"       # Team lead approval
    DIRECTOR = "director"     # Director-level
    CXOO = "cxo"              # C-level
    BOARD = "board"           # Board resolution required


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PartnershipModel(str, enum.Enum):
    REFERRAL = "referral"
    REVENUE_SHARE = "revenue_share"
    JOINT_VENTURE = "joint_venture"
    WHITE_LABEL = "white_label"
    TECHNOLOGY = "technology"
    DISTRIBUTION = "distribution"


# ── Base Event ────────────────────────────────────────────────

class StrategicEvent(BaseModel):
    """Immutable event record. Base class for all strategic events."""
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    domain: EventDomain
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str              # Which agent emitted this
    confidence: float = 0.0      # 0.0 – 1.0
    payload: Dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    requires_approval: bool = False
    approval_level: Optional[ApprovalLevel] = None
    parent_event_id: Optional[UUID] = None  # Chain events
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        frozen = True  # Immutable after creation


# ── Domain-Specific Events ────────────────────────────────────

class PartnershipEvent(StrategicEvent):
    domain: EventDomain = EventDomain.PARTNERSHIP
    partner_name: Optional[str] = None
    partner_industry: Optional[str] = None
    partner_region: Optional[str] = None
    partnership_model: Optional[PartnershipModel] = None
    estimated_revenue_impact_sar: Optional[float] = None


class MAEvent(StrategicEvent):
    domain: EventDomain = EventDomain.MA
    target_company: Optional[str] = None
    target_industry: Optional[str] = None
    target_revenue_sar: Optional[float] = None
    estimated_valuation_sar: Optional[float] = None
    synergy_estimate_sar: Optional[float] = None
    fit_score: Optional[float] = None  # 0–100


class GrowthEvent(StrategicEvent):
    domain: EventDomain = EventDomain.GROWTH
    market: Optional[str] = None
    country: Optional[str] = None
    capex_sar: Optional[float] = None
    opex_monthly_sar: Optional[float] = None
    expected_revenue_sar: Optional[float] = None
    time_to_revenue_months: Optional[int] = None


class GovernanceEvent(StrategicEvent):
    domain: EventDomain = EventDomain.GOVERNANCE
    policy_name: Optional[str] = None
    violation_details: Optional[str] = None
    decision: Optional[str] = None
    decided_by: Optional[str] = None


class ExecutionEvent(StrategicEvent):
    domain: EventDomain = EventDomain.EXECUTION
    initiative_name: Optional[str] = None
    owner: Optional[str] = None
    sla_days: Optional[int] = None
    days_elapsed: Optional[int] = None
    blocker_description: Optional[str] = None


# ── Decision Memo (unified output format) ─────────────────────

class FinancialImpact(BaseModel):
    revenue_impact_sar: float = 0
    cost_impact_sar: float = 0
    net_impact_sar: float = 0
    payback_months: Optional[int] = None
    irr_percent: Optional[float] = None
    npv_sar: Optional[float] = None


class RiskEntry(BaseModel):
    category: str              # financial, operational, legal, reputational, compliance
    description: str
    likelihood: RiskLevel
    impact: RiskLevel
    mitigation: str


class DecisionMemo(BaseModel):
    """Unified output format for all strategic agents."""
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str
    title: str
    title_ar: str
    summary: str
    summary_ar: str
    recommendation: str
    recommendation_ar: str
    financial_impact: FinancialImpact
    risk_register: List[RiskEntry] = Field(default_factory=list)
    confidence_score: float     # 0.0 – 1.0
    next_best_actions: List[str] = Field(default_factory=list)
    approval_level: ApprovalLevel = ApprovalLevel.MANAGER
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    related_events: List[UUID] = Field(default_factory=list)


# ── Event Bus ─────────────────────────────────────────────────

class StrategicEventBus:
    """
    In-process event bus for strategic domain events.
    Supports:
      - Publish/subscribe by domain and event_type
      - Event history (in-memory, flushed to DB periodically)
      - Governance checks (auto-flag high-risk events for HITL)
    """

    def __init__(self):
        self._subscribers: Dict[str, list] = {}  # event_type -> [callbacks]
        self._history: List[StrategicEvent] = []
        self._governance_thresholds: Dict[str, ApprovalLevel] = {
            # Events that ALWAYS need human approval
            MAEventType.BOARD_DECISION_REQUIRED.value: ApprovalLevel.BOARD,
            MAEventType.DEAL_SIGNED.value: ApprovalLevel.CXOO,
            MAEventType.OFFER_STRATEGY_READY.value: ApprovalLevel.DIRECTOR,
            PartnershipEventType.APPROVAL_REQUESTED.value: ApprovalLevel.DIRECTOR,
            PartnershipEventType.SIGNED.value: ApprovalLevel.CXOO,
            GrowthEventType.EXECUTIVE_ESCALATION.value: ApprovalLevel.CXOO,
        }

    def subscribe(self, event_type: str, callback):
        """Register a callback for an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def subscribe_domain(self, domain: EventDomain, callback):
        """Subscribe to ALL events in a domain."""
        for event_type in self._get_domain_types(domain):
            self.subscribe(event_type, callback)

    async def publish(self, event: StrategicEvent) -> StrategicEvent:
        """
        Publish an event. Governance checks are applied automatically:
        - If the event type is in governance_thresholds, mark requires_approval
        - All events are appended to history
        - Subscribers are notified asynchronously
        """
        import logging
        logger = logging.getLogger("dealix.events")

        # Governance auto-tagging
        if event.event_type in self._governance_thresholds:
            event = event.model_copy(update={
                "requires_approval": True,
                "approval_level": self._governance_thresholds[event.event_type],
            })

        # High financial impact auto-escalation
        if isinstance(event, MAEvent) and event.estimated_valuation_sar:
            if event.estimated_valuation_sar > 10_000_000:  # > 10M SAR
                event = event.model_copy(update={
                    "requires_approval": True,
                    "approval_level": ApprovalLevel.BOARD,
                    "risk_level": RiskLevel.CRITICAL,
                })

        self._history.append(event)
        logger.info(f"[EventBus] {event.event_type} by {event.agent_name} "
                     f"(confidence={event.confidence:.2f}, risk={event.risk_level})")

        # Notify subscribers
        callbacks = self._subscribers.get(event.event_type, [])
        for cb in callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(event)
                else:
                    cb(event)
            except Exception as e:
                logger.error(f"[EventBus] Subscriber error on {event.event_type}: {e}")

        return event

    def get_history(self, domain: Optional[EventDomain] = None,
                    tenant_id: Optional[UUID] = None,
                    limit: int = 100) -> List[StrategicEvent]:
        """Query event history with optional filters."""
        events = self._history
        if domain:
            events = [e for e in events if e.domain == domain]
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        return events[-limit:]

    def get_pending_approvals(self, tenant_id: Optional[UUID] = None) -> List[StrategicEvent]:
        """Get all events requiring human approval."""
        events = [e for e in self._history if e.requires_approval]
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        return events

    @staticmethod
    def _get_domain_types(domain: EventDomain) -> list:
        mapping = {
            EventDomain.PARTNERSHIP: [e.value for e in PartnershipEventType],
            EventDomain.MA: [e.value for e in MAEventType],
            EventDomain.GROWTH: [e.value for e in GrowthEventType],
            EventDomain.GOVERNANCE: [e.value for e in GovernanceEventType],
            EventDomain.EXECUTION: [e.value for e in ExecutionEventType],
        }
        return mapping.get(domain, [])


# ── Singleton ─────────────────────────────────────────────────

_event_bus: Optional[StrategicEventBus] = None


def get_strategic_event_bus() -> StrategicEventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = StrategicEventBus()
    return _event_bus
