# حادثة تسريب GitHub PAT — إجراءات وإرشادات

## ماذا حدث؟

ظهر **Personal Access Token (PAT)** لـ GitHub في محادثة خارجية (مثلاً ChatGPT أو شاشة مشاركة). أي توكن يُرى بهذه الطريقة يُعتبر **مكشوفاً (compromised)** حتى لو لم يُلصق في الريبو.

## المطلوب من صاحب الحساب فوراً

1. افتح [GitHub → Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens).
2. **احذف (Revoke)** التوكن المكشوف بالكامل.
3. أنشئ توكناً جديداً **فقط** عند الحاجة، ويفضّل **Fine-grained PAT** بأقل صلاحيات ولأقصر مدة.
4. **لا** تضع PAT في محادثات، ولا في لقطات شاشة، ولا في Issues/PR descriptions.

## المصادقة المحلية الموصى بها

```bash
gh auth login
```

أو SSH keys للـ `git` بدلاً من لصق PAT في remote URL.

## سياسة الريبو

- **لا أسرار** في الملفات المتتبعة: لا `ghp_`، لا `github_pat_`، لا مفاتيح API خام في الكود.
- استخدم `.env` (مُهمل في `.gitignore`) ومتغيرات بيئة على السيرفر فقط.

## فحص الريبو محلياً

شغّل من جذر المشروع (تجاهل `.git` و`.venv` و`node_modules` و`htmlcov`):

```bash
rg -n "ghp_|github_pat_" --glob '!htmlcov/**' --glob '!.git/**' --glob '!.venv/**' .
```

أو PowerShell:

```powershell
Get-ChildItem -Recurse -File -Exclude *.git* | Select-String -Pattern "ghp_|github_pat_" -ErrorAction SilentlyContinue
```

إذا وُجد سر **في commit تاريخي**: أبلغ الفريق؛ قد يلزم **تدوير السر** و**تنظيف التاريخ (BFG/git filter-repo)** — لا يُنفَّذ تلقائياً بدون قرار صاحب الريبو.

## سجل هذا المستند

- تاريخ الإنشاء: ضمن حملة تثبيت PR #125.
- الغرض: توثيق الحادثة ومنع التكرار.
