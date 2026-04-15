# Figma Make

A community **prompt chain** for building full websites end-to-end with **Claude Opus 4.6** (architecture/logic) and **Figma Make** (pixel-perfect UI + publishing).

> This folder does **not** contain the Figma Make system prompt. It contains a user-facing workflow — a sequence of 9 role-based prompts — that you run with Claude + Figma Make to ship a production-grade website in a single session.

## Files

| File | What it is |
|---|---|
| [`Website Builder Prompt Chain.md`](./Website%20Builder%20Prompt%20Chain.md) | The 9 prompts verbatim, in order, with role, inputs, and hand-off notes |
| [`examples/saas-landing-brief.md`](./examples/saas-landing-brief.md) | A worked example — a filled-in brief for a SaaS landing page, showing how the `[BRACKETS]` get resolved in practice |

## Stack

- **Claude Opus 4.6** — architecture, logic, content, QA (prompts 1, 3, 4, 8, 9)
- **Figma Make** — visual design, responsive, motion, publishing (prompts 2, 5, 6, 7)

## Claim

Author [@_TALEBM_](https://x.com/_TALEBM_) reports building a ~$5,000-value site for a client in **118 minutes** using this exact chain. ~100 prompts were tested before distilling these 9.

## Credits

Chain © [@_TALEBM_](https://x.com/_TALEBM_) — X thread dated 28/03/2026.
Archived here with attribution.
