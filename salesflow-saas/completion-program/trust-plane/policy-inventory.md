# Trust Plane — Policy Inventory

> **Version:** 1.0 — 2026-04-16
> **Purpose:** Enumerate every access-control and authorization check currently in the system (app code, prompts, conditionals) so they can be migrated to OPA + OpenFGA.
> **Goal:** Zero policy logic in app code by end of WS4. App code = enforcement hooks only.

---

## Current Policy Locations (Pre-Migration)

| Policy | Current Location | Type | Target: OPA / OpenFGA | Priority |
|--------|----------------|------|----------------------|---------|
| Tenant data isolation | `backend/app/middleware/tenant.py` — `tenant_id` filter on all queries | Row-level filter | OPA + OpenFGA (tenant resource) | HIGH |
| JWT authentication | `backend/app/core/security.py` — JWT decode + user lookup | AuthN | Keycloak (replace custom JWT) | HIGH |
| Role-based endpoint protection | FastAPI `Depends(require_role(...))` scattered across routers | RBAC | OpenFGA (role assignment) | HIGH |
| Agent action sensitivity check | Inline `if sensitivity == "high": raise` in agent orchestrator | Sensitivity gate | OPA policy pack | HIGH |
| PDPL consent check | `backend/app/services/consent.py` — manual flag check | Consent gate | OPA policy pack (PDPL module) | HIGH |
| Data residency enforcement | Not implemented — TODO comment in connector services | Residency gate | OPA policy pack (residency module) | HIGH |
| Affiliate commission rules | Business logic in `backend/app/services/affiliate.py` | Business rule | OPA (if compliance-sensitive) | MEDIUM |
| Rate limiting per tenant | Redis counter in middleware | Quota | OPA (if policy-driven) | LOW |
| WhatsApp message consent | Prompt-level instruction in agent prompt | Consent gate | OPA policy pack | HIGH |
| Knowledge base access (sector) | `if tenant.sector in allowed_sectors` check | Access control | OpenFGA (KB resource) | MEDIUM |

---

## OPA Policy Pack Structure (v1)

```
completion-program/trust-plane/opa/
  ├── policies/
  │   ├── tenant_isolation.rego        # Every data query must include tenant_id filter
  │   ├── agent_sensitivity.rego       # Block Executor actions above threshold without approval
  │   ├── pdpl_consent.rego            # Require consent record for personal data processing
  │   ├── data_residency.rego          # Block cross-border transfer without transfer mechanism
  │   ├── tool_permissions.rego        # Per-tool, per-agent-role permission matrix
  │   └── release_gate.rego            # Block release if compliance checklist not signed
  ├── tests/
  │   ├── tenant_isolation_test.rego
  │   ├── agent_sensitivity_test.rego
  │   ├── pdpl_consent_test.rego
  │   ├── data_residency_test.rego
  │   ├── tool_permissions_test.rego
  │   └── release_gate_test.rego
  └── data/
      ├── agent_roles.json             # Synced from agent-role-registry.md
      ├── tool_permissions.json        # Per-tool allowed roles
      └── pdpl_consent_purposes.json   # Allowed processing purposes
```

---

## OPA Policy Samples

### tenant_isolation.rego

```rego
package dealix.tenant

import future.keywords.if
import future.keywords.in

default allow = false

allow if {
    input.tenant_id != ""
    input.resource_tenant_id == input.tenant_id
}

# Admin override (super-admin only)
allow if {
    input.user.roles[_] == "super_admin"
}
```

### agent_sensitivity.rego

```rego
package dealix.agent

import future.keywords.if

default allow = false

# Low/medium sensitivity: OPA pass is sufficient
allow if {
    input.action.sensitivity in {"low", "medium"}
    input.action.reversibility == "reversible"
}

# High/critical: require valid approval_packet_id
allow if {
    input.action.sensitivity in {"high", "critical"}
    input.approval_packet.status == "approved"
    input.approval_packet.approvers_count >= data.thresholds[input.action.sensitivity].min_approvers
}
```

### data_residency.rego

```rego
package dealix.residency

import future.keywords.if
import future.keywords.in

default allow = false

# KSA personal data must stay in KSA
allow if {
    input.data_classification != "personal"
}

allow if {
    input.data_classification == "personal"
    input.target_residency == "KSA"
}

# Cross-border transfer requires explicit mechanism
allow if {
    input.data_classification == "personal"
    input.target_residency != "KSA"
    input.transfer_mechanism in {"standard_contractual_clauses", "adequacy_decision", "explicit_consent"}
}
```

---

## OpenFGA Model Draft (v1)

