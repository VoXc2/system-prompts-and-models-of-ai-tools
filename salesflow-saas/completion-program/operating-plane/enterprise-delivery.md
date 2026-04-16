# Enterprise Delivery Fabric

> **Version:** 1.0 — 2026-04-16
> **Authority:** Platform Lead — all items below must be implemented before first enterprise client onboarding.
> **Plane:** Operating Plane (WS6)

---

## CODEOWNERS

File location: `CODEOWNERS` at repo root.

```gitattributes
# CODEOWNERS — Dealix Platform
# All patterns relative to repo root.
# Format: <pattern> <owner1> <owner2>

# Global fallback — all files require at least one owner review
*                           @dealix-platform-lead

# Critical backend paths — AI Lead + Backend Lead must review
/salesflow-saas/backend/app/ai/              @dealix-ai-lead @dealix-backend-lead
/salesflow-saas/backend/app/connectors/     @dealix-backend-lead @dealix-platform-lead
/salesflow-saas/backend/app/core/security.py @dealix-security-lead @dealix-backend-lead

# Trust plane — Security Lead must review all policy changes
/salesflow-saas/completion-program/trust-plane/ @dealix-security-lead @dealix-ai-lead
/salesflow-saas/completion-program/saudi-governance/ @dealix-security-lead @dealix-compliance-lead

# Decision plane schemas — AI Lead must review all schema changes
/salesflow-saas/completion-program/decision-plane/schemas/ @dealix-ai-lead @dealix-backend-lead

# Temporal workflows — Backend Lead + Platform Engineer must review
/salesflow-saas/backend/app/temporal/       @dealix-backend-lead @dealix-platform-lead

# Infrastructure / CI — Platform Lead must review
/.github/                                   @dealix-platform-lead
/salesflow-saas/completion-program/operating-plane/ @dealix-platform-lead

# Compliance and legal docs — Compliance Lead must review
/salesflow-saas/docs/legal/                 @dealix-compliance-lead
/salesflow-saas/memory/security/            @dealix-security-lead @dealix-compliance-lead
```

---

## GitHub Branch Rulesets

### Ruleset: `main-protection`

```yaml
# GitHub REST API payload for ruleset creation
# POST /repos/{owner}/{repo}/rulesets

name: main-protection
target: branch
enforcement: active
conditions:
  ref_name:
    include: ["~DEFAULT_BRANCH"]
    exclude: []
rules:
  - type: deletion
  - type: non_fast_forward          # No force-push
  - type: required_signatures       # GPG/SSH signed commits
  - type: pull_request
    parameters:
      required_approving_review_count: 2
      dismiss_stale_reviews_on_push: true
      require_code_owner_review: true
      require_last_push_approval: true
  - type: required_status_checks
    parameters:
      strict_required_status_checks_policy: true
      required_status_checks:
        - context: "ci/tests"
        - context: "ci/lint"
        - context: "ci/schema-validation"
        - context: "ci/opa-tests"
        - context: "ci/security-scan"
        - context: "ci/owasp-llm-checklist"   # Release gate
```

### Ruleset: `release-branch-protection`

```yaml
name: release-branch-protection
target: branch
enforcement: active
conditions:
  ref_name:
    include: ["refs/heads/release/*"]
rules:
  - type: deletion
  - type: non_fast_forward
  - type: required_signatures
  - type: pull_request
    parameters:
      required_approving_review_count: 2
      require_code_owner_review: true
  - type: required_status_checks
    parameters:
      required_status_checks:
        - context: "ci/tests"
        - context: "ci/security-scan"
        - context: "ci/attestation"
```

---

## GitHub Environments Configuration

### `dev`

```yaml
name: dev
deployment_protection_rules: []  # No gates on dev
variables:
  - ENVIRONMENT: development
  - LOG_LEVEL: DEBUG
```

### `staging`

```yaml
name: staging
deployment_protection_rules:
  - type: required_reviewers
    reviewers:
      - type: team
        id: platform-engineers
    wait_timer: 0
variables:
  - ENVIRONMENT: staging
  - LOG_LEVEL: INFO
```

### `canary`

```yaml
name: canary
deployment_protection_rules:
  - type: required_reviewers
    reviewers:
      - type: team
        id: platform-engineers
      - type: team
        id: backend-leads
    wait_timer: 5    # 5-minute observation window
variables:
  - ENVIRONMENT: canary
  - CANARY_TRAFFIC_PERCENT: 5
```

### `production`

```yaml
name: production
deployment_protection_rules:
  - type: required_reviewers
    reviewers:
      - type: team
        id: platform-leads
      - type: team
        id: security-leads
    wait_timer: 30   # 30-minute observation window
variables:
  - ENVIRONMENT: production
  - LOG_LEVEL: WARNING
```

---

## OIDC Federation (GitHub Actions → Cloud)

