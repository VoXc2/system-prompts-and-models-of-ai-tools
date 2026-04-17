# خطة التنفيذ الكاملة — ما بعد الإغلاق

> **الهدف**: تحويل النظام من "مغلق نظرياً" إلى "مثبت تشغيلياً وقابل للبيع"  
> **القاعدة**: لا تبيع إلا ما يشتغل. لا تدّعي إلا ما هو حي.

---

## البوابات الثمانية — معيار "كل شيء تمام"

| # | البوابة | الحالة |
|---|---------|--------|
| 1 | **Truth** — مصدر واحد للحقيقة، لا overclaim | **PASS** |
| 2 | **Contract** — كل output حرج schema-bound | **PARTIAL** — 3/17 schemas مستخدمة (golden path) |
| 3 | **Trust** — Class B يفشل بدون correlation_id | **PASS** — مفعّل في approval_bridge |
| 4 | **Durable** — مسار واحد resumable end-to-end | **PARTIAL** — golden path حي لكن بدون persistence |
| 5 | **Executive** — Executive Room تجيب 5 أسئلة | **PASS** — weekly-pack endpoint حي |
| 6 | **Release** — CI يحرس الإطلاق | **PARTIAL** — architecture_brief في CI |
| 7 | **Saudi** — workflow حساس واحد مربوط | **TARGET** |
| 8 | **Commercial** — التسويق يطابق الواقع | **PASS** — marketer hub مع forbidden claims |

---

## ما أُنجز (الوضع الحالي)

### حي فعلاً
- Golden Path: `POST /api/v1/golden-path/run` → PartnerDossier → EconomicsModel → ApprovalPacket → EvidencePack
- Trust enforcement: Class B actions تفشل بدون correlation_id
- Auto evidence: deal close → auto evidence pack assembly
- Executive Room: weekly-pack contract → ExecWeeklyPack schema
- 9/9 frontend مربوطة بـ APIs حقيقية
- 8/8 backend APIs تقرأ من DB حقيقية
- Architecture Brief: 40/40 PASS

### ناقص
- 14/17 structured output schemas غير مستخدمة
- Connector live health probes
- Saudi compliance live validation
- OpenTelemetry
- OIDC + attestations
- OpenFGA

---

## الأدوات المطلوب إضافتها

### أضف الآن

| الأداة | لماذا | أين |
|--------|-------|-----|
| **OpenTelemetry** | traces + logs + metrics مترابطة | `requirements.txt` + gateway + services |
| **GitHub OIDC** | بدل long-lived secrets | `.github/workflows/` |
| **Artifact attestations** | provenance مثبت | CI build step |
| **OpenFGA** | object-level authorization | approval_bridge + evidence packs |

### أضف قريباً

| الأداة | لماذا | متى |
|--------|-------|-----|
| **Great Expectations** | data quality gates | قبل evidence pack assembly |
| **Unstructured** | استخراج عقود وDD docs | عند تفعيل M&A flow |
| **Airbyte** | data movement موحد | عند 5+ مصادر |

### في الرادار

| الأداة | لماذا | متى |
|--------|-------|-----|
| **OPA** | policy engine | عندما القواعد > 50 |
| **Temporal** | durable execution | بعد نجاح المسار الذهبي |
| **MCP expansion** | أدوات أكثر | بعد استقرار المسارات |

---

## Backend — ما يجب تثبيته

### Endpoint Inventory

| المجموعة | عدد الـ endpoints | Classification |
|----------|------------------|---------------|
| Auth | 8 | Internal — no side effects |
| Leads | 12 | External — Class A (read) / Class B (import) |
| Deals | 10 | External — Class B (stage change triggers evidence) |
| Approvals | 6 | Critical — Class B (approve/reject) |
| Contradictions | 5 | Internal — Class A |
| Evidence Packs | 5 | Critical — Class B (assemble/review) |
| Executive Room | 5 | Internal — Class A (read-only) |
| Compliance | 5 | Internal — Class A |
| Connectors | 4 | Internal — Class A |
| Golden Path | 2 | Critical — Class B (creates approval + evidence) |
| Strategic Deals | 8 | External — Class B |
| Outreach | 6 | External — Class B (sends messages) |

### Trust Enforcement Coverage

