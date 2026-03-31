# Dealix (ديل اي اكس) — Production .env Checklist

> قائمة شاملة لكل متغير في ملف البيئة الإنتاجي
> Last updated: 2026-03-31

---

## Critical Rules / قواعد حاسمة

1. **NEVER commit `.env` to git** — it must be in `.gitignore`
2. **NEVER reuse development secrets in production**
3. **Store a backup copy** in a secure password manager (1Password, Bitwarden)
4. **Rotate secrets** if any team member leaves or a breach is suspected
5. **DEBUG must be False** — always, no exceptions

---

## Complete Variable Reference

### Database / قاعدة البيانات

| Variable | Example Value | Notes |
|---|---|---|
| `DB_NAME` | `dealix_prod` | Use a distinct name from dev/staging |
| `DB_USER` | `dealix_app` | NOT `postgres` — use limited-privilege user |
| `DB_PASSWORD` | `<random 32+ chars>` | Generate with `openssl rand -hex 32` |
| `DATABASE_URL` | `postgresql+asyncpg://dealix_app:<PW>@<HOST>:5432/dealix_prod` | Must point to production DB host |

- [ ] DB_NAME set to production database name
- [ ] DB_USER is NOT `postgres` superuser
- [ ] DB_PASSWORD is randomly generated (32+ characters)
- [ ] DATABASE_URL points to production host (not `localhost` or `db`)
- [ ] Database user has only necessary permissions (SELECT, INSERT, UPDATE, DELETE on app tables)

---

### Redis / ريدس

| Variable | Example Value | Notes |
|---|---|---|
| `REDIS_URL` | `redis://:password@redis-host:6379/0` | Use authentication in production |

- [ ] Redis has a password set (not open)
- [ ] REDIS_URL includes password
- [ ] Redis is not exposed to the internet (bind to internal IP)

---

### Security / الأمان

| Variable | Example Value | Notes |
|---|---|---|
| `SECRET_KEY` | `<random 64+ chars>` | Generate with `openssl rand -hex 64` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Short-lived access tokens |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Reasonable refresh window |

- [ ] SECRET_KEY is randomly generated with **64+ characters** minimum
  ```bash
  # Generate with:
  openssl rand -hex 64
  # or:
  python3 -c "import secrets; print(secrets.token_hex(64))"
  ```
- [ ] SECRET_KEY is **different** from any other environment
- [ ] Token expiration values are appropriate for production

---

### API & Frontend URLs

| Variable | Example Value | Notes |
|---|---|---|
| `API_URL` | `https://dealix.sa/api` | Must use HTTPS |
| `FRONTEND_URL` | `https://dealix.sa` | Must use HTTPS |

- [ ] Both URLs use `https://` (not `http://`)
- [ ] Both URLs use the production domain (not `localhost`)
- [ ] No trailing slashes

---

### CORS Configuration

- [ ] CORS allows ONLY the production frontend domain
- [ ] No wildcard (`*`) origins in production
- [ ] Credentials are allowed only for the production domain

---

### WhatsApp Business API

| Variable | Example Value | Notes |
|---|---|---|
| `WHATSAPP_API_TOKEN` | `EAA...` | From Meta Business Manager |
| `WHATSAPP_PHONE_NUMBER_ID` | `1234567890` | From WhatsApp Business dashboard |
| `WHATSAPP_BUSINESS_ACCOUNT_ID` | `9876543210` | From Meta Business Manager |
| `WHATSAPP_VERIFY_TOKEN` | `<random string>` | For webhook verification |

- [ ] All WhatsApp credentials are from the **production** Meta Business account
- [ ] Phone number is verified and approved for messaging
- [ ] Message templates are approved by Meta
- [ ] Webhook verify token is a unique random string
- [ ] If not yet available, leave empty (see LAUNCH-BLOCKERS.md)

---

### Email / البريد الإلكتروني

| Variable | Example Value | Notes |
|---|---|---|
| `EMAIL_PROVIDER` | `smtp` | or `sendgrid` |
| `SMTP_HOST` | `smtp.gmail.com` | Google Workspace SMTP |
| `SMTP_PORT` | `587` | TLS port |
| `SMTP_USER` | `noreply@dealix.sa` | Production email account |
| `SMTP_PASSWORD` | `<app-password>` | Google App Password, NOT account password |
| `SENDGRID_API_KEY` | `SG.xxx` | If using SendGrid for transactional |

- [ ] SMTP credentials are for the production email account
- [ ] Using App Password (not regular password) for Google Workspace
- [ ] SendGrid API key has restricted permissions (Mail Send only)
- [ ] Test email sends successfully before go-live

---

### SMS (Unifonic) / الرسائل النصية

| Variable | Example Value | Notes |
|---|---|---|
| `UNIFONIC_APP_SID` | `<from Unifonic dashboard>` | Production App SID |
| `UNIFONIC_SENDER_ID` | `Dealix` | Must be approved by Unifonic |

- [ ] Unifonic account is active and funded
- [ ] Sender ID "Dealix" is approved (requires approval in Saudi Arabia)
- [ ] Test SMS sends successfully to a Saudi number

---

### App Settings / إعدادات التطبيق

| Variable | Example Value | Notes |
|---|---|---|
| `APP_NAME` | `Dealix` | Do not change |
| `APP_NAME_AR` | `ديل اي اكس` | Do not change |
| `DEFAULT_TIMEZONE` | `Asia/Riyadh` | Saudi Arabia timezone |
| `DEFAULT_CURRENCY` | `SAR` | Saudi Riyal |
| `DEFAULT_LOCALE` | `ar` | Arabic first |

- [ ] Timezone is `Asia/Riyadh`
- [ ] Currency is `SAR`
- [ ] Locale is `ar`

---

### Additional Production Variables

| Variable | Example Value | Notes |
|---|---|---|
| `DEBUG` | `False` | **MUST be False in production** |
| `ALLOWED_HOSTS` | `dealix.sa,www.dealix.sa` | Comma-separated |
| `LOG_LEVEL` | `WARNING` | INFO for initial launch, WARNING for stable |
| `SENTRY_DSN` | `https://xxx@sentry.io/xxx` | Error tracking |

- [ ] DEBUG is explicitly set to `False`
- [ ] ALLOWED_HOSTS lists only production domains
- [ ] LOG_LEVEL is appropriate (INFO during launch week, WARNING after)
- [ ] SENTRY_DSN configured for error tracking

---

## Generation Script / سكربت التوليد

Use this to generate secure random values:

```bash
#!/bin/bash
echo "=== Dealix Production Secrets Generator ==="
echo ""
echo "SECRET_KEY=$(openssl rand -hex 64)"
echo "DB_PASSWORD=$(openssl rand -hex 32)"
echo "REDIS_PASSWORD=$(openssl rand -hex 24)"
echo "WHATSAPP_VERIFY_TOKEN=$(openssl rand -hex 16)"
echo ""
echo "=== Copy these into your .env file ==="
```

---

## Verification Checklist / قائمة التحقق النهائية

- [ ] All placeholder values replaced with real credentials
- [ ] No variable is empty (except optional ones marked as such)
- [ ] `.env` file is NOT in git (`git status` shows it's ignored)
- [ ] A secure backup of `.env` exists in password manager
- [ ] Backend starts without errors with production `.env`
- [ ] Health check passes: `curl https://dealix.sa/api/v1/health`
- [ ] No secrets appear in application logs
- [ ] No secrets are exposed in API responses

---

> تحذير: مشاركة ملف .env مع أي شخص غير مخول يعتبر خرقاً أمنياً خطيراً
> WARNING: Sharing the .env file with unauthorized persons is a critical security breach
