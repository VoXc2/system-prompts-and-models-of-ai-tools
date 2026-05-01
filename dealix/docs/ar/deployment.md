# دليل النشر

النسخة الإنجليزية الكاملة: [deployment.md](../deployment.md)

## 🐳 Docker (الموصى به)

### حاوية واحدة (التطبيق فقط)

```bash
docker build -t ai-company-saudi:2.0.0 .
docker run -d \
  --name ai-company \
  --env-file .env \
  -p 8000:8000 \
  --restart unless-stopped \
  ai-company-saudi:2.0.0
```

### الـ stack الكامل

```bash
make docker-up
# التطبيق + PostgreSQL 16 + Redis 7 + MongoDB 7
```

## ☁️ VPS إنتاجي

```bash
# تجهيز السيرفر
sudo apt update && sudo apt install -y python3.12 python3.12-venv git nginx postgresql redis

# استنساخ وإعداد
git clone https://github.com/YOUR-ORG/ai-company-saudi.git /opt/ai-company
cd /opt/ai-company
python3.12 -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# عدّل .env
```

## قائمة التحقق قبل النشر الإنتاجي

- [ ] `.env` يحتوي مفاتيح حقيقية و `APP_ENV=production`
- [ ] `APP_SECRET_KEY` عشوائي بطول ٦٤ حرف
- [ ] `CORS_ORIGINS` محصورة على نطاقك الفعلي
- [ ] Rate limiting على nginx أو Cloudflare
- [ ] شهادة TLS صالحة
- [ ] كلمات مرور قوية لقاعدة البيانات
- [ ] جدول نسخ احتياطي يومي
- [ ] Dependabot مفعّل
- [ ] حماية الفرع الرئيسي على GitHub
- [ ] مطلوب مراجعات على PRs
- [ ] `gitleaks detect --source .` يمر بدون أخطاء
