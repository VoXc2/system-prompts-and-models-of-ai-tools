# Live Deployment Guide — Client Installation Step-by-Step

> **هدف**: تركيب Dealix عند عميل حقيقي خلال 48 ساعة  
> **القاعدة**: ركّب فقط Revenue OS + Approval + Executive Dashboard. لا M&A. لا Expansion.

---

## Pre-Deployment Checklist (قبل يوم التركيب)

### من العميل (يجهزهم قبل)
- [ ] قائمة بأعضاء الفريق (الاسم، الإيميل، الدور)
- [ ] رقم WhatsApp Business أو رقم الشركة
- [ ] قائمة بـ 5-10 صفقات نشطة (اسم الشركة، القيمة، المرحلة)
- [ ] من يملك صلاحية الموافقة على الصفقات
- [ ] هل عندهم CRM حالي (اسمه)

### منك (جاهز مسبقًا)
- [ ] VPS/Cloud instance جاهز (Saudi region مفضّل)
- [ ] Domain configured (client.dealix.sa أو subdomain)
- [ ] SSL certificate
- [ ] WhatsApp Business API token
- [ ] `.env` file prepared

---

## Day 0: Infrastructure Setup (2-4 ساعات)

### Step 1: Deploy Stack
```bash
# Clone and configure
git clone <repo> && cd salesflow-saas
cp .env.example .env

# Edit .env with client-specific values
# CRITICAL: Change these
#   APP_NAME=ClientName
#   DATABASE_URL=postgresql+asyncpg://...
#   SECRET_KEY=<generate-random-64>
#   WHATSAPP_API_TOKEN=<client-token>
#   FRONTEND_URL=https://client.dealix.sa

# Launch
docker-compose up -d

# Verify
curl -s http://localhost:8000/api/v1/health | python -m json.tool
```

### Step 2: Initialize Database
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.seed_database
```

### Step 3: Create Tenant + Admin User
```bash
# Via API or direct DB
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@client.com",
    "password": "<secure>",
    "name": "Admin",
    "role": "admin",
    "language": "ar"
  }'
```

### Step 4: Verify Frontend
- Open `https://client.dealix.sa`
- Login with admin credentials
- Verify Arabic RTL layout
- Check dashboard loads

---

## Day 1: Data Import + Configuration (2-4 ساعات)

### Step 5: Import Existing Deals
```bash
# Prepare CSV: company,title,value,stage,assigned_to
# Map stages: new → discovery, negotiation → negotiation, etc.

curl -X POST http://localhost:8000/api/v1/leads/import \
  -H "Authorization: Bearer <token>" \
  -F "file=@leads.csv"
```

### Step 6: Configure Approval Flow
```bash
# Set approval SLA thresholds
# In .env:
OPENCLAW_APPROVAL_SLA_HOURS_WARN=8
OPENCLAW_APPROVAL_SLA_HOURS_BREACH=24
OPENCLAW_APPROVAL_ESCALATION_L3_MULTIPLIER=2.0
```

### Step 7: Setup WhatsApp Templates
- Configure approved templates in WhatsApp Business Manager
- Map templates to Dealix outreach sequences
- Test send to internal number first

### Step 8: Create Users
```bash
# For each team member
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sales@client.com",
    "name": "Mohammed",
    "role": "sales",
    "language": "ar"
  }'
```

### Step 9: Seed Compliance Controls
```bash
# Trigger compliance matrix seeding
curl -X POST "http://localhost:8000/api/v1/compliance/matrix/scan?tenant_id=<tid>"
```

---

## Day 1: Training Session (1 ساعة)

### Training Agenda (60 minutes)
| الوقت | الموضوع | الجمهور |
|-------|---------|---------|
| 0-10 | الدخول + لوحة التحكم | الكل |
| 10-20 | إضافة leads + صفقات | المبيعات |
| 20-30 | إرسال WhatsApp من النظام | المبيعات |
| 30-40 | الموافقات + SLA | المديرين |
| 40-50 | Executive Room | CEO/VP |
| 50-60 | أسئلة | الكل |

### Quick Reference Card (يُطبع للفريق)
```
🟢 أهم الأزرار:
  • Dashboard → لوحة التحكم
  • Leads → العملاء المحتملين
  • Deals → الصفقات
  • Approvals → الموافقات
  • Executive Room → غرفة القيادة

📱 WhatsApp:
  • الرسائل تطلع من النظام مباشرة
  • PDPL consent يتحقق تلقائيًا
  
✅ الموافقات:
  • تجيك إشعارات
  • SLA: 8 ساعات تحذير، 24 ساعة خرق
  • موافقة أو رفض بضغطة
```

---

## Day 2-14: Pilot Monitoring

### Daily Checks (15 دقيقة/يوم)
```bash
# Health check
curl -s http://localhost:8000/api/v1/health

# Executive snapshot
curl -s "http://localhost:8000/api/v1/executive-room/snapshot?tenant_id=<tid>" | python -m json.tool

# Approval SLA status
curl -s "http://localhost:8000/api/v1/approval-center/stats?tenant_id=<tid>" | python -m json.tool

# Compliance posture
curl -s "http://localhost:8000/api/v1/compliance/matrix/posture?tenant_id=<tid>" | python -m json.tool
```

### Weekly Review with Client (30 دقيقة)
| البند | المحتوى |
|-------|---------|
| Revenue | actual vs forecast |
| Approvals | SLA compliance rate |
| Adoption | daily active users |
| Issues | any blockers |
| Next | action items |

### Success Metrics to Track
| المقياس | قبل Dealix | بعد Dealix | الهدف |
|---------|-----------|-----------|-------|
| وقت الموافقة | __ يوم | __ ساعة | -70% |
| وضوح Pipeline | __% | __% | +50% |
| وقت الإقفال | __ يوم | __ يوم | -40% |
| Executive visibility | شهري | لحظي | Real-time |

---

## Post-Pilot: Conversion to Paid

### Day 12: Pre-Close Meeting
```
[الاسم]، مرت أسبوعين على الـ pilot.

خلني أشاركك النتائج:
• الموافقات صارت أسرع بـ X%
• فريقك استخدم النظام Y مرة
• عندكم Z صفقة أوضح الآن

السؤال: تحب نستمر بالاشتراك الشهري؟

الخطة [الاسم]: [السعر]/شهر
تشمل: [المميزات]
```

### Day 14: Contract Signing
- Send contract via system (eSign if available)
- First monthly payment
- Transition from pilot to production config
- Remove pilot time limits

---

## Troubleshooting — Common Issues

| المشكلة | الحل |
|---------|------|
| WhatsApp لا يرسل | تحقق من MOCK_MODE=false + API token |
| Dashboard بطيء | Check Redis connection + DB indexes |
| Approval لا يصل | Verify notification settings + SLA config |
| Arabic مكسر | Check font loading + RTL direction |
| Login فشل | Check JWT_SECRET_KEY + token expiry |
| Data لا يظهر | Verify tenant_id in all queries |

---

## Rollback Plan

إذا صار أي مشكلة كبيرة:
```bash
# 1. Inform client immediately
# 2. Take snapshot
docker-compose exec db pg_dump -U dealix dealix_db > backup.sql

# 3. If needed, rollback last migration
docker-compose exec backend alembic downgrade -1

# 4. If critical, switch to maintenance mode
# Set ENVIRONMENT=maintenance in .env
docker-compose restart backend
```
