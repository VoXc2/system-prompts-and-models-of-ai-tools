# Founder Decision Package — Dealix Tier-1

> **Purpose**: Everything the founder needs to make 4 decisions and unblock full execution.  
> **All code automation is DONE.** Only these decisions remain.

---

## Decision 1: GitHub Organization Name (5 min)

### Options
| Option | Pro | Con |
|--------|-----|-----|
| `dealix-io` | Clean, aligns with dealix.io domain | Standard |
| `dealix-hq` | Professional, enterprise feel | Less common |
| `dealix` | Shortest, clean | May be taken |
| `getdealix` | Matches marketing convention | Longer |

### Recommendation
`dealix-io` — matches the typical domain/org pattern, easy to communicate, unambiguous.

### Action
```bash
# After creating GitHub org `dealix-io` and empty private repo `dealix-io/platform`:
cd /home/user/system-prompts-and-models-of-ai-tools
./salesflow-saas/scripts/extract_dealix_repo.sh git@github.com:dealix-io/platform.git
```

---

## Decision 2: Company Entity Structure (this week)

### Options

| Option | Pro | Con | Estimated cost |
|--------|-----|-----|---------------|
| **MISA Startup License (KSA)** | Saudi-first customers prefer local entity; Vision 2030 alignment; PDPL compliance easier | Requires Saudi founder/partner for some structures; 100% foreign allowed in many sectors now | ~15-30K SAR setup |
| **DIFC (UAE)** | Strong IP protection; easier banking; common-law courts; international-friendly | Not "Saudi-first" for KSA sales; distance from market | ~50-100K AED setup |
| **ADGM (UAE)** | Similar to DIFC but often faster | Same "not Saudi" issue | ~50-100K AED setup |
| **Two-entity structure (KSA + UAE)** | Best of both | Complex; more cost | 70-130K total |

### Recommendation
**MISA Startup License** if founder is Saudi or has Saudi partner. **DIFC** if founder is foreign and speed matters more than local presence.

### Action
Engage one of these:
1. **TAM (Saudi)** — https://tamkeentech.net (Saudi startup formation)
2. **Diligents** — KSA/GCC legal formations
3. **DIFC Authority** — self-service if DIFC route

Expected timeline: 4-12 weeks.

---

## Decision 3: Saudi Legal Counsel (this month)

Saudi privacy policy + ToS + DPA review is **mandatory** before customer-facing launch.

### Recommended Firms (by specialization)

| Firm | Strength | Fit |
|------|----------|-----|
| **Al Tamimi & Company** | Largest KSA + GCC practice | Best for enterprise contracts + IP |
| **Clyde & Co (Riyadh)** | Strong in tech + data | Good PDPL expertise |
| **Bird & Bird (Riyadh)** | International, tech-focused | Good for cross-border |
| **Nowfal Law Firm** | Saudi boutique, fast | Cost-effective for startups |

### Scope to Request
1. Review + customize `docs/legal/templates/PRIVACY_POLICY_EN.md`
2. Review + customize `docs/legal/templates/TERMS_OF_SERVICE_EN.md`
3. Review + customize `docs/legal/templates/DPA_EN.md`
4. Review + customize `docs/legal/templates/PRIVACY_POLICY_AR.md`
5. Create Arabic versions of ToS + DPA
6. Verify Saudi PDPL compliance (especially cross-border transfers)
7. Create IP assignment agreement final version
8. One-hour consult on entity structure if not yet decided

**Budget**: 15-30K SAR for full scope.

---

## Decision 4: Trademark Filing (this month)

### Marks to File
- "DEALIX" (Latin)
- "ديلكس" (Arabic)
- Logo (once finalized)

### Classes
- 9 (software)
- 42 (SaaS)
- 35 (business services)

### Jurisdictions (priority order)
1. **KSA (SAIP)** — 5,000 SAR/class, file this week
2. **UAE** — 5,500 SAR/class, file within 30 days
3. **Egypt, Jordan, Kuwait** — within 90 days

### Recommended Agent
**Abu-Ghazaleh Intellectual Property (AGIP)** — largest MENA IP firm, handles all GCC in one engagement.

**Total budget**: ~90-120K SAR across all MENA jurisdictions.

### Self-Serve Alternative (KSA only)
Founder can file directly at https://qima.saip.gov.sa — save ~2-4K SAR per filing but slower learning curve.

---

## What's Already Automated (no decisions needed)

- ✓ Extraction script ready: `scripts/extract_dealix_repo.sh`
- ✓ Python deps pinned + pyproject.toml for uv
- ✓ Node deps pinned to pnpm@9.12.0
- ✓ Pre-commit hooks: gitleaks + detect-private-key + ruff
- ✓ Secret scan completed (1 false positive, documented)
- ✓ Rotation log template
- ✓ Legal status tracker
- ✓ Legal templates (IP Assignment, Privacy EN+AR, ToS, DPA)
- ✓ Trademark filing kit with application text
- ✓ Truth registry + claims registry + validator + CI
- ✓ Release readiness gate (blueprint-spec)
- ✓ Architecture brief (40/40) + Release readiness matrix (53/53)
- ✓ Golden path, Saudi workflow, 17 structured schemas, RLS migration, idempotency, OpenTelemetry, durable execution

---

## Total Founder Time to Unblock Full Execution

| Decision | Time required |
|----------|--------------|
| GitHub org name | 5 minutes |
| Entity structure | 2-4 hours research + engagement |
| Counsel engagement | 2-3 meetings + 15-30K SAR |
| Trademark filing | 1-2 hours with agent + 15-30K SAR |
| **Total founder time** | **~1 week of attention + ~50K SAR initial outlay** |

After these decisions, Phase 1 is truly complete and Phase 2 can begin.
