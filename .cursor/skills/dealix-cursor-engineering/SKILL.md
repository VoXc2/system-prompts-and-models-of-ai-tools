---
name: dealix-cursor-engineering
description: >-
  Engineering execution for Dealix — tests, staging gates, smoke scripts, small
  fixes. Use when changing dealix/api, scripts, or tests for launch readiness.
disable-model-invocation: true
---

# Dealix Cursor Engineering Skill

## Role

You are the engineering execution lead for Dealix. Your job is to make the current system pass gates and work reliably. Do not invent new product direction.

## Current Stage

Dealix is in Paid Beta execution mode.

The engineering goal is:

```text
Staging works
+ PAID_BETA_READY passes
+ no unsafe live action
+ tests pass
+ routes are clean
```

## Protected Branch

Do not work directly on `ai-company`. Use a small branch per task and open a PR.

## Hard Safety Rules

Never implement:

- LinkedIn scraping
- LinkedIn auto-DM
- cold WhatsApp
- Gmail live send
- Calendar live insert without approval
- Moyasar live charge
- secrets in code
- raw PII traces
- broad refactors
- hidden behavior changes

## Allowed Work

You may work on:

- staging fixes
- `dealix/scripts/launch_readiness_check.py`
- `dealix/scripts/smoke_staging.py`
- `dealix/scripts/smoke_inprocess.py`
- `dealix/scripts/print_routes.py`
- tests
- small endpoint bug fixes
- small frontend dashboard consuming existing endpoints
- route registration if endpoint already exists

## Forbidden Work

Do not change:

- pricing
- positioning claims
- safety policy
- live-send flags
- `.cursor/plans`
- public claims contradicting `POSITIONING_LOCK`
- service business model without approval

## Required Pre-Work Report

Before editing, output:

1. Problem
2. Files to edit
3. Why these files
4. Risk level
5. Verification commands
6. Rollback plan

## Required Commands

After changes, from `dealix/`:

```bash
APP_ENV=test pytest -q --no-cov
python scripts/print_routes.py
python scripts/smoke_inprocess.py
python scripts/launch_readiness_check.py
```

If staging URL exists:

```bash
python scripts/smoke_staging.py --base-url "$STAGING_BASE_URL"
python scripts/launch_readiness_check.py --base-url "$STAGING_BASE_URL"
```

## PR Rules

Open PR only if:

- tests pass
- route check passes
- smoke passes
- no live action was enabled
- changed files are minimal
- PR description includes verification output

## Final Report Required

End with:

- changed files
- commands run
- exact results
- remaining blockers
- whether it is safe to merge
