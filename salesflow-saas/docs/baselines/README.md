# Performance & Accessibility Baselines

> Every future "faster than X" or "WCAG compliant" claim must reference a file in this directory.

## Contents

| File pattern | Produced by | Update frequency |
|--------------|-------------|------------------|
| `perf_YYYYMMDD.json` | `k6 run infra/load-tests/baseline.js` | Monthly + before each release |
| `a11y_YYYYMMDD.json` | `pnpm run test:a11y` (Playwright + axe) | Monthly + before each release |

## Interpretation

### Performance (V006)
- Source: k6 stages → 10 → 50 → 200 VUs over 5 minutes
- Target: p95 golden_path <2s, weekly_pack <1.5s, approval_center <800ms
- Error budget: <1%

### Accessibility (V007)
- Source: axe-core via @axe-core/playwright
- Target: 0 violations on routes: `/`, `/login`, `/deals`, `/approvals`, `/executive-room`
- Checks both LTR (en) and RTL (ar) layouts

## Rule

- **Never** cite performance or a11y numbers from memory, screenshots, or CI badges.
- Reference the JSON file in commit messages, marketing claims, security questionnaires, customer demos.
- If claiming an improvement, include the baseline JSON **and** the new JSON in the PR.

## Current baselines

*(Empty until V006 + V007 first runs. Do not claim perf/a11y numbers until populated.)*
