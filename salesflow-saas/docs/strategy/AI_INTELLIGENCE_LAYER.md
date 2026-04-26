# Dealix — AI Intelligence Layer

## وش AI يقدر يسوي (آمن)
- يبحث عن الشركة ونشاطها
- يستنتج الألم المحتمل
- يصنّف القطاع
- يسجّل score (fit + urgency + access)
- يكتب أول سطر مخصص
- يولّد رسالة كاملة (email / WhatsApp)
- يولّد follow-ups
- يصنّف الردود (7 categories)
- يقترح زاوية تفاوض
- يقترح العرض المناسب
- يقترح next action
- يحدّث playbook من النتائج

## وش AI ما يقدر يسوي (ممنوع)
- يرسل رسائل بدون موافقة سامي
- يكشط LinkedIn أو أي منصة
- يزوّر نتائج أو case studies
- يخترع أرقام عملاء
- يقرر شروط تفاوض نهائية لوحده
- يتجاهل opt-out
- يخالف سياسات المنصات

## Next Best Action Logic
```
if target == agency → partner pitch
if target == real_estate → speed-to-lead audit
if target == clinic → booking follow-up
if target == website_agency → add-on after website
if target == ecommerce → inquiry-to-order
if target == consultant → consulting partner
if target == contractor → quote follow-up

if reply == "مهتم" → book demo within 24h
if reply == "كم السعر" → send pricing + book demo
if reply == "أرسل تفاصيل" → send one-pager + push for demo
if reply == "مو الحين" → schedule 30-day follow-up
if reply == "لا" → stop immediately
if reply == "إيقاف" → stop immediately + remove from list
if reply == "أنا وكالة" → switch to partner pitch
```
