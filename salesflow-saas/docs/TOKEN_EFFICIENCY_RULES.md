# TOKEN_EFFICIENCY_RULES.md — قواعد توفير التوكنز في Dealix

> هذا الملف إلزامي لأي وكيل ذكاء اصطناعي يعمل على Dealix (Claude Code, Cursor, Codex, GitHub Copilot, Warp, Windsurf, etc.).
> الهدف: **تخفيض استهلاك التوكنز/الطلبات بنسبة 50-70% بدون فقدان جودة**.

---

## 1. قواعد مطلقة (Must-Follow)

### 1.1 استخدم CLI بدل MCP دائماً
- ✅ `gh pr view 16 --json title,body,files` — رخيص وسريع
- ❌ GitHub MCP connector — يحشر كل tool schemas في الـcontext على الجانبين (input + output)
- قاعدة عامة: إذا وُجد CLI لأداة، استخدمه.

### 1.2 لا تقرأ ملفاً بأكمله إذا كنت تحتاج جزءاً منه
- ✅ `grep -n "executive_roi_service" file.py` ثم `read` بـoffset/limit حول السطر
- ❌ `cat file.py` أو `read` للملف كامل إذا كان >200 سطر
- استثناء: الملفات الصغيرة (<100 سطر) — اقرأها كاملة.

### 1.3 استخدم `gh` بدل استنساخ الريبو
- ✅ `gh pr view 16 --json files --jq '.files[].path'` — يرجّع قائمة الملفات بس
- ✅ `gh api repos/OWNER/REPO/contents/PATH` — يرجّع ملف واحد
- ❌ `git clone` لكل الريبو بس عشان تفحص ملفاً واحداً
- استثناء: إذا كنت ستعدّل 5+ ملفات في نفس الجلسة، الاستنساخ أرخص.

### 1.4 استخدم `--depth 1` و `--jq` دائماً
- ✅ `gh repo clone owner/repo -- --depth 1 --single-branch`
- ✅ `gh api ... --jq '.field.subfield'` — يصفّي الـJSON قبل ما يوصل الـcontext

---

## 2. قواعد الـContext

### 2.1 امسح الـcontext بين المهام المختلفة
- مهمة "إصلاح CI bug" → جلسة جديدة
- مهمة "إضافة endpoint جديد" → جلسة جديدة
- لا تكمل في نفس الجلسة لمهام غير مرتبطة — الـcontext يتضخم.

### 2.2 لا تضيف الوثائق إلا عند الحاجة
- لا تقرأ `DEALIX_VISION.md` أو `MASTER_BLUEPRINT.mdc` إلا إذا المهمة استراتيجية.
- المهام التقنية (bug fixes, refactors) ما تحتاج رؤية المنتج.

### 2.3 قلّص output الأوامر بنفسك
- ✅ `| head -30`, `| tail -20`, `| wc -l`
- ✅ `2>&1 | grep ERROR` — فلتر الأخطاء فقط
- ❌ `pytest -v` — استخدم `pytest -q` أو `pytest --tb=line`

---

## 3. قواعد الكود

### 3.1 عدّل، لا تعيد الكتابة
- ✅ `edit` tool بـ old_string/new_string — يرسل الفرق فقط
- ❌ `write` لملف موجود بمحتوى كامل جديد

### 3.2 استخدم نموذجاً مناسباً لحجم المهمة
| نوع المهمة | النموذج المقترح |
|------------|------------------|
| تخطيط معماري، قرارات كبيرة | Claude Opus 4.7 / GPT-5.4 |
| كتابة كود، بناء features | Claude Sonnet 4.6 |
| إصلاح imports، تنسيق، bugs بسيطة | Gemini 3 Flash / GPT-5.4 mini |
| استخراج بيانات من JSON | Gemini 3 Flash |

### 3.3 اكتب اختبارات مبكراً
- اختبار فاشل واضح = معلومة دقيقة للوكيل = إصلاح سريع = توكنز أقل
- اختبار غامض = الوكيل يخمّن = توكنز ضائعة

---

## 4. قواعد الـRepo

### 4.1 لا ترفع ملفات ضخمة إلى الريبو
- لا ترفع `node_modules/`, `.venv/`, `dist/`, `build/`
- لا ترفع ملفات `.zip` (مثل `dealix-frontend.zip` الموجود حالياً — يجب حذفه)
- تأكد من `.gitignore` شامل.

### 4.2 اكتب README بإيجاز
- الـAI سيقرأ README في كل جلسة. كل كلمة زايدة = توكنز مضاعفة عبر مئات الجلسات.
- احتفظ بـREADME الرئيسي تحت 150 سطر. التفاصيل في ملفات منفصلة.

### 4.3 حافظ على llms.txt محدَّث
- ملف `/llms.txt` في جذر الريبو يوجّه الـAI لأهم الملفات.
- مثال في `salesflow-saas/llms.txt`:
  ```
  # Dealix
  High-priority context files for AI agents:
  - CLAUDE.md — operating rules (READ FIRST)
  - AGENTS.md — project identity
  - docs/ARCHITECTURE.md — system design
  - backend/app/main.py — API entrypoint
  - backend/app/api/v1/router.py — all routes
  ```

---

## 5. قواعد الـCI/Tests

### 5.1 فشل CI = توكنز ضائعة
- كل push يُفشل CI يعني: اختبارات تعيد التشغيل + تحليل logs + إصلاح + إعادة push
- شغّل الاختبارات محلياً قبل الـpush دائماً:
  ```bash
  cd salesflow-saas/backend && pytest tests -q --tb=line
  cd salesflow-saas/frontend && npm run lint && npm run build
  ```

### 5.2 Pre-commit hooks
- مفعّلة في `.pre-commit-config.yaml` — لا تعطلها.
- تلقط أخطاء بسيطة (imports, formatting) قبل ما توصل للـAI agent.

---

## 6. المراقبة والقياس

### 6.1 تتبّع الاستهلاك أسبوعياً
- Anthropic Console → Usage
- GitHub Copilot → Settings → Copilot usage
- OpenAI Platform → Usage

### 6.2 إذا كلفة جلسة > 500K توكن
توقف. المهمة غلط مقسّمة. ابدأ جلسة جديدة مع scope أضيق.

---

## 7. قائمة فحص نهاية الجلسة

قبل إغلاق أي جلسة عمل:
- [ ] كل الاختبارات تمر محلياً
- [ ] CI أخضر على PR
- [ ] لم أقرأ ملفاً بالكامل بدون حاجة
- [ ] استخدمت `gh` بدل MCP
- [ ] كتبت commit message واضح (يوفّر على الوكيل القادم قراءة الـdiff)

---

**المراجع:**
- [Sabrina Ramonov — 6 Ways I Cut My Claude Token Usage](https://www.sabrina.dev/p/6-ways-i-cut-my-claude-token-usage)
- [Supermemory — LLM Costs](https://supermemory.ai/blog/llm-costs-skyrocketing-real-experts-weigh-in/)
- [Symflower — Managing LLM Costs](https://symflower.com/en/company/blog/2024/managing-llm-costs/)
- [Cursor Forum — Code Caching Ideas](https://forum.cursor.com/t/idea-optimize-llm-usage-with-a-local-filter-code-caching-reduce-token-costs/91985)
