# Dealix — Deploy Checklist (لسامي)

**متى تستخدم هذا:** بعد ما ينمرج PR جديد للـ main، تبي تنشر للإنتاج.

**السيرفر:** `ssh -i ~/.ssh/dealix_deploy root@188.245.55.180`
**المسار:** `/opt/dealix`
**الخدمة:** `systemctl status dealix-api`

---

## 🟢 Deploy routine (after PR merge)

```bash
# 1. SSH
ssh -i ~/.ssh/dealix_deploy root@188.245.55.180

# 2. Record the current good SHA (only if current is known-stable)
cd /opt/dealix
CURRENT_SHA=$(git rev-parse --short HEAD)
echo "Current: $CURRENT_SHA"
# If you want to mark this as last-good BEFORE the new deploy:
# git rev-parse HEAD > .last_good_sha

# 3. Pull latest
git fetch origin
git pull origin main

# 4. Update dependencies
.venv/bin/pip install -q -r requirements.txt

# 5. Restart service
systemctl restart dealix-api
sleep 5

# 6. Verify health
curl -s http://127.0.0.1:8001/health/deep | jq .
# Expect: postgres green, redis green, llm_providers=[groq,openai]

# 7. Smoke test new endpoints
export API_KEY="$(grep '^API_KEYS=' /opt/dealix/.env | cut -d= -f2- | tr -d '"' | cut -d, -f1)"

# Pricing (should now be PUBLIC — no key needed after PR #55)
curl -s http://127.0.0.1:8001/api/v1/pricing/plans | jq .

# Approvals stats
curl -s -H "X-API-Key: $API_KEY" http://127.0.0.1:8001/api/v1/admin/approvals/stats

# DLQ stats
curl -s -H "X-API-Key: $API_KEY" http://127.0.0.1:8001/api/v1/admin/dlq/stats
```

**إذا أي خطوة فشلت:** ارجع إلى RUNBOOK Scenario 2 (rollback) وشغّل:
```bash
sudo bash /opt/dealix/scripts/ops/rollback_drill.sh --dry-run
```
إذا خطة الـ rollback صحيحة، نفّذ `--real` بـ `CONFIRM=YES`.

---

## 🔵 الـ deploy الجاي (PRs #55 و #58 مرج، ما زال ما انتشر)

الآن على الـ main:
- ✅ PR #54 (D0 hardening) — deployed على السيرفر (SHA `a2c7845`)
- 🔵 PR #55 (pricing public + middleware 401 fix) — merged، **ما زال ما انتشر**
- 🔵 PR #57 (docs: gates 16/30) — merged، docs فقط
- 🔵 PR #58 (drill scripts + SLO + on-call) — merged، scripts جديدة تحت `scripts/ops/`

### اللي راح يصير بعد الـ deploy:
1. `/api/v1/pricing/plans` يرد 200 بدون key (prospects يقدرون يشوفون الأسعار)
2. أي `/api/*` بدون key يرد **401** بدل 500 (UX أصح للـ clients)
3. `scripts/ops/*.sh` تصير متاحة للاستخدام

### Deploy steps:
```bash
ssh -i ~/.ssh/dealix_deploy root@188.245.55.180
cd /opt/dealix

# بدّل .last_good_sha للنقطة الحالية (a2c7845) قبل ما نستبدلها
git rev-parse HEAD > .last_good_sha
cat .last_good_sha  # should show a2c7845...

# Deploy
git pull origin main
.venv/bin/pip install -q -r requirements.txt
systemctl restart dealix-api
sleep 5

# Verify PR #55 fix worked
curl -s -o /dev/null -w "pricing public: %{http_code}\n" http://127.0.0.1:8001/api/v1/pricing/plans
# Expected: 200

curl -s -o /dev/null -w "checkout no-key: %{http_code}\n" http://127.0.0.1:8001/api/v1/checkout -X POST -H "Content-Type: application/json" -d '{}'
# Expected: 401 (NOT 500)

# Make scripts executable
chmod +x /opt/dealix/scripts/ops/*.sh
```

---

## 🟡 بعد الـ deploy مباشرة — شغل الـ drills

### T7 dry-run (آمن تمامًا — ما يغير شي):
```bash
sudo bash /opt/dealix/scripts/ops/rollback_drill.sh --dry-run
```
راح يطبع الخطوات بس بدون تنفيذ. راجع اللوق في `/var/log/dealix_rollback_drill.*.log`.

### T5 DLQ fault-injection (يضيف event واحد في DLQ ثم تقدر تنظّفه):
```bash
export API_KEY="$(grep '^API_KEYS=' /opt/dealix/.env | cut -d= -f2- | tr -d '"' | cut -d, -f1)"
export API_BASE="http://127.0.0.1:8001"
bash /opt/dealix/scripts/ops/dlq_fault_injection.sh

# تنظيف:
curl -X POST -H "X-API-Key: $API_KEY" "$API_BASE/api/v1/admin/dlq/webhooks/drain"
```

### T6 k6 (يحتاج تنصيب k6 أول مرة):
انظر `docs/DRILL_PLAN.md` لخطوات التنصيب، ثم:
```bash
sudo bash /opt/dealix/scripts/ops/run_k6_prod.sh
```

---

## 📌 الحالة بعد Deploy + Drills

لو نفذت Deploy + T5 + T6 + T7 dry-run بنجاح:

| Before | After |
|---|---|
| 18/30 gates closed | **21/30 gates closed** |
| G1 🟡 Partial | G1 ✅ verified in prod |
| T5 🟡 Partial | T5 ✅ fault-injection passed |
| T6 🔴 Open | T6 ✅ thresholds met |
| T7 🔴 Open | T7 ✅ rollback procedure validated |

**هذا يقربنا 3 gates من عتبة الإطلاق (24/30).**

الباقي 3 gates الي نحتاجها:
- أحد الـ credentials الأربعة (أسرعها PostHog → يفتح O3 ومعه O4 الـ alerts)
- T8 backup restore (يحتاج staging — أو نوثقها كـ blocker)
- واحد من commercial gates (G4 leads / G5 deal) — هذا رهينك
