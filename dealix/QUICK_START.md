# 🚀 الخطوات السريعة — ارفع المشروع على GitHub في دقيقة واحدة

## الطريقة الأسهل — سكربت جاهز

```bash
# 1. فك الضغط
tar -xzf ai-company-saudi-v2.0.0.tar.gz
cd ai-company-saudi

# 2. تأكد أن gh CLI مثبت ومسجّل دخولك
#    (اختياري لكنه الأسهل)
gh auth login

# 3. شغّل السكربت (عدّل اسم المستخدم)
GITHUB_USER=your-github-username \
REPO_NAME=ai-company-saudi \
VISIBILITY=private \
bash scripts/github_setup.sh
```

السكربت يقوم بـ:
1. فحص أمني — يتأكد ما فيه أي سر مكشوف
2. `git init` وإنشاء commit أول شامل
3. إنشاء الريبو على GitHub (خاص افتراضياً)
4. رفع الفرع `main`
5. إنشاء tag `v2.0.0` ورفعه
6. إنشاء GitHub Release مع CHANGELOG

---

## الطريقة اليدوية — إذا تبغى تتحكم بكل خطوة

```bash
tar -xzf ai-company-saudi-v2.0.0.tar.gz
cd ai-company-saudi

# تأكد إن .env ما موجود (لازم تبقى بس .env.example)
ls .env 2>/dev/null && echo "⚠️ احذف .env قبل ما تكمل!"

# Initialize
git init -b main
git add -A
git commit -m "feat: initial release v2.0.0"

# أنشئ الريبو على github.com يدوياً ثم:
git remote add origin git@github.com:YOUR-USER/ai-company-saudi.git
git push -u origin main

# الـ tag
git tag -a v2.0.0 -m "Release v2.0.0"
git push origin v2.0.0
```

---

## بعد الرفع — خطوات GitHub مهمة

### 1. فعّل Branch Protection على `main`
Settings → Branches → Add rule:
- Require pull request reviews (1 reviewer)
- Require status checks to pass (`CI` job)
- Require conversation resolution
- Do not allow force pushes

### 2. فعّل الحماية الأمنية
Settings → Code security:
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Secret scanning
- ✅ Push protection (for secrets)

### 3. أضف Secrets للـ CI (اختياري للاختبارات)
Settings → Secrets and variables → Actions:
- `ANTHROPIC_API_KEY` (للاختبارات التي تستدعي LLM فعلياً)
- `CODECOV_TOKEN` (لرفع تقارير التغطية)

### 4. فعّل GitHub Actions
في أول push، اذهب إلى Actions tab وتأكد إن CI workflow نجح.

---

## ⚠️ مهم جداً قبل أي شيء

**المفاتيح اللي كانت في ملف `PROJECT_FULL_REPORT.md` الأصلي تسرّبت مسبقاً.** لازم تدوّرها كلها قبل استخدام المشروع:

| المزود | الرابط |
| --- | --- |
| Anthropic | https://console.anthropic.com/settings/keys |
| DeepSeek | https://platform.deepseek.com/api_keys |
| Groq | https://console.groq.com/keys |
| GLM (Z.ai) | https://open.bigmodel.cn/usercenter/apikeys |
| Google | https://console.cloud.google.com/apis/credentials |
| HubSpot | Settings → Integrations → Private Apps |
| ClickBank | Account Settings → API |
| HIX AI | Account → API |

بعد التدوير، ضعها في `.env` محلياً (ما ترفع `.env` أبداً) وفي GitHub Secrets للـ CI.

---

## الأوامر الأساسية بعد الرفع

```bash
# إعداد التطوير المحلي
make setup

# تشغيل محلي
make run                    # على http://localhost:8000/docs

# اختبارات
make test

# Docker كامل
make docker-up

# CLI تفاعلي
python cli.py menu
# أو
python cli.py demo          # عرض توضيحي شامل
python cli.py sector healthcare -e
python cli.py status
```