| Enforcement | المُغطى | الفجوة |
|-------------|---------|--------|
| Policy gate (A/B/C) | All OpenClaw actions | Direct API calls bypass OpenClaw |
| correlation_id required | Class B via gateway | API routes don't enforce yet |
| Auto evidence on deal close | deals.py | Other entity closes not covered |
| Structured output validation | Golden path only | Other flows use free-form |

### ما يجب فعله

1. **كل Class B API route**: تحقق من correlation_id في payload
2. **كل outreach endpoint**: تحقق من PDPL consent قبل الإرسال
3. **كل strategic deal endpoint**: log to audit_log
4. **idempotency key**: على كل POST يسبب side effects

---

## Frontend — ما يجب تثبيته

### Surface Maturity

| Surface | API Wired | Contract-Driven | States Complete | Arabic RTL |
|---------|-----------|-----------------|-----------------|-----------|
| Executive Room | ✅ | ✅ (weekly-pack) | Partial | ✅ |
| Approval Center | ✅ | Partial | Partial | ✅ |
| Evidence Viewer | ✅ | Partial | Partial | ✅ |
| Compliance | ✅ | Partial | Partial | ✅ |
| Connectors | ✅ | ✅ | Partial | ✅ |
| Forecast | ✅ | Partial | Partial | ✅ |
| Risk Heatmap | ✅ | Partial | Partial | ✅ |
| Violations | ✅ | Partial | Partial | ✅ |
| Partner Pipeline | ✅ | Partial | Partial | ✅ |

### ما يجب فعله

1. **Executive Room**: استهلك weekly-pack endpoint كمصدر وحيد
2. **كل surface**: أضف loading spinner + empty state message + error handler
3. **Demo indicator**: badge يوضح "بيانات تجريبية" vs "بيانات حية"

---

## الوثائق — ما يجب إضافته

### For Customer (العميل)

| الوثيقة | الحالة | الأولوية |
|---------|--------|----------|
| Onboarding guide | Done (LIVE_DEPLOYMENT_GUIDE) | — |
| Admin setup guide | Target | P1 |
| Executive quickstart | Target | P1 |
| FAQ | Target | P2 |

### For Team (الفريق)

| الوثيقة | الحالة |
|---------|--------|
| Architecture docs | Done (26+ docs) |
| Release docs | Done (release-prep) |
| Runbooks | Done (memory/runbooks/) |
| Closure program | Done (10 tracks) |

### For Sales (البيع)

| الوثيقة | الحالة |
|---------|--------|
| One-pager | Done |
| Marketer Hub | Done |
| Outreach sequences | Done |
| Demo seeder | Done |
| Deployment guide | Done |
| Revenue engine plan | Done |

---

## الترتيب الأمثل — 5 مراحل

### المرحلة 1: Assurance (أسبوع 1)
- [ ] فعّل OpenTelemetry (trace_id + span_id في gateway + services)
- [ ] فعّل OIDC في CI/deploy
- [ ] أضف attestation step في CI
- [ ] اربط Release Matrix بـ PR checks

### المرحلة 2: Live Path (أسبوع 1-2)
- [x] Golden Path حي end-to-end
- [x] Trust enforcement (correlation_id required)
- [x] Auto evidence on deal close
- [x] Executive weekly-pack contract
- [ ] Contradiction auto-detection في golden path

### المرحلة 3: Saudi Activation (أسبوع 2-3)
- [ ] اختر workflow: مشاركة بيانات شريك
- [ ] اربطه بـ PDPL data classification
- [ ] اربطه بـ retention/export rules
- [ ] اربطه بـ audit path + AI risk overlay

### المرحلة 4: Productization (أسبوع 3-4)
- [ ] Admin setup guide
- [ ] Executive quickstart
- [ ] Customer FAQ
- [ ] Public landing page copy
- [ ] Trust/compliance page

### المرحلة 5: Expansion (شهر 2+)
- [ ] Procurement/vendor deal flow
- [ ] Renewal/expansion deal flow
- [ ] Deeper M&A DD orchestration
- [ ] More connectors with governance
- [ ] Broader OpenFGA coverage

---

## تجنب الآن

| ما تتجنبه | السبب |
|-----------|-------|
| Temporal قبل golden path يستقر | over-engineering |
| أكثر من 2 golden paths بنفس الوقت | تشتت |
| MCP tools expansion | agent sprawl |
| Industry pages قبل case study حقيقي | لا proof |
| SOC2 certification claim | لا نملكها |
| "أفضل من Salesforce" messaging | مختلف ≠ أفضل |
