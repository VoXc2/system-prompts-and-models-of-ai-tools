# Cost Optimization Guide — Dealix v3.0.0

## الأهداف
- تقليل فاتورة LLM بنسبة 60-80%
- إبقاء زمن الاستجابة < 3 ثوانٍ لـ 95% من الطلبات
- إتاحة مراقبة فورية عبر `/api/v1/admin/costs`

## المكوّنات

### 1. Prompt Caching (Anthropic)
- `core/llm/anthropic_client.py`
- يُفعّل تلقائياً للـ system prompts >= 1024 توكن
- توفير 90% على المدخلات المُخزّنة ($0.30 بدل $3.00 لكل 1M)

### 2. Semantic Cache (Redis + MiniLM)
- `dealix/caching/semantic_cache.py`
- threshold 0.95 cosine similarity
- TTL 24 ساعة، max 200 scan
- موديل embeddings محلي: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim، 118MB)

### 3. Smart Routing
- `core/config/models.smart_route()`
- قواعد:
  | المهمة | النموذج | السعر (in/out لكل 1M) |
  |-------|---------|-----------|
  | Classification/Triage | Groq Llama 3.3 | مجاني |
  | Arabic non-critical | GLM-4 | $0.14/$0.28 |
  | Code/Extraction | DeepSeek Chat | $0.14/$0.28 |
  | Research | Gemini 2.5 Flash | $0.075/$0.30 |
  | Critical reasoning | Claude Sonnet 4.5 + cache | $3/$15 (أو $0.30 مُخزّن) |

### 4. Batch Processing
- `AcquisitionPipeline.run_batch()`
- يجمع ≥5 عملاء في تشغيل موازٍ (semaphore = 8)

### 5. Cost Tracker
- `dealix/observability/cost_tracker.py`
- جدول `llm_calls` في Postgres
- ring buffer في الذاكرة كـ fallback
- `/api/v1/admin/costs` يجمع حسب model/provider/task

## التوقعات
عند 100k نداء/شهر:
- قبل: ~$400 شهرياً (كل شيء على Claude Sonnet)
- بعد: ~$80-140 شهرياً (توفير 65-80%)
