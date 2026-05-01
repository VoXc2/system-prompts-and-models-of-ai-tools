# WhatsApp Operator Flow — Design

## Message types

- **Session messages** — conversational text (Arabic).
- **Interactive (buttons)** — up to **3 reply buttons** per message (WhatsApp Cloud API limit).
- **Template messages** — for opt-in / utility (separate approval with Meta).

## Reply buttons

### Step 1 — Opportunity / brief

Suggested labels (Arabic):

- قبول → `opp:{id}:accept`
- تخطي → `opp:{id}:skip`
- رسالة → `opp:{id}:draft` (opens second step for message approval)

### Step 2 — After «رسالة»

- اعتماد → `msg:{draft_id}:approve`
- تعديل → `msg:{draft_id}:edit`
- إلغاء → `msg:{draft_id}:cancel`

## Payload examples

See `auto_client_acquisition/personal_operator/whatsapp_cards.py` — functions return JSON structures compatible with WhatsApp interactive `button` payloads. **No HTTP send** is performed in-repo.

## Webhook parse

Inbound events should map `button_reply.id` through `parse_button_reply()` to `{ kind, action, opportunity_id | draft_id }`.

## Decision mapping

| Button id suffix | Meaning |
|------------------|---------|
| `:accept` | Accept opportunity → draft path, still **approval_required**. |
| `:skip` | Skip; no outbound. |
| `:draft` | Prepare message draft → second step. |
| `:schedule` | Meeting draft only until calendar adapter + approval. |

## Opt-in requirement

- No **cold** WhatsApp to unknown contacts.
- Opt-in ledger + contactability checks (Compliance OS) before any template or session outbound.

## Failure cases

- More than 3 actions → use **second message** or list message.
- Unknown button id → log + safe default (no send).
- Rate limits / 131047 template issues → surface to operator UI.

## Testing checklist

- [ ] Payload never exceeds 3 buttons  
- [ ] IDs stable per opportunity / draft  
- [ ] Arabic labels render under 20 chars per button title where required  
- [ ] Webhook signature verification (future)  

## Staging checklist (webhook — عند التفعيل لاحقاً)

- [ ] Meta App + رقم هاتف تجريبي + **Verify Token** في env السيرفر فقط  
- [ ] `POST /webhook` (أو المسار المعتمد) يتحقق من توقيع `X-Hub-Signature-256`  
- [ ] **Feature flag** لأي إرسال فعلي: `WHATSAPP_ALLOW_LIVE_SEND` → `core.config.settings.whatsapp_allow_live_send` (الافتراضي **false**)  
- [ ] سجل opt-in قبل أي template تسويقي  
- [ ] اختبار أزرار 3+3 على جهاز حقيقي في sandbox  
- [ ] لا cold outreach في سيناريوهات الاختبار  

## Flow principle

**Accept / Skip / Draft** first; **Schedule** only after accept or draft path confirms intent.
