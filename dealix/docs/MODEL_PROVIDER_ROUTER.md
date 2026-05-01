# Model Provider Router — موجّه النماذج

> 7 providers، 10 task types. كل مهمة تذهب لمزود مناسب مع fallback chain. لا تعتمد على مزود واحد.

## 1. Task Types

```
strategic_reasoning, arabic_copywriting, classification,
compliance_guardrail, meeting_analysis, vision_analysis,
extraction, summarization, coding_project_understanding,
low_cost_bulk
```

## 2. Providers

| key | family | cost | latency | privacy | الاستخدام |
|-----|--------|------|---------|---------|----------|
| claude_sonnet | anthropic | mid | balanced | vendor | استراتيجية + كتابة عربية + امتثال |
| claude_haiku | anthropic | low | fast | vendor | تصنيف + استخراج كثيف |
| gpt_4_class | openai | high | balanced | vendor | استراتيجية + رؤية |
| gpt_4o_mini | openai | low | fast | vendor | تصنيف رخيص |
| gemini_pro | google | mid | balanced | vendor | اجتماعات + رؤية |
| azure_oai_ksa | azure | mid | balanced | **ksa_region** | الحالات الحساسة (PDPL) |
| local_qwen_ar | local | low | balanced | **self_hosted** | حالات شديدة الحساسية |

## 3. Cost Policy

```
bulk=True               → low
output_tokens > 1500    → high
input_tokens > 8000     → high
strategic/vision/compl. → mid
arabic_copywriting      → mid
default                 → low
```

## 4. Fallback Strategy

- لو `sensitivity="high"`: الترتيب حسب `privacy_tier` أولاً (self_hosted > ksa_region > vendor).
- وإلا: الترتيب حسب `cost_class` (low > mid > high).
- لو `primary_provider` محدد ويدعم المهمة → يُرفع لرأس السلسلة.

## 5. Endpoints

```
GET  /api/v1/model-router/providers
GET  /api/v1/model-router/tasks
POST /api/v1/model-router/route
POST /api/v1/model-router/cost-class
GET  /api/v1/model-router/usage/demo
```

## 6. حدود

- Router نفسه لا يستدعي LLM. يصدر قراراً فقط.
- التنفيذ الفعلي يبقى مسؤولية adapter منفصل.
- لا lock-in — جميع المزودين قابلون للاستبدال بدون تغيير API.
