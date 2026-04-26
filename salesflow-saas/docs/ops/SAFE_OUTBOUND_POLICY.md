# Dealix — سياسة الـ Outbound الآمن

> **القاعدة الأساسية:** نؤتمت البحث والتحليل والتخصيص والتتبع — الإرسال المباشر يبقى human-approved.

---

## حدود الإرسال اليومية

| القناة | الحد اليومي (أسبوع 1-2) | الحد (بعد إثبات) | ملاحظات |
|--------|------------------------|-----------------|---------|
| Email | 10 | 20 | targeted فقط |
| WhatsApp | 5 warm | 10 warm | opted-in فقط |
| LinkedIn DM | 3 | 5 | manual فقط |
| X DM/Reply | 3 | 5 | بعد تفاعل |
| Instagram DM | 2 | 3 | inbound reply فقط |

---

## LinkedIn ⚠️

### ممنوع
- ❌ أدوات scraping (Phantombuster, LinkedIn Helper, etc.)
- ❌ automated DMs أو connection requests
- ❌ mass connection spam
- ❌ fake engagement (pods, bots)
- ❌ fake accounts
- ❌ استخراج بيانات profiles آلياً

### مسموح
- ✅ نشر محتوى يومي من حساب سامي
- ✅ تعليقات يدوية ذات قيمة
- ✅ DMs يدوية مخصصة (max 3-5/يوم)
- ✅ connection requests مع ملاحظة شخصية
- ✅ AI-assisted drafting (أنت تكتب، AI يساعد بالصياغة)

### السبب
LinkedIn يمنع صراحة أدوات الطرف الثالث التي تكشط أو تؤتمت نشاط الموقع. المخالفة = حظر الحساب.

---

## X / Twitter ⚠️

### ممنوع
- ❌ automated mentions/replies غير مطلوبة
- ❌ mass follow/unfollow
- ❌ bot accounts
- ❌ duplicate/spam tweets
- ❌ automated DMs لأشخاص ما تابعوك

### مسموح
- ✅ نشر محتوى أصلي يومياً
- ✅ ردود يدوية ذات قيمة
- ✅ threads تعليمية
- ✅ DMs لأشخاص تابعوك أو تفاعلوا
- ✅ AI-assisted drafting

---

## Instagram ⚠️

### ممنوع
- ❌ mass DM لأشخاص ما تفاعلوا
- ❌ أدوات automation (Jarvee, etc.)
- ❌ fake followers/engagement
- ❌ spam comments

### مسموح
- ✅ نشر stories, carousels, reels
- ✅ رد على DMs واردة
- ✅ DM بعد تفاعل حقيقي (علّق على بوستك / أرسلك رسالة)
- ✅ تعليقات يدوية ذات قيمة على حسابات ذات صلة

---

## WhatsApp ⚠️

### ممنوع
- ❌ blast رسائل لأرقام عشوائية
- ❌ إرسال لأشخاص ما يعرفونك بدون سياق
- ❌ رسائل تسويقية متكررة بدون موافقة
- ❌ شراء قوائم أرقام

### مسموح
- ✅ رسائل لأشخاص يعرفون سامي (warm network)
- ✅ follow-up لشخص أبدى اهتمام
- ✅ تأكيد مواعيد
- ✅ رد على استفسارات واردة
- ✅ WhatsApp Status (مرئي لجهات الاتصال فقط)

### Opt-out إلزامي
كل رسالة أولى لشخص جديد تنتهي بـ:
```
إذا ما يناسبكم هالنوع من الرسائل، ردوا "إيقاف" وما بنتواصل مرة ثانية.
```

### Stop Conditions
إذا الشخص رد بأي من:
- "إيقاف" / "stop" / "لا شكراً" / "لا" / "ما يهمني"
→ **أوقف فوراً. لا تراسله مرة ثانية.**

---

## Email ⚠️

### ممنوع
- ❌ شراء قوائم email
- ❌ subject lines مضللة
- ❌ إرسال أكثر من 3 follow-ups بدون رد
- ❌ إخفاء هوية المرسل

### مسموح
- ✅ إيميلات مستهدفة لشركات محددة
- ✅ max 3 في sequence (أولى + 2 follow-up)
- ✅ personalization حقيقية (مو mail merge عشوائي)
- ✅ opt-out واضح

### الهيكل الإلزامي
```
From: سامي العسيري <sami@dealix.me>
Subject: [موضوع محدد ومفيد — مو clickbait]
Body: [قيمة حقيقية + عرض واضح]
Footer: "إذا ما يناسبكم هالنوع من الرسائل، ردوا 'إيقاف'"
```

---

## بوابات الموافقة (Approval Gates)

**يتطلب موافقة سامي قبل:**
1. ☐ أول رسالة لشخص جديد
2. ☐ WhatsApp لأي شخص مو warm
3. ☐ نشر ادعاءات عن نتائج
4. ☐ إرسال payment link
5. ☐ إرسال عرض revenue share لشريك
6. ☐ استخدام اسم أي عميل/شركة كـ social proof
7. ☐ إرسال أكثر من 10 رسائل/يوم
8. ☐ تفعيل أي automated sending

---

## Risk Mitigation

| المخاطرة | الاحتمال | التأثير | الحل |
|----------|---------|---------|------|
| حظر LinkedIn | منخفض (manual) | عالي | التزم بـ 3-5 DMs/يوم يدوية |
| حظر WhatsApp | منخفض (warm only) | عالي | warm فقط + opt-out + stop |
| شكوى spam email | منخفض (targeted) | متوسط | opt-out + max 3 في sequence |
| سمعة سيئة | منخفض | عالي | لا ادعاءات كاذبة + احترافية |

---

## القاعدة الذهبية
> **Aggressive في البحث والتحضير. Conservative في الإرسال.**
>
> AI يدرس ويخصص ويقترح. سامي يوافق ويرسل.
