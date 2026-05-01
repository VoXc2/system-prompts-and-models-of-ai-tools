"""Action Graph — typed signal→action→approval→outcome→proof relationships."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


EDGE_TYPES: tuple[str, ...] = (
    "signal_created_opportunity",
    "message_triggered_reply",
    "reply_created_meeting",
    "meeting_created_followup",
    "followup_influenced_payment",
    "objection_required_proof",
    "partner_introduced_customer",
    "review_created_recovery_task",
    "approval_allowed_send",
    "blocked_action_prevented_risk",
)


@dataclass
class ActionEdge:
    """One typed edge in the action graph."""

    edge_id: str
    edge_type: str
    src_id: str
    dst_id: str
    customer_id: str
    occurred_at: datetime
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "edge_type": self.edge_type,
            "src_id": self.src_id,
            "dst_id": self.dst_id,
            "customer_id": self.customer_id,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self.payload,
        }


@dataclass
class ActionGraph:
    """In-memory action graph for the customer's decision history."""

    edges: list[ActionEdge] = field(default_factory=list)

    def add_edge(
        self,
        *,
        edge_type: str,
        src_id: str,
        dst_id: str,
        customer_id: str,
        payload: dict[str, Any] | None = None,
    ) -> ActionEdge:
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"unknown edge_type: {edge_type}")
        e = ActionEdge(
            edge_id=f"edge_{uuid.uuid4().hex[:16]}",
            edge_type=edge_type,
            src_id=src_id,
            dst_id=dst_id,
            customer_id=customer_id,
            occurred_at=datetime.now(timezone.utc).replace(tzinfo=None),
            payload=payload or {},
        )
        self.edges.append(e)
        return e

    def what_works_summary(self, customer_id: str) -> dict[str, Any]:
        """Roll-up: which signal types led to outcomes?"""
        by_type: dict[str, int] = {}
        for e in self.edges:
            if e.customer_id != customer_id:
                continue
            by_type[e.edge_type] = by_type.get(e.edge_type, 0) + 1
        winning = sorted(by_type.items(), key=lambda x: x[1], reverse=True)
        return {
            "total_edges": sum(by_type.values()),
            "by_edge_type": by_type,
            "top_winning_relationships": winning[:5],
        }
