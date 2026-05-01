#!/usr/bin/env bash
# ============================================================
# Dealix Deploy Bundle v2 — النشر الموحّد (Moyasar + PostHog + Calendly)
#
# الاستخدام:
#   1. ضع المفاتيح في /opt/dealix/.env.secrets قبل تشغيل السكريبت
#      (يمكن نسخها من الرسالة في محادثة Computer)
#   2. bash /opt/dealix/scripts/ops/deploy_bundle_v2.sh
# ============================================================
set -euo pipefail

REPO_DIR="/opt/dealix"
ENV_FILE="$REPO_DIR/.env"
SECRETS_FILE="$REPO_DIR/.env.secrets"
SERVICE="dealix-api"

if [ ! -f "$SECRETS_FILE" ]; then
  cat <<'EOF'
━━━ خطأ: ملف الأسرار مفقود ━━━
أنشئ /opt/dealix/.env.secrets أولاً بالمحتوى التالي (احصل على المفاتيح من محادثة Computer):

POSTHOG_API_KEY=phc_...
POSTHOG_HOST=https://us.i.posthog.com
POSTHOG_ENABLED=true
MOYASAR_PUBLIC_KEY=pk_live_...
MOYASAR_SECRET_KEY=sk_live_...
CALENDLY_WEBHOOK_SECRET=...
CALENDLY_OAUTH_CLIENT_ID=...
CALENDLY_OAUTH_CLIENT_SECRET=...
CALENDLY_PAT=...
APP_URL=https://dealix.me

استخدم:
  nano /opt/dealix/.env.secrets
  chmod 600 /opt/dealix/.env.secrets
  bash /opt/dealix/scripts/ops/deploy_bundle_v2.sh
EOF
  exit 1
fi

echo "━━━ [1/7] تحديث الكود من GitHub ━━━"
cd "$REPO_DIR"
git fetch origin main
CURRENT=$(git rev-parse HEAD)
echo "الـ HEAD الحالي: $CURRENT"
git checkout main
git pull origin main --ff-only
NEW_HEAD=$(git rev-parse HEAD)
echo "الـ HEAD الجديد: $NEW_HEAD"
echo "$CURRENT" > "$REPO_DIR/.last_good_sha"

echo ""
echo "━━━ [2/7] تحديث متغيرات البيئة ━━━"
cp "$ENV_FILE" "$ENV_FILE.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null || touch "$ENV_FILE"

# ولّد MOYASAR_WEBHOOK_SECRET إذا غير موجود
if ! grep -q "^MOYASAR_WEBHOOK_SECRET=" "$ENV_FILE" 2>/dev/null; then
  MOYASAR_WH=$(openssl rand -hex 32)
  echo "MOYASAR_WEBHOOK_SECRET=$MOYASAR_WH" >> "$ENV_FILE"
  echo "✔ ولّدت MOYASAR_WEBHOOK_SECRET جديد"
  echo "  ⚠ سجّله في Moyasar dashboard: $MOYASAR_WH"
fi

# دمج المفاتيح من .env.secrets
upsert_env() {
  local key="$1"; local val="$2"
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    # استخدام `|` كفاصل بدل `/` لتجنب المشاكل مع URLs
    local esc_val
    esc_val=$(printf '%s\n' "$val" | sed 's/[&|]/\\&/g')
    sed -i "s|^${key}=.*|${key}=${esc_val}|" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

# قراءة السطور من secrets وتحديث .env
while IFS='=' read -r key val; do
  [[ -z "$key" || "$key" =~ ^# ]] && continue
  upsert_env "$key" "$val"
done < "$SECRETS_FILE"

chmod 600 "$ENV_FILE"
echo "✔ .env محدّث (صلاحيات 600)"

echo ""
echo "━━━ [3/7] تثبيت deps إذا تغيرت ━━━"
if [ -f pyproject.toml ]; then
  pip install -e . 2>&1 | tail -3 || true
fi

echo ""
echo "━━━ [4/7] تشغيل migrations ━━━"
if command -v alembic &>/dev/null && [ -f alembic.ini ]; then
  alembic upgrade head 2>&1 | tail -5 || echo "⚠ لا يوجد migrations جديدة"
fi

echo ""
echo "━━━ [5/7] إعادة تشغيل الخدمة ━━━"
systemctl restart "$SERVICE"
sleep 3
systemctl status "$SERVICE" --no-pager | head -10

echo ""
echo "━━━ [6/7] فحص صحة API ━━━"
sleep 2
curl -sf http://localhost:8000/healthz && echo "" || echo "⚠ /healthz لم يستجب"
curl -sf http://localhost:8000/readyz && echo "" || echo "⚠ /readyz لم يستجب"

echo ""
echo "━━━ [7/7] ملخص ━━━"
echo "  HEAD: $NEW_HEAD"
echo "  Service: $(systemctl is-active $SERVICE)"
echo ""
MOYASAR_WH_CUR=$(grep ^MOYASAR_WEBHOOK_SECRET= "$ENV_FILE" | cut -d= -f2-)
echo "═══ الخطوات التالية ═══"
echo "1. سجل webhook Moyasar: https://dashboard.moyasar.com/webhooks"
echo "   URL:    https://dealix.me/api/v1/webhooks/moyasar"
echo "   Secret: $MOYASAR_WH_CUR"
echo ""
echo "2. شغل pilot test (1 SAR):"
echo "   bash /opt/dealix/scripts/ops/moyasar_pilot_test.sh"
echo ""
echo "3. تحقق من events في PostHog:"
echo "   https://us.posthog.com/project/394094/activity/explore"
echo ""
echo "✔ انتهى النشر"

# حذف الأسرار المؤقتة (آمن)
shred -u "$SECRETS_FILE" 2>/dev/null || rm -f "$SECRETS_FILE"
echo "✔ تم حذف /opt/dealix/.env.secrets بعد الدمج"
