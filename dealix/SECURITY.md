# Security Policy | سياسة الأمن

## 🛡️ Supported versions

| Version | Supported |
| ------- | --------- |
| 2.x     | ✅         |
| 1.x     | ❌ (EOL)   |

## 🐛 Reporting a vulnerability

**Please do NOT open a public issue for security vulnerabilities.**

Instead, report them privately via:

- **Email**: security@ai-company.sa
- **GitHub Security Advisories**: [Open a private advisory](../../security/advisories/new)

Include:
1. A description of the vulnerability.
2. Steps to reproduce.
3. Potential impact.
4. Any suggested fixes.

We aim to acknowledge within **48 hours** and provide a resolution timeline within **7 days**.

## 🔒 Security features in this project

- **Config**: all secrets loaded from `.env` via `pydantic-settings` with `SecretStr`.
- **Secret scanning**: `gitleaks` + `detect-secrets` + `trufflehog` in pre-commit AND CI.
- **Dependency scanning**: Dependabot weekly + `bandit` Python security linter.
- **Docker**: non-root user, multi-stage build, minimal base image.
- **Webhooks**: HMAC-SHA256 signature verification (WhatsApp).
- **LinkedIn integration**: disabled by default (ToS compliance).

## 🔑 Key rotation guidance

If you believe a key has been exposed:

1. **Immediately** rotate the key in the provider's dashboard:
   - Anthropic Console → API Keys → regenerate
   - DeepSeek, Groq, GLM, Google, OpenAI: regenerate in respective consoles
   - HubSpot, Resend, SendGrid: regenerate
   - WhatsApp Business: regenerate access token
2. Update `.env` with the new key.
3. Redeploy.
4. Check GitHub → Settings → Secret scanning alerts.
5. Run `gitleaks detect --source . --report-format json` to scan history.

## ✅ Pre-commit checklist for maintainers

Before merging any PR:
- [ ] `gitleaks` pre-commit hook passed
- [ ] No new files in `.env*` except `.env.example`
- [ ] No new domain-specific secrets in `core/` or `integrations/`
- [ ] All new integrations use `settings.*_api_key.get_secret_value()` pattern

---

## 🇸🇦 بالعربية

### الإبلاغ عن ثغرات

**لا تفتح issue عام للثغرات الأمنية.** أرسل إلى: **security@ai-company.sa**

نهدف للرد خلال ٤٨ ساعة وتقديم جدول زمني للحل خلال ٧ أيام.

### تدوير المفاتيح

إذا تسرّب مفتاح:
1. **فوراً** دوّر المفتاح من لوحة المزود.
2. حدّث `.env`.
3. أعد النشر.
4. افحص تنبيهات GitHub secret scanning.
