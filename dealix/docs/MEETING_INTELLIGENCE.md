# Meeting Intelligence — ذكاء الاجتماعات

> Pre-meeting brief + transcript summary + objection extraction + post-meeting follow-up + deal risk. كله Arabic، deterministic، approval-required.

## 1. الوحدات

| الوحدة | الدور |
|--------|------|
| `transcript_parser` | يقبل Google Meet entries أو نصاً عادياً، يحوّل إلى `speaker_turns`. |
| `meeting_brief` | يبني pre-meeting brief بـ6 أقسام عربية: هدف، أسئلة، اعتراضات محتملة، عرض، خطوة تالية. |
| `objection_extractor` | يستخرج 8 فئات اعتراضات (السعر، التوقيت، صانع القرار، الأمان، التكامل، البديل، إثبات النتائج، التعقيد). |
| `followup_builder` | يبني drafts للـemail + WhatsApp بدون إرسال حي. |
| `deal_risk` | يحسب risk_score (0..100) بناءً على الاعتراضات وغياب صاحب القرار وعدم تحديد خطوة تالية. |

## 2. Pre-Meeting Brief

`build_pre_meeting_brief(company, contact, opportunity, sector)` يعطي:
- objective_ar
- 5 questions_ar
- 5 likely_objections_ar
- offer_skeleton_ar (Pilot 7 أيام، 499 ريال)
- next_step_ar

## 3. Transcript Summarizer

`parse_transcript_entries` يدعم:
- list of `{participantId, text}` (Google Meet shape)
- plain text "Speaker: line"

`summarize_meeting(parsed)` يعطي ملخصاً عربياً + أسئلة مرشحة + `approval_required=True`.

Google Meet API يدعم قراءة transcripts عبر `conferenceRecords.transcripts.entries.list` — لكن يلزم موافقة كل المشاركين (PDPL).

## 4. Objection Extractor

8 فئات regex + Arabic gloss:
```
price        → "غالي|مرتفع|الميزانية|expensive|cost"
timing       → "ليس\s+الآن|بعد\s+شهر|next\s+quarter"
authority    → "المدير|صاحب\s+القرار|need\s+approval"
trust        → "بيانات|خصوصية|أمان|PDPL|security|privacy"
integration  → "CRM|نظامنا|الربط|migration"
competitor   → "نستخدم|بديل|أداة\s+ثانية|alternative"
results      → "نتائج|مضمون|guarantee|ROI|دليل"
complexity   → "معقد|صعب|تدريب|onboarding"
```

النتيجة: قائمة `{category, label_ar, snippet}` مع snippet ±40 حرف.

## 5. Follow-up Builder

`build_post_meeting_followup(summary, next_steps, contact_name, company_name, objections)`:
- Email draft (subject_ar + body_ar)
- WhatsApp draft (body_ar)
- كلا الـdraftsْ: `live_send_allowed=False, approval_required=True`

عندما تكون فيه objections، يضيف فقرة "رجعت بعد الاجتماع وفكرت في النقاط التي ذكرتها: ..."

## 6. Deal Risk

```
+20 price objection
+15 timing objection
+25 authority not present
+20 trust/security objection
+10 integration concern
+15 competitor in play
+25 next step NOT set
+10 decision maker absent
+10 days_since_last_touch > 14
```

تيرز: ≥70 high, ≥40 medium, <40 low.

`recommended_action_ar`:
- high: اجتماع ثانٍ مع صاحب القرار خلال 5 أيام + مادة إثبات قيمة قصيرة.
- medium: متابعة خلال 3 أيام مع خطوة تالية محددة.
- low: نفّذ الخطوة التالية المتفق عليها.

## 7. Endpoints

```
POST /api/v1/meeting-intelligence/brief
GET  /api/v1/meeting-intelligence/brief/demo
POST /api/v1/meeting-intelligence/transcript/summarize
POST /api/v1/meeting-intelligence/followup/draft
POST /api/v1/meeting-intelligence/deal-risk
```

## 8. حدود

- لا realtime listening (مرحلة لاحقة).
- لا يرسل follow-up — drafts فقط.
- لا يقرأ transcript بدون موافقة جميع الأطراف.
