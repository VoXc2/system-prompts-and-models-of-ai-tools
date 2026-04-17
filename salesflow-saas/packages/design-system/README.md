# Dealix Design System

> **Status**: Foundation scaffolded (Phase 2 TASK-F201)  
> **Owner**: Design + Frontend Platform team

---

## Structure

```
packages/design-system/
├── tokens/
│   ├── primitive.json      # Raw values (colors, spacing, radius, motion, typography)
│   ├── semantic.json       # Intent-based (surface, fg, border, interactive, status)
│   └── component.json      # (future) Per-component tokens
├── primitives/             # (future) Button, Input, Card, Dialog
├── patterns/               # (future) ApprovalCard, EvidenceTimeline
├── layouts/                # (future) Shell, Split, Command
├── motion/                 # (future) Framer Motion variants
└── docs/                   # (future) Storybook stories
```

---

## Token Design Principles

### 1. Primitive → Semantic → Component
Never reference primitives directly in components. Always go through semantic tokens.

```tsx
// ❌ Wrong
<div style={{ color: 'hsl(var(--color-neutral-900))' }} />

// ✓ Right
<div style={{ color: 'hsl(var(--fg-primary))' }} />
```

### 2. Arabic adjustments are first-class
- `typography.fontSize.arabic-adjustment`: multiply Latin sizes by 1.15 for Arabic
- `typography.lineHeight.arabic`: 1.8 for diacritic-heavy text
- Arabic font stack defaults to IBM Plex Sans Arabic with Tajawal fallback

### 3. Motion respects reduced-motion
Every motion token is used through utilities that check `prefers-reduced-motion`.

### 4. Dark mode is not a retrofit
Light + dark semantic layers defined in parallel in `semantic.json`.

---

## Integration (Phase 2)

Once scaffolded:
1. Install Style Dictionary: `pnpm add -D style-dictionary`
2. Build tokens to CSS + TS: `pnpm tokens:build`
3. Import in app: `import '@dealix/design-system/tokens.css'`

---

## Standards

- **W3C Design Tokens Community Group** format (`$value`, `$type`)
- **Tokens Studio** compatible for Figma ↔ code round-trip
- **CSS custom properties** output with `--` prefix per theme

---

## Phase 2 Roadmap

| Task | Status | Notes |
|------|--------|-------|
| TASK-F201 — Tokens | SCAFFOLDED | primitive + semantic done |
| TASK-F210 — Typography | — | Arabic-first type scale |
| TASK-F211 — RTL layout | — | Logical CSS properties |
| TASK-F240 — Motion | — | Framer Motion variants |
| TASK-F270 — ApprovalCard | — | Signature pattern |
| TASK-F280 — Themes | — | Light/dark/high-contrast/white-label |

See `DEALIX_PHASE2_BLUEPRINT.md` for full roadmap.
