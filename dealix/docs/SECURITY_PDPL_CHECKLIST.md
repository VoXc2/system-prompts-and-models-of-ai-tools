# Security & PDPL Checklist — Dealix

## Data minimization

- [ ] Collect only fields required for the revenue workflow.
- [ ] Separate **PII** from **embedding payloads** unless explicitly allowed and documented.

## Consent & suppression

- [ ] **Consent ledger** for marketing / WhatsApp outreach.
- [ ] **Opt-out / suppression list** enforced before any campaign or message draft batch.

## Contactability

- [ ] Channel-specific rules (email vs WhatsApp vs LinkedIn).
- [ ] No cold WhatsApp; LinkedIn DMs not automated.

## Audit

- [ ] **Audit logs** for outbound drafts, approvals, and agent tool calls.
- [ ] Correlation IDs on API requests (`RequestIDMiddleware`).

## Secrets & embeddings

- [ ] **No secret indexing** — block `sk-`, private keys, bearer tokens (see `looks_like_secret`, `should_block_embedding`).
- [ ] **No tokens in embeddings** — redact before chunk upsert.

## Supabase

- [ ] **Service role key** only on server-side runtimes (Railway/Render/Fly/VPS).
- [ ] **RLS** enabled; policies reviewed before any client exposure.
- [ ] **Retention policy** for logs, embeddings refresh, and deletion requests.

## Data subject rights

- [ ] **Export** process documented.
- [ ] **Delete** process documented (including vectors and CRM mirrors).

## Outbound messaging

- [ ] **Approval-required** for Gmail send, WhatsApp send, calendar **create**.
- [ ] **Admin-only** tools for project memory bulk reindex in production.

## Approval-required messaging (product)

- Personal Operator endpoints return `approval_required: true` on drafts by design.
- Calendar route documents Arabic + English notes that real creation needs explicit approval.
