# Follow-Up Engine

## Purpose
The anti-leakage engine. Makes lost follow-ups difficult, late responses visible, and conversation gaps operationally trackable.

## Follow-Up Triggers

| Trigger | Action | Timing |
|---------|--------|--------|
| New lead, no response | Alert assigned agent + auto-sequence | After first_response SLA |
| Meeting completed | Create follow-up task | Immediately |
| Proposal sent, no response | Send follow-up message | After 24h, 72h, 7d |
| Deal stale in stage | Alert + suggest next action | After stage_max SLA |
| Customer inactive | Reactivation sequence | After 30/60/90 days |
| Lead replied | Pause sequence + alert agent | Immediately |

## Follow-Up Queue (Agent View)

### Dashboard: "مهام المتابعة"
```
Priority | Contact | Type | Due | Source
──────────────────────────────────────────────
🔴 Urgent | أحمد محمد | SLA Breach - No Response | Overdue 2h | New lead from website
🟡 High | سارة أحمد | Proposal Follow-up | Due today | Sent 3 days ago
🟢 Normal | محمد خالد | Post-Meeting Follow-up | Due tomorrow | Meeting yesterday
🔵 Low | فهد العمري | Reactivation | Due next week | Inactive 60 days
```

### Queue Data Contract
```json
{
  "items": [
    {
      "id": "uuid",
      "priority": "urgent",
      "contact_name": "أحمد محمد",
      "contact_phone": "+966501234567",
      "follow_up_type": "sla_breach",
      "due_at": "2026-03-29T10:00:00Z",
      "overdue_minutes": 120,
      "context": "New lead from Google Ads, no response in 3 hours",
      "suggested_action": "Call or WhatsApp immediately",
      "entity_type": "lead",
      "entity_id": "uuid"
    }
  ],
  "total": 15,
  "overdue": 3
}
```

## Reactivation System

### Dormant Lead Detection
```
Leads WHERE:
  status NOT IN ("converted", "lost")
  AND last activity > 30 days ago
  AND NOT in active sequence
  AND NOT suppressed
```

### Reactivation Sequence Template
```
Day 0: "مرحباً {name}، تواصلنا سابقاً بخصوص {service}. هل لا زلت مهتم؟"
Day 3: (if no reply) "عندنا عرض جديد ممكن يفيدك..."
Day 7: (if no reply) AI-generated personalized message based on original interest
Day 14: (if no reply) Final touch: "نحترم وقتك. إذا تحتاج مساعدة مستقبلاً لا تتردد"
→ If no reply after day 14: mark as "dormant", remove from active follow-up
```

## No-Response Detection

### Timer Logic
```python
def check_no_response(conversation):
    if conversation.status == "open":
        last_outbound = get_last_outbound_message(conversation.id)
        if last_outbound and not has_inbound_after(conversation.id, last_outbound.created_at):
            hours_since = (now - last_outbound.created_at).total_hours()
            if hours_since > sla_policy.follow_up_minutes / 60:
                create_follow_up_task(conversation)
                if sla_policy.escalation_enabled:
                    escalate(conversation)
```

## Worker Architecture

| Worker | Frequency | Responsibility |
|--------|-----------|---------------|
| `sequence_worker` | Every 60s | Execute sequence steps |
| `sla_check_worker` | Every 5min | Detect SLA breaches |
| `follow_up_worker` | Every 15min | Generate follow-up tasks from no-response |
| `reactivation_worker` | Daily | Detect dormant leads, enroll in reactivation |
| `reminder_worker` | Every 5min | Send appointment reminders |

## Idempotency & Failure

- Each worker run is idempotent (safe to re-run)
- Failed message sends: retry 3x with exponential backoff
- Failed step: mark enrollment as "error", alert operator
- Duplicate detection: check if step already executed for this enrollment + step combo
