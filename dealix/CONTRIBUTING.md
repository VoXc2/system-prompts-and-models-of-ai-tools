# Contributing | المساهمة

Thanks for considering a contribution! | شكراً لاهتمامك بالمساهمة!

## 🚀 Quick start

```bash
git clone https://github.com/YOUR-ORG/ai-company-saudi.git
cd ai-company-saudi
make setup
```

This creates a virtualenv, installs dev deps, installs pre-commit hooks,
and copies `.env.example` → `.env` for you.

## 🧰 Development workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```
2. **Make changes** — write code + tests.
3. **Run quality checks**:
   ```bash
   make lint
   make test
   ```
4. **Commit** — pre-commit hooks run automatically (gitleaks, ruff, mypy, etc.).
5. **Open a Pull Request** using the PR template.

## 📝 Commit message style

Conventional Commits (loose):

- `feat(phase8): add booking confirmation email`
- `fix(intake): normalize Kuwaiti phone numbers`
- `docs: update README install instructions`
- `chore(deps): bump fastapi to 0.116`
- `test(icp): cover edge case for budget in range`
- `refactor(core): extract LLM client base`

## 🧪 Testing requirements

- Every new agent MUST have at least one unit test.
- Every new API endpoint MUST have at least one integration test.
- Aim for meaningful coverage — not just line-count.

## 🔒 Security

- **NEVER commit secrets.** The pre-commit hooks should catch it, but be vigilant.
- If you find a vulnerability, please see [SECURITY.md](SECURITY.md) — do NOT open a public issue.

## 🌍 Bilingual contributions

- Docstrings: English primary, Arabic translation where it adds value (especially user-facing).
- User-facing strings (sales scripts, prompts, docs): provide both AR and EN.
- Commit messages + PR descriptions: English preferred, Arabic acceptable.

## 🏷️ Style

- Python: `ruff` + `black` + `mypy` — run `make format` before committing.
- Line length: 100.
- Type hints: required on new code.
- Docstrings: Google-style for public APIs.

## 📦 Releasing (maintainers)

1. Bump version in `pyproject.toml` and `.env.example`.
2. Update `CHANGELOG.md`.
3. Commit, tag: `git tag -a v2.x.x -m "v2.x.x"`.
4. Push: `git push && git push --tags`.
5. GitHub Actions will handle the release + Docker publish.

---

## 🇸🇦 بالعربية

شكراً لمساهمتك!

### البدء السريع

```bash
git clone https://github.com/YOUR-ORG/ai-company-saudi.git
cd ai-company-saudi
make setup
```

### سير العمل

1. أنشئ فرعاً من `main`.
2. اكتب الكود + الاختبارات.
3. شغّل `make lint` و `make test`.
4. كل commit يمر عبر pre-commit hooks تلقائياً.
5. افتح Pull Request.

### متطلبات الاختبار

- كل وكيل جديد يحتاج اختبار وحدة واحد على الأقل.
- كل endpoint جديد يحتاج اختبار تكامل واحد على الأقل.

### الأمن

- **لا ترفع أبداً أي أسرار.** pre-commit hooks ستمسكها، لكن انتبه.
- إذا اكتشفت ثغرة، راجع [SECURITY.md](SECURITY.md).

### الأسلوب ثنائي اللغة

- docstrings: الإنجليزية أساسية، مع عربي حيث يضيف قيمة.
- النصوص التي يراها المستخدم: العربية والإنجليزية.
- رسائل commit: الإنجليزية مفضّلة، العربية مقبولة.
