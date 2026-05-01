# Security Guide — Dealix v3.0.0

## الطبقات

### 1. Rate Limiting (slowapi)
- `api/security/rate_limit.py`
- حدود افتراضية:
  - `POST /api/v1/leads` → 10/min
  - `POST /api/v1/sales/*` → 30/min
  - `POST /api/v1/webhooks/whatsapp` → 100/min
  - باقي المسارات → 60/min
  - الحد الكلي لكل IP/key → 1000/min
- التخزين: `memory://` افتراضياً، Redis في الإنتاج عبر `RL_STORAGE_URI`

### 2. API Key Authentication
- `api/security/api_key.APIKeyMiddleware`
- يطلب رأس `X-API-Key` لكل مسارات `/api/*` باستثناء `/health*`, `/docs*`, `/webhooks/*`
- المفاتيح المسموح بها في متغير البيئة `API_KEYS` (مفصولة بفواصل)
- مقارنة ثابتة الزمن عبر `hmac.compare_digest`

### 3. Webhook Signatures
| المزود | Header | الخوارزمية |
|--------|--------|------------|
| HubSpot | `X-HubSpot-Signature-v3` | HMAC-SHA256 (method + url + body + timestamp) |
| Calendly | `Calendly-Webhook-Signature` | HMAC-SHA256 (t=ts + . + body) |
| n8n | `X-N8N-Signature` | HMAC-SHA256 (body) |

### 4. Secret Rotation
- `scripts/rotate_secrets.sh`
- يدور: `API_KEYS`, `HUBSPOT_APP_SECRET`, `CALENDLY_WEBHOOK_SECRET`, `N8N_WEBHOOK_SECRET`, `JWT_SECRET`, `DEALIX_INTERNAL_TOKEN`
- احتياط تلقائي لـ `.env.bak.YYYYMMDDTHHMMSSZ`

### 5. Infra Hardening
- `scripts/infra/ssh_harden.sh`: port 2222، مفاتيح فقط، fail2ban، UFW
- `scripts/infra/ssl_certbot.sh`: Let's Encrypt auto-renew
- `scripts/infra/backup_pg.sh`: نسخ احتياطي يومي بضغط gzip + استبقاء 14 يوم

### 6. CI/CD Security
- CodeQL للتحليل الثابت
- Trivy scan للحاويات (CRITICAL/HIGH)
- SBOM (SPDX-JSON) لكل بناء
- Dependabot أسبوعي (pip + actions + docker)
- pre-commit: ruff + mypy + bandit + gitleaks
