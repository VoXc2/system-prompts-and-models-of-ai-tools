"""Revenue Action Graph — signal → action → outcome → proof relationships."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

# 14 typed edges Dealix records to learn what works.
REVENUE_EDGE_TYPES: tuple[str, ...] = (
    "signal_created_opportunity",
    "opportunity_drafted_message",
    "message_triggered_reply",
    "reply_led_to_meeting",
    "meeting_led_to_proposal",
    "proposal_led_to_payment",
    "partner_introduced_customer",
    "review_created_recovery_task",
    "approval_allowed_send",
    "blocked_action_prevented_risk",
    "list_intel_top50_targets",
    "service_completed_generated_proof",
    "proof_triggered_upsell",
    "upsell_converted_to_subscription",
)


@dataclass
class RevenueActionGraph:
    """In-memory revenue action graph. Production = Supabase + pgvector."""
    edges: list[dict[str, Any]] = field(default_factory=list)

    def add_edge(
        self,
        *,
        edge_type: str,
        src_id: str,
        dst_id: str,
        customer_id: str = "",
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a typed edge. Validates edge_type."""
        if edge_type not in REVENUE_EDGE_TYPES:
            raise ValueError(
                f"Unknown edge_type: {edge_type}. "
                f"Valid: {', '.join(REVENUE_EDGE_TYPES)}"
            )
        edge: dict[str, Any] = {
            "edge_id": str(uuid.uuid4()),
            "edge_type": edge_type,
            "src_id": src_id,
            "dst_id": dst_id,
            "customer_id": customer_id,
            "weight": float(weight),
            "metadata": dict(metadata or {}),
            "ts": time.time(),
        }
        self.edges.append(edge)
        return edge

    def what_works_for_customer(self, customer_id: str) -> dict[str, Any]:
        """Aggregate edges for a customer → what's working."""
        edges = [e for e in self.edges if e["customer_id"] == customer_id]
        by_type: dict[str, int] = {}
        for e in edges:
            by_type[e["edge_type"]] = by_type.get(e["edge_type"], 0) + 1

        # Score: weighted edge counts. Outcome edges weigh more.
        outcome_edges = {
            "proposal_led_to_payment": 5,
            "upsell_converted_to_subscription": 5,
            "reply_led_to_meeting": 3,
            "meeting_led_to_proposal": 3,
            "blocked_action_prevented_risk": 2,
        }
        score = sum(by_type.get(e, 0) * w for e, w in outcome_edges.items())

        return {
            "customer_id": customer_id,
            "total_edges": len(edges),
            "by_type": by_type,
            "outcome_score": score,
        }


def build_revenue_action_graph_demo() -> dict[str, Any]:
    """Demo graph with realistic edges across 2 customers."""
    g = RevenueActionGraph()
    # Customer A — full funnel
    g.add_edge(edge_type="signal_created_opportunity",
               src_id="signal_1", dst_id="opp_1", customer_id="cust_A")
    g.add_edge(edge_type="opportunity_drafted_message",
               src_id="opp_1", dst_id="msg_1", customer_id="cust_A")
    g.add_edge(edge_type="approval_allowed_send",
               src_id="msg_1", dst_id="msg_1_approved", customer_id="cust_A")
    g.add_edge(edge_type="message_triggered_reply",
               src_id="msg_1_approved", dst_id="reply_1", customer_id="cust_A")
    g.add_edge(edge_type="reply_led_to_meeting",
               src_id="reply_1", dst_id="meeting_1", customer_id="cust_A")
    g.add_edge(edge_type="meeting_led_to_proposal",
               src_id="meeting_1", dst_id="proposal_1", customer_id="cust_A")
    g.add_edge(edge_type="proposal_led_to_payment",
               src_id="proposal_1", dst_id="payment_499",
               customer_id="cust_A", weight=499)
    g.add_edge(edge_type="service_completed_generated_proof",
               src_id="payment_499", dst_id="proof_1", customer_id="cust_A")
    g.add_edge(edge_type="proof_triggered_upsell",
               src_id="proof_1", dst_id="upsell_1", customer_id="cust_A")
    # Customer B — risk path
    g.add_edge(edge_type="blocked_action_prevented_risk",
               src_id="msg_2", dst_id="cold_wa_blocked", customer_id="cust_B")
    g.add_edge(edge_type="review_created_recovery_task",
               src_id="review_2", dst_id="recovery_1", customer_id="cust_B")
    g.add_edge(edge_type="partner_introduced_customer",
               src_id="partner_1", dst_id="customer_B_intro",
               customer_id="cust_B")
    return {
        "edges": list(g.edges),
        "summary_a": g.what_works_for_customer("cust_A"),
        "summary_b": g.what_works_for_customer("cust_B"),
    }