```yaml
# .github/workflows/deploy.yml — OIDC-based deployment (no static secrets)

name: Deploy

on:
  push:
    branches: [release/*]

permissions:
  id-token: write    # Required for OIDC token
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/dealix-github-actions
          aws-region: me-south-1    # KSA region (Bahrain) — closest to KSA

      # From this point, no static AWS_SECRET_ACCESS_KEY in env
      - name: Login to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push image
        run: |
          docker build -t $ECR_REGISTRY/dealix-backend:$GITHUB_SHA .
          docker push $ECR_REGISTRY/dealix-backend:$GITHUB_SHA

      - name: Attest image
        uses: actions/attest-build-provenance@v1
        with:
          subject-name: $ECR_REGISTRY/dealix-backend
          subject-digest: sha256:${{ steps.push.outputs.digest }}
```

---

## Artifact Attestations

```yaml
# Attestation verification step (added to deployment pipeline)
- name: Verify image attestation
  run: |
    gh attestation verify oci://$ECR_REGISTRY/dealix-backend:$GITHUB_SHA \
      --owner dealix-ai \
      --bundle-from-oci
```

Every production image must pass `gh attestation verify` before deployment proceeds.

---

## Canary Release Workflow

```yaml
# .github/workflows/canary.yml

name: Canary Release

on:
  workflow_dispatch:
    inputs:
      image_tag:
        required: true
        type: string

jobs:
  canary-5pct:
    environment: canary
    runs-on: ubuntu-latest
    steps:
      - name: Deploy 5% traffic
        run: |
          # Update load balancer weights: canary=5, stable=95
          aws elbv2 modify-rule --rule-arn $CANARY_RULE_ARN \
            --conditions '[{"Field":"path-pattern","Values":["/*"]}]' \
            --actions '[{"Type":"forward","ForwardConfig":{"TargetGroups":[
              {"TargetGroupArn":"$CANARY_TG","Weight":5},
              {"TargetGroupArn":"$STABLE_TG","Weight":95}
            ]}}]'

      - name: Observe 5 minutes
        run: sleep 300

      - name: Check error rate
        run: |
          ERROR_RATE=$(aws cloudwatch get-metric-statistics \
            --namespace Dealix --metric-name HTTPErrorRate \
            --period 300 --statistics Average \
            --query 'Datapoints[0].Average' --output text)
          if (( $(echo "$ERROR_RATE > 1.0" | bc -l) )); then
            echo "Error rate $ERROR_RATE% exceeds threshold — rolling back"
            # Rollback: restore 100% to stable
            aws elbv2 modify-rule ... # restore stable
            exit 1
          fi

  canary-25pct:
    needs: canary-5pct
    environment: canary
    runs-on: ubuntu-latest
    steps:
      - name: Promote to 25% traffic
        run: |
          # Update weights: canary=25, stable=75
          ...

      - name: Observe 15 minutes + check error rate
        run: |
          sleep 900
          # Same error rate check as above

  promote-100pct:
    needs: canary-25pct
    environment: production
    runs-on: ubuntu-latest
    steps:
      - name: Full rollout
        run: |
          # Update weights: canary=100 (stable deprecated)
          ...
```

**Rollback SLA: < 2 minutes** (automated on error rate breach).

---

## Audit Log Streaming

### Problem

GitHub Enterprise audit log retains events for 180 days; Git events for 7 days. For NCA ECC compliance (5-year retention) and PDPL, external streaming is required.

### Solution

Stream GitHub audit log to external SIEM / data warehouse:

```yaml
# GitHub Audit Log Streaming config (via GitHub REST API)
# POST /enterprises/{enterprise}/audit-log/streaming-configuration

{
  "enabled": true,
  "vendor_name": "amazon_s3",
  "authentication": {
    "provider": "oidc",
    "arn": "arn:aws:iam::ACCOUNT:role/github-audit-log-streaming"
  },
  "bucket": "dealix-audit-logs-ksa",
  "prefix": "github-audit/",
  "region": "me-south-1"
}
```

All audit events land in S3 (KSA region) → queried via Athena or forwarded to SIEM.

**Retention:** 5 years (NCA ECC minimum), encrypted at rest (AES-256), access-logged.

---

## Required CI Status Checks (per PR to main)

| Check | Tool | Description |
|-------|------|-------------|
| `ci/tests` | pytest | Full unit + integration test suite |
| `ci/lint` | ruff + mypy | Python linting + type checking |
| `ci/schema-validation` | jsonschema | Validate all 5 decision plane schemas |
| `ci/opa-tests` | opa test | All OPA policy unit tests |
| `ci/security-scan` | Trivy + Bandit | Container + code vulnerability scan |
| `ci/owasp-llm-checklist` | Custom script | OWASP LLM automated checks (LLM01, 02, 06, 07, 08) |
| `ci/ge-validate` | Great Expectations | Data quality gates on staging dataset |
| `ci/attestation` | gh attestation | Verify image attestation (release branches only) |

---

## Release Checklist (Living Document)

Before every `release/*` branch creation:

- [ ] All required CI checks green on `main`
- [ ] OWASP LLM checklist signed by AI Lead + Security Lead
- [ ] NCA ECC gap register reviewed — no new HIGH gaps unaddressed
- [ ] PDPL processing register reviewed — no new data flows unregistered
- [ ] Semantic metrics dictionary updated for new KPIs
- [ ] Runbooks updated for new operational components
- [ ] Canary deployment plan reviewed by Platform Lead
- [ ] Rollback plan tested on staging
- [ ] Audit log streaming verified (events appearing in S3/SIEM)
- [ ] Architecture register status column updated
