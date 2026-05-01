# 📤 رفع Sales Kit لـ GitHub — 3 طرق

الـ branch جاهز ومُرتّب: `sales-kit-2026-04-23`
الحزمة تحتوي: 12 ملف، 2092 سطر، 0 secrets

في هذه الجلسة ما توفر لي GitHub auth، فأرفعته في ملفات محلية جاهزة. اختر طريقة وتنفّذ من منصّتك:

---

## الطريقة 1 — تشغيل من Claude Code أو Terminal مع GitHub auth (الأفضل)

```bash
# 1. افتح مجلد عمل
cd ~/Desktop

# 2. انسخ Dealix
git clone https://github.com/VoXc2/dealix.git
cd dealix

# 3. نزّل الـ patch من workspace
# (انقل dealix_sales_kit.patch من How to use Claude لـ ~/Desktop/dealix/)

# 4. طبّق الـ patch
git checkout -b sales-kit-2026-04-23
git am < ~/Desktop/dealix_sales_kit.patch

# 5. ارفع
git push -u origin sales-kit-2026-04-23

# 6. افتح PR
gh pr create --title "docs(sales): add complete sales kit" --body "11 sales assets for revenue launch. No secrets." --base main
gh pr merge --squash --delete-branch
```

---

## الطريقة 2 — GitHub Web UI (بدون terminal)

1. روح على: **https://github.com/VoXc2/dealix**
2. اضغط على **branch** dropdown (أعلى يسار) → **View all branches**
3. اضغط **New branch** → اكتب اسم: `sales-kit-2026-04-23`
4. بعد إنشاء الـ branch، روح على: `https://github.com/VoXc2/dealix/tree/sales-kit-2026-04-23`
5. اضغط **Add file** → **Upload files**
6. أنشئ مجلد `docs/sales-kit/` واسحب الـ 12 ملف من workspace هذا:
   - `README.md` (في الـ sales-kit workspace — موجود هنا في tar)
   - `START_HERE.md`
   - `RAILWAY_MOYASAR_STEP_BY_STEP.md`
   - `dealix_leads_20_real.md`
   - `dealix_personalized_messages.md`
   - `dealix_demo_script_30min.md`
   - `dealix_objection_handler.md`
   - `dealix_roi_calculator.html`
   - `dealix_pilot_agreement.md`
   - `dealix_onepager.md`
   - `dealix_14day_tracker.html`
   - `dealix_1_riyal_test.sh`
7. اكتب commit message: `docs(sales): add complete sales kit`
8. اضغط **Commit changes**
9. بعدها: **Compare & pull request** → **Merge pull request**

---

## الطريقة 3 — Git Bundle (أسرع لو عندك git محلياً)

```bash
cd ~/Desktop
git clone https://github.com/VoXc2/dealix.git
cd dealix

# انسخ dealix_sales_kit.bundle من workspace لـ ~/Desktop/dealix/
git fetch ~/Desktop/dealix_sales_kit.bundle sales-kit-2026-04-23:sales-kit-2026-04-23
git push origin sales-kit-2026-04-23

# بعدها افتح PR من GitHub web
```

---

## الطريقة 4 — الأسهل: تشغيل مباشر من workspace (إذا محلياً)

الملفات جاهزة على جهازك في:
```
C:\Users\[اسمك]\AppData\...\jolly-charming-darwin\How to use Claude\
```
أو على macOS:
```
~/Library/.../How to use Claude/
```

افتح terminal هناك وشغّل:

```bash
# ملف bash سأنشئه الآن — شغّله من داخل workspace
bash push_sales_kit_to_github.sh
```

---

## ✅ النتيجة بعد الرفع

على `https://github.com/VoXc2/dealix/tree/main/docs/sales-kit/` راح تجد:
- 12 ملف sales kit
- README.md يشرح كل شي
- يشتغلون من أي منصة (web, mobile, Claude Code, Cursor, VS Code)

---

## 🎯 بعد الرفع تقدر

- تفتح الـ repo من أي جهاز وترى كل الأصول
- تشتغل عليها من **Claude Code، Cursor، أو GitHub.dev**
- تشارك روابط محددة مع فريقك/مستثمرين
- تضيف ملفات جديدة وتسحبها بين المنصات
- تنشر `docs/sales-kit/` كـ GitHub Pages (موقع ويب) بنقرة واحدة

---

## 📎 الملفات الجاهزة في workspace للتنزيل

| الملف | الحجم | الاستخدام |
|-------|--------|-----------|
| `dealix_sales_kit.patch` | 95 KB | طبّقه بـ `git am` |
| `dealix_sales_kit.bundle` | 36 KB | استخدمه بـ `git fetch` |
| `dealix_sales_kit.tar.gz` | 30 KB | فكّه لأي مكان |

الثلاثة يحتوون **نفس المحتوى** — اختر الأنسب لطريقتك.
