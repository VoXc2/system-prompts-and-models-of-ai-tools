<div align="center" dir="rtl">

# 🏢 شركة AI السعودية

### منصة ذكاء اصطناعي متعددة الوكلاء، جاهزة للإنتاج، للسوق السعودي والخليجي

[![CI](https://github.com/VoXc2/dealix/actions/workflows/ci.yml/badge.svg)](https://github.com/VoXc2/dealix/actions/workflows/ci.yml)
[![الرخصة: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

**العربية** · **[English](README.md)**

</div>

---

## 🌟 نظرة عامة

**شركة AI السعودية** منصة ذكاء اصطناعي متعددة الوكلاء جاهزة للإنتاج، تُؤتمت:

- **المرحلة 8 — اكتساب العملاء تلقائياً:** استقبال العملاء، مطابقة ICP، استخلاص المشاكل، التأهيل BANT، الحجز، مزامنة HubSpot، توليد العروض، الوصول، ومتابعات متدرّجة.
- **المرحلة 9 — النمو المستقل:** ذكاء القطاعات السعودية، توليد محتوى ثنائي اللغة، نشر متعدد القنوات، إثراء العملاء، مراقبة المنافسين، وبحث السوق.

مصمّمة للسوق **السعودي والخليجي** مع دعم **عربي من الدرجة الأولى**، أسعار بـ **الريال السعودي**، معرفة بـ **توقيت آسيا/الرياض**، ومتناغمة مع برامج **رؤية 2030**.

## ✨ المزايا الرئيسية

- 🧠 **توجيه ذكي لنماذج LLM** — يوزّع المهام بين **Anthropic Claude** (منطق)، **Gemini** (بحث)، **Groq** (تصنيف سريع)، **DeepSeek** (كود)، **GLM** (عربي). سلسلة احتياط تلقائية عند الفشل.
- 🤖 **أكثر من 15 وكيلاً إنتاجياً** — كل وكيل بمدخلات/مخرجات مُعرَّفة، سجلات مهيكلة، تقهقر لطيف، واختبارات.
- 🌍 **ثنائي اللغة AR/EN** — محتوى، سكربتات مبيعات، prompts، واجهات تدعم العربية أولاً.
- 🔒 **الأمن أولاً** — الإعدادات من `.env` فقط، استخدام `SecretStr` لكل سر، فحوصات gitleaks + detect-secrets + bandit قبل كل commit، تكامل LinkedIn آمن من حيث الشروط.
- 🐳 **جاهز للسحابة** — Dockerfile متعدد المراحل، حاوية بمستخدم غير جذري، stack كامل بـ Docker Compose (التطبيق + Postgres + Redis + MongoDB)، CI/CD عبر GitHub Actions.
- 📊 **قابل للمراقبة** — سجلات مهيكلة بـ structlog، تتبع LLM اختياري عبر Langfuse، تتبع الاستخدام لكل مزود.
- 🇸🇦 **سعودي أصيل** — ١٢ قطاعاً ببيانات منسّقة (عقار، صحة، تعليم، لوجستيات، فينتك…)، مرجع للمنظّمين السعوديين، أسعار بـ SAR/USD، أعياد سعودية.

## 🚀 البدء السريع

### المتطلبات

- Python 3.11 أو 3.12
- Docker + Docker Compose (اختياري)
- على الأقل مفتاح API واحد لـ LLM (يُنصح بـ Anthropic)

### 1. استنساخ المشروع وإعداد البيئة

```bash
git clone https://github.com/YOUR-ORG/ai-company-saudi.git
cd ai-company-saudi

# إعداد لمرة واحدة
make setup
```

### 2. إعداد الأسرار

عدّل `.env` وأضف مفاتيح الـ API. **الحد الأدنى:** `ANTHROPIC_API_KEY`.

> ⚠️ **لا ترفع `.env` أبداً.** المشروع يحميك بـ `.gitignore` و pre-commit hook عبر gitleaks.

### 3. التشغيل

```bash
# محلياً
make run
# → http://localhost:8000/docs

# أو الـ stack الكامل
make docker-up
make docker-logs
```

### 4. جرّب

```bash
# إرسال عميل محتمل عبر قمع اكتساب العملاء الكامل
curl -X POST http://localhost:8000/api/v1/leads \
  -H "Content-Type: application/json" \
  -d '{
    "company": "شركة التقنية المتقدمة",
    "name": "أحمد محمد",
    "email": "ahmed@example.sa",
    "phone": "+966501234567",
    "sector": "technology",
    "region": "Saudi Arabia",
    "budget": 50000,
    "message": "نحتاج نظام AI لإدارة المبيعات"
  }'
```

## 📊 وكلاء المرحلة 8 — الاكتساب

| الوكيل | الوظيفة |
| --- | --- |
| Intake | التقاط العملاء من مصادر متعددة، توحيد، تكرار |
| ICP Matcher | تقييم بـ ٥ أبعاد + تصنيف (A/B/C/D) |
| Pain Extractor | استخلاص المشاكل ودرجة الاستعجال (عربي + إنجليزي) |
| Qualification | أسئلة BANT وتحديث المرحلة |
| Booking | Calendly → Google Calendar → يدوي |
| CRM | مزامنة HubSpot (contact + deal) |
| Proposal | عروض مُعدّة بـ Claude، أسعار حسب المنطقة |
| Outreach | افتتاحيات وصول باردة ثنائية اللغة |
| Follow-up | رسائل متابعة متدرّجة |

## 📈 وكلاء المرحلة 9 — النمو

| الوكيل | الوظيفة |
| --- | --- |
| Sector Intel | ١٢ قطاعاً سعودياً ببيانات منسّقة |
| Content Creator | مقالات + LinkedIn + دراسات حالة ثنائية اللغة |
| Distribution | جدولة متعددة القنوات (توقيت الرياض) |
| Enrichment | إثراء العميل من النطاق + LLM |
| Competitor Monitor | تحليل المنافسين واقتراح ردود |
| Market Research | بحث سوقي عبر Gemini بمصادر |

## 📚 التوثيق

| الوثيقة | الوصف |
| --- | --- |
| [`docs/architecture.md`](docs/architecture.md) | هيكل النظام |
| [`docs/agents.md`](docs/agents.md) | كل وكيل مُوثّق |
| [`docs/api.md`](docs/api.md) | مرجع REST API |
| [`docs/deployment.md`](docs/deployment.md) | النشر الإنتاجي |
| [`docs/pricing.md`](docs/pricing.md) | الأسعار |

## 🤝 المساهمة

راجع [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 الرخصة

MIT — راجع [LICENSE](LICENSE).

---

<div align="center" dir="rtl">

**[📖 التوثيق](docs/)** · **[🐛 المشاكل](../../issues)** · **[💬 النقاشات](../../discussions)**

</div>
