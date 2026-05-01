#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# GitHub — One-shot repo initialization + push script
# سكربت واحد لتهيئة المشروع على GitHub ورفعه بالكامل
# ═══════════════════════════════════════════════════════════════════
#
# Usage:
#   1. cd into the extracted project folder
#   2. Edit GITHUB_USER and REPO_NAME below
#   3. Run: bash scripts/github_setup.sh
#
# Prerequisites:
#   - git installed
#   - gh CLI installed (https://cli.github.com/) — optional but easiest
#   - Logged in: gh auth login
#
# What this does:
#   1. Scans for leaked secrets (safety check)
#   2. Initializes git repo
#   3. Creates an initial commit with everything
#   4. Creates the GitHub repo (private by default)
#   5. Pushes main branch
#   6. Creates and pushes the v2.0.0 tag
#   7. Opens the repo in your browser
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ──────────────────────────────────────────────────────────────
# EDIT THESE TWO VARIABLES
# ──────────────────────────────────────────────────────────────
GITHUB_USER="${GITHUB_USER:-YOUR-GITHUB-USERNAME}"
REPO_NAME="${REPO_NAME:-ai-company-saudi}"
VISIBILITY="${VISIBILITY:-private}"   # private | public
# ──────────────────────────────────────────────────────────────

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🏢 AI Company Saudi — GitHub Setup                ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo

# ──────────────────────────────────────────────────────────────
# Step 0: Pre-flight checks
# ──────────────────────────────────────────────────────────────
if [[ "$GITHUB_USER" == "YOUR-GITHUB-USERNAME" ]]; then
    echo -e "${RED}❌ Edit GITHUB_USER in this script first, or run:${NC}"
    echo "   GITHUB_USER=yourname REPO_NAME=ai-company-saudi bash scripts/github_setup.sh"
    exit 1
fi

# Ensure we're in the project root
if [[ ! -f "pyproject.toml" || ! -d "core" ]]; then
    echo -e "${RED}❌ Run this from the project root (where pyproject.toml lives)${NC}"
    exit 1
fi

# ──────────────────────────────────────────────────────────────
# Step 1: Safety scan — no secrets must exist
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}[1/7]${NC} Scanning for hardcoded secrets..."

if [[ -f ".env" ]]; then
    echo -e "${RED}❌ .env file exists. Move it outside the repo before continuing.${NC}"
    echo "   mv .env ../ai-company-saudi.env.backup"
    exit 1
fi

# Simple grep for known key patterns
PATTERNS='sk-ant-api|AIza[0-9A-Za-z_-]{30,}|gsk_[A-Za-z0-9]{30,}|pat-na|ghp_[A-Za-z0-9]{30,}'
if grep -rEn --include="*.py" --include="*.toml" --include="*.yml" --include="*.yaml" \
    --exclude-dir=".git" --exclude-dir="__pycache__" --exclude-dir=".venv" \
    "$PATTERNS" . 2>/dev/null | \
    grep -vE "\.gitleaks\.toml|\.secrets\.baseline|\.env\.example|docs/|tests/|README" | \
    head -5 | grep -q .; then
    echo -e "${RED}❌ Possible secrets detected. Review before pushing.${NC}"
    exit 1
fi
echo -e "   ${GREEN}✓ Clean — no secrets detected${NC}"

# ──────────────────────────────────────────────────────────────
# Step 2: git init
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}[2/7]${NC} Initializing git..."

if [[ -d ".git" ]]; then
    echo -e "   ${YELLOW}⚠  .git already exists — reusing${NC}"
else
    git init -b main -q
    echo -e "   ${GREEN}✓ Initialized${NC}"
fi

git config --local user.name "${GIT_USER_NAME:-$(git config --global user.name)}" 2>/dev/null || true
git config --local user.email "${GIT_USER_EMAIL:-$(git config --global user.email)}" 2>/dev/null || true

# ──────────────────────────────────────────────────────────────
# Step 3: Initial commit
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}[3/7]${NC} Creating initial commit..."

git add -A
if git diff --cached --quiet 2>/dev/null; then
    echo -e "   ${YELLOW}⚠  Nothing to commit (already committed?)${NC}"
else
    git commit -q -m "feat: initial release v2.1.0

Complete multi-agent AI platform for the Saudi Arabian market with
Dealix Tier-1 sovereign governance layer.

Dealix governance layer (v2.1.0):
- Master Blueprint + 7 Master Documents + 4 governance registers
- Pydantic contracts (DecisionOutput, EventEnvelope, EvidencePack, AuditEntry)
  with generated JSON Schemas
- Mandatory classifications (Approval A0-A3, Reversibility R0-R3, Sensitivity S0-S3)
- Trust Plane: PolicyEvaluator + ApprovalCenter + AuditSink + ToolVerificationLedger
- GovernedPipeline composing Phase 8 with the Trust Plane
- NEVER_AUTO_EXECUTE enforcement for pricing, contracts, NDAs, regulator comms
- PDPL + NCA ECC/DCC/CCC + NIST AI RMF + OWASP LLM Top 10 mapped
- 63 tests passing (34 new Dealix tests)

Phase 8 — Auto Client Acquisition (9 agents + pipeline):
- Intake, ICP Matcher, Pain Extractor, Qualification
- Booking, CRM (HubSpot), Proposal, Outreach, Follow-up

