# دليل الربط التقني الشامل - Dealix (ديل اي اكس)

> آخر تحديث: مارس 2026 | هذا الدليل يشرح كيفية ربط جميع الخدمات التقنية المطلوبة لتشغيل Dealix

---

## 1. واتساب بزنس API (WhatsApp Business API)

### المتطلبات:
- حساب Meta Business (business.facebook.com)
- رقم جوال مخصص لواتساب بزنس (غير مرتبط بواتساب شخصي)
- موقع إلكتروني نشط (للتحقق)

### الخطوات:

#### الخطوة 1: إنشاء حساب Meta Business
1. اذهب إلى: https://business.facebook.com
2. أنشئ حساب بزنس جديد باسم "Dealix"
3. أكمل بيانات الشركة (الاسم، العنوان، الموقع)
4. ارفع المستندات المطلوبة للتحقق (سجل تجاري أو وثيقة رسمية)

#### الخطوة 2: تفعيل WhatsApp Business API
1. من لوحة Meta Business، اذهب إلى: Settings → Business Settings
2. اختر: WhatsApp Accounts → Add
3. أنشئ WhatsApp Business Account جديد
4. أدخل اسم العرض: "Dealix - ديل اي اكس"
5. اربط رقم الجوال المخصص
6. استلم رمز التحقق (SMS أو مكالمة)

#### الخطوة 3: الحصول على الـ API Credentials
1. من Meta Business → WhatsApp → API Setup
2. انسخ:
   - **WHATSAPP_API_TOKEN**: الـ Permanent Token (أنشئ System User → Generate Token)
   - **WHATSAPP_PHONE_NUMBER_ID**: يظهر تحت Phone Numbers
   - **WHATSAPP_BUSINESS_ACCOUNT_ID**: يظهر في عنوان الصفحة
   - **WHATSAPP_VERIFY_TOKEN**: أنشئ نص عشوائي طويل

#### الخطوة 4: تحديث .env
```env
WHATSAPP_API_TOKEN=EAAxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=1234567890
WHATSAPP_BUSINESS_ACCOUNT_ID=9876543210
WHATSAPP_VERIFY_TOKEN=dealix_verify_token_2026_secure
```

#### الخطوة 5: إعداد Webhook
- URL: `https://yourdomain.com/webhooks/whatsapp`
- Verify Token: نفس WHATSAPP_VERIFY_TOKEN
- اشترك في: messages, message_deliveries, message_reads

#### اختبار:
```bash
curl -X POST "https://graph.facebook.com/v21.0/PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messaging_product":"whatsapp","to":"966XXXXXXXXX","type":"text","text":{"body":"تجربة من Dealix"}}'
```

---

## 2. البريد الإلكتروني (SMTP)

### الخيار أ: Google Workspace (موصى به للفريق)

#### الخطوات:
1. اشترك في Google Workspace: https://workspace.google.com
2. أضف دومينك (dealix.sa)
3. إعدادات DNS المطلوبة:

```
MX Records:
| الأولوية | السيرفر |
|---------|---------|
| 1 | ASPMX.L.GOOGLE.COM |
| 5 | ALT1.ASPMX.L.GOOGLE.COM |
| 5 | ALT2.ASPMX.L.GOOGLE.COM |
| 10 | ALT3.ASPMX.L.GOOGLE.COM |
| 10 | ALT4.ASPMX.L.GOOGLE.COM |
```

4. أنشئ الحسابات: info@, support@, sales@, noreply@, privacy@
5. تحديث .env:
```env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@dealix.sa
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App Password من Google
```

### الخيار ب: SendGrid (للرسائل الآلية)

1. أنشئ حساب: https://sendgrid.com
2. أنشئ API Key: Settings → API Keys → Create
3. أضف Domain Authentication (SPF + DKIM)
4. تحديث .env:
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
```

### SPF Record:
```
v=spf1 include:_spf.google.com include:sendgrid.net ~all
```

### DKIM: يتم إعداده تلقائياً من Google Workspace / SendGrid

### DMARC:
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@dealix.sa; pct=100
```

---

## 3. الرسائل النصية SMS (Unifonic)

### الخطوات:
1. أنشئ حساب: https://cloud.unifonic.com
2. أكمل التحقق من الهوية (سعودي)
3. احصل على App SID من: Dashboard → Settings
4. حدد Sender ID: "Dealix"
5. تحديث .env:
```env
UNIFONIC_APP_SID=xxxxxxxxxxxxxxxxxx
UNIFONIC_SENDER_ID=Dealix
```

### اختبار:
```bash
curl -X POST "https://el.cloud.unifonic.com/rest/SMS/messages" \
  -d "AppSid=YOUR_APP_SID&SenderID=Dealix&Recipient=966XXXXXXXXX&Body=تجربة Dealix"
```

---

## 4. الدومين + SSL

### شراء الدومين:
- dealix.sa (يتطلب سجل تجاري سعودي) - من: nic.sa
- dealix.com - من: Namecheap, GoDaddy, Google Domains

### إعدادات DNS:

| النوع | الاسم | القيمة | TTL |
|-------|-------|--------|-----|
| A | @ | SERVER_IP | 300 |
| A | www | SERVER_IP | 300 |
| CNAME | api | @ | 300 |