```
model
  schema 1.1

type user

type service_account
  relations
    define owner: [user]

type tenant
  relations
    define admin: [user]
    define member: [user] or admin
    define viewer: [user] or member

type agent
  relations
    define owned_by: [tenant]
    define can_observe: [user, service_account] or member from owned_by
    define can_recommend: [user, service_account] or admin from owned_by
    define can_execute: [service_account] or admin from owned_by

type workflow
  relations
    define owned_by: [tenant]
    define can_trigger: [user, service_account] or admin from owned_by
    define can_signal: [user, service_account] or admin from owned_by
    define can_view: [user] or member from owned_by

type tool
  relations
    define owned_by: [tenant]
    define can_call: [service_account] or admin from owned_by
    define can_configure: [user] or admin from owned_by

type knowledge_base_chunk
  relations
    define owned_by: [tenant]
    define can_read: [user, service_account] or member from owned_by

type deal
  relations
    define owned_by: [tenant]
    define assigned_to: [user]
    define can_read: [user] or member from owned_by
    define can_write: [user] or assigned_to or admin from owned_by
    define can_approve: [user] or admin from owned_by
```

### Assertion File (openfga-assertions.yaml)

```yaml
# Tests run against OpenFGA staging instance during CI
assertions:
  - description: "Tenant admin can trigger workflow"
    tuple:
      user: "user:alice"
      relation: "can_trigger"
      object: "workflow:partner-approval-123"
    context:
      tuples:
        - { user: "user:alice", relation: "admin", object: "tenant:acme" }
        - { user: "tenant:acme", relation: "owned_by", object: "workflow:partner-approval-123" }
    expected: true

  - description: "Non-member cannot trigger workflow"
    tuple:
      user: "user:bob"
      relation: "can_trigger"
      object: "workflow:partner-approval-123"
    context:
      tuples:
        - { user: "tenant:acme", relation: "owned_by", object: "workflow:partner-approval-123" }
    expected: false

  - description: "Service account can execute agent"
    tuple:
      user: "service_account:docusign-worker"
      relation: "can_execute"
      object: "agent:docusign-trigger"
    context:
      tuples:
        - { user: "tenant:acme", relation: "owned_by", object: "agent:docusign-trigger" }
        - { user: "service_account:docusign-worker", relation: "can_execute", object: "agent:docusign-trigger" }
    expected: true

  - description: "Regular member cannot execute agent"
    tuple:
      user: "user:charlie"
      relation: "can_execute"
      object: "agent:docusign-trigger"
    context:
      tuples:
        - { user: "user:charlie", relation: "member", object: "tenant:acme" }
        - { user: "tenant:acme", relation: "owned_by", object: "agent:docusign-trigger" }
    expected: false
```

---

## Tool Verification Ledger Schema (v1)

Reference: `trust-plane/tool-verification-schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://dealix.ai/schemas/trust/tool-verification/v1",
  "title": "ToolVerificationEntry",
  "type": "object",
  "required": ["entry_id", "tenant_id", "agent_id", "tool_name", "intended_action", "claimed_action", "actual_execution", "side_effects", "contradiction_status", "timestamp"],
  "properties": {
    "entry_id": { "type": "string", "format": "uuid" },
    "tenant_id": { "type": "string", "format": "uuid" },
    "agent_id": { "type": "string" },
    "tool_name": { "type": "string" },
    "intended_action": { "type": "string", "description": "What the agent intended to do" },
    "claimed_action": { "type": "string", "description": "What the agent claimed it did" },
    "actual_execution": { "type": "string", "description": "What was actually executed (from audit log / connector response)" },
    "side_effects": { "type": "array", "items": { "type": "string" } },
    "contradiction_status": {
      "type": "string",
      "enum": ["none", "minor", "major", "critical"],
      "description": "none=intended≈claimed≈actual; minor=small diff; major=significant diff; critical=hallucinated operation"
    },
    "resolution": { "type": "string", "enum": ["auto_compensated", "human_reviewed", "escalated", "pending"] },
    "trace_id": { "type": "string", "description": "OTel trace ID for correlation" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

---

## Migration Plan: App Code → OPA/OpenFGA

| Sprint | Action |
|--------|--------|
| Sprint 1 | Complete this inventory; identify all scattered policy locations |
| Sprint 2 | Deploy OPA sidecar in staging; implement `tenant_isolation.rego` + `agent_sensitivity.rego` |
| Sprint 3 | Implement `pdpl_consent.rego` + `data_residency.rego`; deploy OpenFGA staging; implement model |
| Sprint 4 | Remove inline policy checks from app code (replace with OPA/OpenFGA calls); Vault + Keycloak live |
| Sprint 5 | All policy in OPA/OpenFGA; app code = enforcement hooks only; zero scattered conditionals |
