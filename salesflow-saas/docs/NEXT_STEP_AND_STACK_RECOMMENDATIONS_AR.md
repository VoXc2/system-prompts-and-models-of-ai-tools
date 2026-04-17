# الخطوة التالية + توصيات المكدس — NEXT STEP & STACK RECOMMENDATIONS

> **القاعدة**: Core System = done. الآن = Live Path + Enforcement + Release Gate.  
> **المرجع**: `MASTER_OPERATING_PROMPT.md` + `tier1-master-closure-checklist.md`

---

## الخطوة التالية الواحدة الآن

### أغلق المسار الذهبي end-to-end

```
Partner intake → Partner dossier (PartnerDossier schema)
  → Economics model (EconomicsModel schema)
  → Approval packet (ApprovalPacket schema)
  → Approval Center (Class B enforcement)
  → Workflow commitment (DurableTaskFlow checkpoint)
  → Evidence pack (auto-assembled, SHA256)
  → Executive weekly summary (ExecWeeklyPack schema)
```

**لماذا هذا المسار؟**
- يختبر القرار + الثقة + التنفيذ + الواجهة في تشغيل واحد
- أسرع wedge لإظهار قيمة حقيقية
- يثبت 5 من 6 اختبارات الإغلاق (truth, schema, workflow, trust, executive)

---

## 6 اختبارات الإغلاق

| # | الاختبار | المعيار | الحالة |
|---|---------|---------|--------|
| 1 | **Truth** | مصدر واحد للحقيقة يحدد current/partial/pilot/production | **PASS** — `current-vs-target-register.md` |
| 2 | **Schema** | كل output حرج schema-bound مع validation | **FAIL** — 17 schemas defined, 0 enforced |
| 3 | **Workflow** | مسار حي واحد end-to-end بدون تعديل يدوي | **FAIL** — لا يوجد مسار مكتمل |
| 4 | **Trust** | external commitment يفشل بدون approval + evidence + correlation | **PARTIAL** — policy gate موجود، enforcement غير مكتمل |
| 5 | **Release** | Release Readiness Matrix توقف الإصدار فعلاً | **FAIL** — architecture_brief في CI لكن ليس gate |
| 6 | **Executive** | Executive Room حية تُستخدم أسبوعياً | **PARTIAL** — مربوطة بـ API، لكن بحاجة بيانات + استخدام |

---

## أضف الآن — Stack Additions

### 1. OpenTelemetry (correlation)
**لماذا**: ربط trace_id/span_id عبر approval → execution → evidence  
**كيف**: إضافة `opentelemetry-api` + `opentelemetry-sdk` لـ requirements.txt  
**أين**: `openclaw/gateway.py` — generate trace_id at entry, propagate downstream  
**الأثر**: كل قرار قابل للتتبع من البداية للنهاية

### 2. GitHub OIDC
**لماذا**: استبدال long-lived secrets بـ short-lived tokens  
**كيف**: في `.github/workflows/dealix-ci.yml` — إضافة `permissions: id-token: write`  
**أين**: deploy steps + cloud access  
**الأثر**: أمان أفضل + compliance ready

### 3. Artifact Attestations
**لماذا**: إثبات provenance لكل build  
**كيف**: `actions/attest-build-provenance@v1` في CI  
**متطلب**: GitHub Enterprise Cloud لـ private repos  
**الأثر**: كل artifact مربوط بـ commit SHA + workflow + environment

### 4. OpenFGA (أقل تكامل حي)
**لماذا**: object-level authorization لمسار approval/evidence  
**كيف**: ابدأ بـ authorization_model_id pinned لمسار واحد  
**أين**: approval_bridge.py — check can_user_approve(resource)  
**الأثر**: صلاحيات دقيقة بدل RBAC عام

---

## أضف بعده مباشرة

### 5. Great Expectations (data quality)
**لماذا**: جودة البيانات كجزء من workflow preconditions  
**أين**: قبل evidence pack assembly + forecast calculations  
**الأثر**: بيانات موثوقة في Executive Room

### 6. Connector Governance Layer
**لماذا**: فرض contract موحد لكل connector  
**ما المطلوب**: version, timeout, retry, health, freshness, audit mapping  
**الأثر**: لا direct vendor bindings من agents

### 7. Unstructured (document extraction)
**لماذا**: استخراج DD docs, contracts, CIMs, PDFs  
**متى**: عند تفعيل M&A DD workflow  
**الأثر**: evidence pipeline أقوى

---

## احتفظ به في الرادار (لا تضفه الآن)

| التقنية | السبب | متى |
|---------|-------|-----|
| Temporal | durable workflows | بعد نجاح المسار الذهبي |
| OPA | policy engine | عندما تتجاوز القواعد 50 |
| MCP expansion | tool connectors كثيرة | بعد استقرار المسارات الأولى |
| Airbyte | data ingestion | عند 5+ مصادر بيانات |

---

## Backend Upgrades — الترتيب

### الآن
1. **correlation_id propagation**: `openclaw/gateway.py` → agent → audit → evidence
2. **Schema enforcement**: LeadScoreCard + ApprovalPacket في live flows
3. **Auto evidence pack**: on deal close → assemble from 6 tables
4. **Approval enforcement**: Class B actions MUST have ApprovalPacket schema

### بعده
5. **Idempotency keys**: لكل endpoint يسبب side effects
6. **Retry/compensation**: لمسارات الشراكة والتوقيع
7. **Verification receipts**: لكل tool call عبر OpenClaw
8. **Telemetry**: structured logs + approval SLA metrics + contradiction counters

---

## Frontend Upgrades — الترتيب

### الآن
1. **Contract-driven rendering**: Executive Room يستهلك ExecWeeklyPack مباشرة
2. **Loading/empty/error states**: لكل surface
3. **Demo vs live indicator**: فصل واضح

### بعده
4. **Arabic/RTL polish**: جداول، تقارير، تصدير
5. **Print/export modes**: للواجهات التنفيذية
6. **State badges**: severity + trust indicators

---

## Docs/Sales/Marketing Additions — الترتيب

### الآن
1. **Customer onboarding guide** (pilot clients)
2. **Admin setup guide** (IT team)
3. **Executive quickstart** (CEO first use)
4. **Pilot sales pack**: one-pager + deck + ROI + scope
5. **Marketer hub**: positioning + ICPs + objection handling + claims allowed

### بعده
6. **Operator guide**
7. **Implementation checklist**
8. **Trust/compliance page** (public)
9. **Saudi/GCC readiness page** (public)
10. **Industry use-case pages**

---

## الترتيب الأمثل — 7 خطوات

```
1. فعّل Docs/Governance/Contracts CI بالكامل ✅ (architecture_brief في CI)
2. أغلق المسار الذهبي end-to-end ← الآن
3. حوّل Executive Room إلى contract-driven
4. اجعل Release Readiness Matrix gate فعلية
5. فعّل workflow سعودي حساس واحد
6. أضف OpenTelemetry + OIDC + attestations
7. جهّز pilot sales pack + marketer hub + customer docs
```

---

## تجنب الآن

| ما تتجنبه | السبب |
|-----------|-------|
| إضافة agents جديدة | agent sprawl قبل القيمة |
| MCP heavy expansion | تعقيد قبل استقرار |
| Temporal قبل المسار الذهبي | over-engineering |
| Industry pages قبل pilot | لا عميل = لا case study |
| Perfect CI قبل المنتج | CI يُصلح لاحقاً، المنتج أولاً |
