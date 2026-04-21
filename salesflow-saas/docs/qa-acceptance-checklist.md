# QA Acceptance Checklist — Dealix Launch

## 1) Core Functional Flows
- [ ] User signup/login يعمل بدون أخطاء.
- [ ] Tenant isolation صحيح في كل الطلبات.
- [ ] Lead creation/edit/assignment يعمل.
- [ ] Opportunity pipeline transitions تعمل.
- [ ] Follow-up/task reminders تعمل.
- [ ] Notifications الأساسية تعمل.

## 2) AI & Local Model Flows
- [ ] طلب AI يمر عبر local routing بنجاح.
- [ ] fallback provider يعمل عند فشل المحلي.
- [ ] Response quality مقبولة (AR/EN).
- [ ] Timeout handling لا يكسر الواجهة.

## 3) API & Integration
- [ ] `/api/v1/*` endpoints تعيد status codes صحيحة.
- [ ] Auth/JWT lifecycle سليم.
- [ ] Webhook/integration critical paths سليمة.

## 4) Performance
- [ ] صفحات أساسية ضمن زمن تحميل مقبول.
- [ ] API p95 ضمن SLA الداخلي.
- [ ] Queue lag ضمن الحد.

## 5) Security & Compliance
- [ ] لا تسريب أسرار في logs.
- [ ] PDPL consent checks فعالة قبل الإرسال.
- [ ] صلاحيات RBAC لا تسمح بتجاوزات.

## 6) Localization
- [ ] واجهة عربية RTL سليمة.
- [ ] نصوص AR/EN متطابقة وظيفياً.

## 7) Release Decision
- [ ] لا توجد أعطال P0/P1 مفتوحة.
- [ ] تم اعتماد Go من: QA + Product + Eng + Ops.
