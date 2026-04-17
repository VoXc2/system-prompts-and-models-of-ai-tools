# Customer Friction Log

> One entry per friction. No aggregation, no editorializing. Raw source of truth.
> Head of CS owns; Founder reads weekly on Wednesday.
> **Rule**: entry written within 24h of the conversation. No exceptions.

---

## Entry Template (copy for each new entry)

```
### YYYY-MM-DD — [customer_short_name] — [short_title]

- **Reporter**: [dealix_team_member]
- **Customer role**: [CFO / COO / Sales Ops / Admin / End user]
- **Severity**: [P0 show-stopper | P1 major | P2 annoyance | P3 nice-to-have]
- **Theme tag**: [auth | arabic | approval | evidence | reporting | integration | perf | a11y | other]
- **Context** (1–2 sentences describing what customer was trying to do):

- **What they said** (direct quote when possible, Arabic OK):
  >

- **What actually happened** (observed behavior, steps to reproduce):

- **Workaround used (if any)**:

- **Linked GitHub issue / ticket**: #____

- **Status**: [open | in-progress | resolved | won't-fix-with-rationale]
```

---

## Entries

### [Seed — example of the format; delete on first real entry]

### 2026-04-17 — Example Retail Group — Approval Card Arabic RTL label truncation

- **Reporter**: Head of CS
- **Customer role**: CFO
- **Severity**: P2 annoyance
- **Theme tag**: arabic, a11y
- **Context**: CFO trying to approve a deal from mobile Safari in Arabic locale.
- **What they said**:
  > "الزر الأخضر يخفي نصف السطر العلوي. ما أقدر أقرأ اسم الصفقة."
- **What actually happened**: Approve button overlaps deal title in RTL at viewport <375px.
- **Workaround used**: Customer approved from desktop instead.
- **Linked GitHub issue / ticket**: #TBD
- **Status**: open (queued for Wave A)