### SSL عبر Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d dealix.sa -d www.dealix.sa
```

### SSL عبر Cloudflare (أسهل):
1. أنشئ حساب Cloudflare
2. أضف دومينك
3. غيّر Nameservers عند المسجل
4. فعّل Full (Strict) SSL
5. فعّل Always Use HTTPS

### تحديث nginx:
```nginx
server {
    listen 443 ssl;
    server_name dealix.sa www.dealix.sa;
    
    ssl_certificate /etc/letsencrypt/live/dealix.sa/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dealix.sa/privkey.pem;
    
    location /api/ { proxy_pass http://backend:8000; }
    location / { proxy_pass http://frontend:3000; }
}
```

### تحديث .env:
```env
API_URL=https://api.dealix.sa
FRONTEND_URL=https://dealix.sa
```

---

## 5. بوابة الدفع (Moyasar)

### لماذا Moyasar؟
- سعودي 100%
- يدعم مدى، فيزا، ماستركارد، Apple Pay, STC Pay
- سهل التكامل
- رسوم: 2.7% + 1 ريال لكل معاملة

### الخطوات:
1. أنشئ حساب: https://moyasar.com
2. أكمل KYC (سجل تجاري + حساب بنكي)
3. احصل على API Keys من: Dashboard → Settings → API Keys
4. تحديث .env:
```env
MOYASAR_API_KEY=sk_test_xxxxxxxxxxxx    # test mode
MOYASAR_PUBLISHABLE_KEY=pk_test_xxxxx   # for frontend
# عند الإنتاج:
# MOYASAR_API_KEY=sk_live_xxxxxxxxxxxx
# MOYASAR_PUBLISHABLE_KEY=pk_live_xxxxx
```

### اختبار الدفع (Test Mode):
- بطاقة اختبار: 4111 1111 1111 1111
- تاريخ: أي تاريخ مستقبلي
- CVC: أي 3 أرقام

---

## 6. Google Maps API (لتوليد العملاء)

### الخطوات:
1. اذهب إلى: https://console.cloud.google.com
2. أنشئ مشروع جديد: "Dealix Lead Gen"
3. فعّل هذه الـ APIs:
   - Places API
   - Maps JavaScript API
   - Geocoding API
4. أنشئ API Key: APIs & Services → Credentials → Create
5. حدد القيود: HTTP referrers (dealix.sa) + API restrictions
6. تحديث .env:
```env
GOOGLE_MAPS_API_KEY=AIzaxxxxxxxxxxxxxxxxxx
```

### الاستخدام المجاني:
- 28,500 طلب Places/شهر مجاناً
- بعدها: $0.032 لكل طلب
- ميزانية شهرية مقترحة: $200 (كافية لـ 6,250+ طلب إضافي)

---

## 7. ملف .env الكامل للإنتاج

```env
# === قاعدة البيانات ===
DB_NAME=dealix
DB_USER=dealix_user
DB_PASSWORD=STRONG_RANDOM_PASSWORD_HERE
DATABASE_URL=postgresql+asyncpg://dealix_user:PASSWORD@db:5432/dealix

# === Redis ===
REDIS_URL=redis://redis:6379/0

# === الأمان ===
SECRET_KEY=RANDOM_64_CHAR_STRING_HERE
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# === URLs ===
API_URL=https://api.dealix.sa
FRONTEND_URL=https://dealix.sa

# === واتساب ===
WHATSAPP_API_TOKEN=EAAxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456
WHATSAPP_BUSINESS_ACCOUNT_ID=789012
WHATSAPP_VERIFY_TOKEN=secure_random_token

# === إيميل ===
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@dealix.sa
SMTP_PASSWORD=app_password_here
SENDGRID_API_KEY=SG.xxxxx

# === SMS ===
UNIFONIC_APP_SID=xxxxx
UNIFONIC_SENDER_ID=Dealix

# === الدفع ===
MOYASAR_API_KEY=sk_live_xxxxx
MOYASAR_PUBLISHABLE_KEY=pk_live_xxxxx

# === Google Maps ===
GOOGLE_MAPS_API_KEY=AIzaxxxxx

# === التطبيق ===
APP_NAME=Dealix
APP_NAME_AR=ديل اي اكس
DEBUG=False
DEFAULT_TIMEZONE=Asia/Riyadh
DEFAULT_CURRENCY=SAR
DEFAULT_LOCALE=ar
```

---

## ملخص الربط

| الخدمة | الحالة | الأولوية | الوقت المتوقع |
|--------|-------|---------|-------------|
| دومين + SSL | مطلوب أولاً | P1 | 1-2 ساعة |
| إيميل SMTP | مطلوب | P1 | 1 ساعة |
| واتساب API | مطلوب للمبيعات | P1 | 2-5 أيام (تحقق Meta) |
| بوابة الدفع | مطلوب للاشتراكات | P2 | 1-3 أيام (KYC) |
| SMS (Unifonic) | اختياري | P3 | 1 ساعة |
| Google Maps API | مطلوب للـ Lead Gen | P2 | 30 دقيقة |