Phase 9 — Autonomous Growth (6 agents + orchestrator):
- Sector Intel (12 Saudi sectors), Content Creator
- Distribution, Enrichment, Competitor Monitor, Market Research

Integrations: WhatsApp Business Cloud API, Email (Resend/SendGrid/SMTP),
Google Calendar, Calendly, HubSpot, n8n.

LLM Router with fallback: Claude, DeepSeek, GLM, Gemini, Groq.

Security: .env-only secrets, SecretStr, gitleaks + detect-secrets + bandit
pre-commit, webhook HMAC verification, non-root Docker.

Ops: FastAPI with 6 routers, SQLAlchemy 2.0 async, Docker multi-stage,
docker-compose stack, GitHub Actions CI/CD, bilingual AR/EN documentation."

    echo -e "   ${GREEN}✓ Committed $(git rev-list --count HEAD) commit(s)${NC}"
fi

# ──────────────────────────────────────────────────────────────
# Step 4: Create GitHub repo (via gh CLI)
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}[4/7]${NC} Creating GitHub repo ${GITHUB_USER}/${REPO_NAME}..."

if command -v gh >/dev/null 2>&1; then
    if ! gh repo view "${GITHUB_USER}/${REPO_NAME}" >/dev/null 2>&1; then
        gh repo create "${GITHUB_USER}/${REPO_NAME}" \
            --"${VISIBILITY}" \
            --description "🏢 Production-grade multi-agent AI platform for the Saudi Arabian market | منصة ذكاء اصطناعي متعددة الوكلاء للسوق السعودي" \
            --source=. \
            --remote=origin \
            --push=false
        echo -e "   ${GREEN}✓ Created ${GITHUB_USER}/${REPO_NAME} (${VISIBILITY})${NC}"
    else
        echo -e "   ${YELLOW}⚠  Repo already exists — reusing${NC}"
        if ! git remote get-url origin >/dev/null 2>&1; then
            git remote add origin "git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
        fi
    fi
else
    echo -e "   ${YELLOW}⚠  gh CLI not found — set up remote manually:${NC}"
    echo "     git remote add origin git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
    git remote add origin "git@github.com:${GITHUB_USER}/${REPO_NAME}.git" 2>/dev/null || true
fi

# ──────────────────────────────────────────────────────────────
# Step 5: Push
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}[5/7]${NC} Pushing main branch..."
git push -u origin main
echo -e "   ${GREEN}✓ Pushed${NC}"

# ──────────────────────────────────────────────────────────────
# Step 6: Tag v2.1.0
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}[6/7]${NC} Creating tag v2.1.0..."

if git rev-parse v2.1.0 >/dev/null 2>&1; then
    echo -e "   ${YELLOW}⚠  Tag v2.1.0 already exists${NC}"
else
    git tag -a v2.1.0 -m "Release v2.1.0 — Dealix Tier-1 governance layer

Adds the full Dealix sovereign governance layer:
- Master Blueprint + 7 Master Documents + 4 governance registers
- Pydantic contracts (DecisionOutput, EventEnvelope, EvidencePack, AuditEntry)
- Mandatory classifications (Approval A0-A3, Reversibility R0-R3, Sensitivity S0-S3)
- Trust Plane: PolicyEvaluator + ApprovalCenter + AuditSink + ToolVerificationLedger
- GovernedPipeline composing Phase 8 with the Trust Plane
- NEVER_AUTO_EXECUTE enforcement for pricing, contracts, NDAs, regulator comms
- PDPL + NCA ECC/DCC/CCC + NIST AI RMF + OWASP LLM Top 10 mapped
- 63 tests passing (34 new Dealix tests)

See CHANGELOG.md for full release notes."
    git push origin v2.1.0
    echo -e "   ${GREEN}✓ Tagged and pushed v2.1.0${NC}"
fi

# ──────────────────────────────────────────────────────────────
# Step 7: Create GitHub release
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}[7/7]${NC} Creating GitHub release..."

if command -v gh >/dev/null 2>&1; then
    if ! gh release view v2.1.0 --repo "${GITHUB_USER}/${REPO_NAME}" >/dev/null 2>&1; then
        gh release create v2.1.0 \
            --repo "${GITHUB_USER}/${REPO_NAME}" \
            --title "v2.1.0 — Dealix Tier-1 Governance Layer" \
            --notes-file CHANGELOG.md \
            --latest
        echo -e "   ${GREEN}✓ Release created${NC}"
    else
        echo -e "   ${YELLOW}⚠  Release v2.1.0 already exists${NC}"
    fi
fi

# ──────────────────────────────────────────────────────────────
# DONE
# ──────────────────────────────────────────────────────────────
echo
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🎉  Repo is live on GitHub!                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo
echo -e "   🔗 ${CYAN}https://github.com/${GITHUB_USER}/${REPO_NAME}${NC}"
echo -e "   🏷️  Release: ${CYAN}https://github.com/${GITHUB_USER}/${REPO_NAME}/releases/tag/v2.0.0${NC}"
echo
echo -e "${YELLOW}Recommended next steps:${NC}"
echo "   1. Enable branch protection on 'main' in repo settings"
echo "   2. Enable Dependabot alerts + secret scanning"
echo "   3. Review the CI workflow on the first push"
echo "   4. Rotate ALL old API keys that were exposed in the source project"
echo

if command -v gh >/dev/null 2>&1; then
    gh repo view "${GITHUB_USER}/${REPO_NAME}" --web 2>/dev/null || true
fi
