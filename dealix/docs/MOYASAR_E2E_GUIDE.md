# Dealix — Moyasar E2E Pilot Guide (G2 Gate)

**الهدف:** pilot 1 SAR test من البداية للنهاية، يفتح G2 + O3 بنفس الجلسة.

---

## الخطوات (بالترتيب)

### الخطوة 1 — SSH للسيرفر

```bash
ssh -i ~/.ssh/dealix_deploy root@188.245.55.180
```

### الخطوة 2 — Deploy آخر PRs

```bash
cd /opt/dealix
git rev-parse HEAD > .last_good_sha
git pull origin main
.venv/bin/pip install -q -r requirements.txt
chmod +x scripts/ops/*.sh
systemctl restart dealix-api
sleep 5
curl -s http://127.0.0.1:8001/health/deep | python3 -m json.tool
```

### الخطوة 3 — توليد Webhook secret محلياً

```bash
# ضف هذا في ذهنك فقط — راح تستخدمه في الخطوة 4 + Moyasar dashboard
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo "Your webhook secret (save it, you'll register it in Moyasar too):"
echo "  $WEBHOOK_SECRET"
```

### الخطوة 4 — تحديث `.env`

```bash
# backup first
cp /opt/dealix/.env /opt/dealix/.env.bak.$(date +%Y%m%dT%H%M%SZ)

# افتح nano
nano /opt/dealix/.env
```

أضف هذي السطور (أو حدّث لو موجودة):

```env
# PostHog (US Cloud — project 394094)
POSTHOG_API_KEY=phc_YOUR_POSTHOG_KEY_HERE
POSTHOG_HOST=https://us.i.posthog.com

# Moyasar (Test mode — switch to sk_live_ only after pilot success)
MOYASAR_SECRET_KEY=sk_test_<NEW_FROM_DASHBOARD_AFTER_REGENERATE>
MOYASAR_WEBHOOK_SECRET=<WEBHOOK_SECRET_FROM_STEP_3>

# App URL (used in Moyasar callback_url)
APP_URL=https://dealix.me
```

احفظ (`Ctrl+O, Enter, Ctrl+X`).

### الخطوة 5 — تسجيل Webhook في Moyasar Dashboard

1. ادخل https://dashboard.moyasar.com/webhooks
2. اضغط "إضافة webhook جديد" / "Add Webhook"
3. **URL:** `https://dealix.me/api/v1/webhooks/moyasar`
   - ⚠️ لو dealix.me DNS مو مضبوط، استخدم: `http://188.245.55.180/api/v1/webhooks/moyasar` مؤقتاً
4. **Secret:** ألصق نفس `$WEBHOOK_SECRET` من الخطوة 3
5. **Events:** اختر:
   - ☑️ `payment_paid`
   - ☑️ `payment_failed`
   - ☑️ `invoice_paid`
6. احفظ

### الخطوة 6 — إعادة تشغيل API

```bash
systemctl restart dealix-api
sleep 5
systemctl status dealix-api | head -10
```

### الخطوة 7 — Verify /pricing/plans public

```bash
curl -s http://127.0.0.1:8001/api/v1/pricing/plans | python3 -m json.tool
```

**المتوقع:** starter (999), growth (2999), scale (7999) — بدون pilot_1sar.

### الخطوة 8 — تشغيل pilot E2E test

```bash
export API_KEY=$(grep '^API_KEYS=' /opt/dealix/.env | cut -d= -f2- | tr -d '"' | cut -d, -f1)
export API_BASE=http://127.0.0.1:8001
bash /opt/dealix/scripts/ops/moyasar_pilot_test.sh
```

السكريبت:
1. يتحقق من الـ .env
2. ينشئ invoice 1 SAR
3. يطبع payment URL → **افتحه في المتصفح وادفع بـ test card**
4. Test card: `4111 1111 1111 1111`, expiry أي تاريخ مستقبلي, CVV أي 3 أرقام
5. يتحقق من وصول webhook + idempotency + PostHog event

---

## التحقق بعد النجاح

### في PostHog Dashboard
- ادخل https://us.posthog.com/project/394094/activity/explore
- فلتر: `event = "checkout started"` أو `"payment succeeded"`
- لازم تشوف event بـ `distinct_id=pilot_<timestamp>`

### في Moyasar Dashboard
- ادخل https://dashboard.moyasar.com/payments
- ستشوف invoice الـ 1 SAR بحالة "paid"

### Logs السيرفر
```bash
journalctl -u dealix-api --since "5 minutes ago" --no-pager | \
  grep -E "moyasar_webhook|posthog|payment"
```

---

## لو شي فشل

| المشكلة | الحل |
|---|---|
| `/pricing/plans` 401/500 | PR #55 ما انتشر. ارجع للخطوة 2 |
| `moyasar_invoice_failed` في logs | `MOYASAR_SECRET_KEY` غلط في `.env` |
| `moyasar_webhook_bad_signature` | `MOYASAR_WEBHOOK_SECRET` في `.env` مختلف عن المسجّل في Moyasar |
| webhook ما وصل | DNS مو مضبوط، أو port 443 مقفل، أو nginx ما يوجّه `/api/v1/webhooks/moyasar` |
| PostHog event ما ظهر | Check `POSTHOG_HOST=https://us.i.posthog.com` (مش eu) |

### Rollback لو شي كسر

```bash
sudo bash /opt/dealix/scripts/ops/rollback_drill.sh --dry-run  # check
sudo CONFIRM=YES bash /opt/dealix/scripts/ops/rollback_drill.sh --real
```

---

## بعد النجاح — Gates Progression

| قبل | بعد |
|---|---|
| 18/30 | **22/30** |
| G2 🚫 Blocked | G2 ✅ |
| O3 🚫 Blocked | O3 ✅ |
| T5 🟡 Partial | T5 ✅ (webhook E2E verified) |
| G1 🟡 Partial | G1 ✅ (pricing public verified in prod) |

**الخطوة التالية بعد Success:** تكرار مع Calendly + HubSpot لـ G3 (يحتاج token صحيح من Private App)، أو البدء بجمع leads حقيقيين لـ G4.
