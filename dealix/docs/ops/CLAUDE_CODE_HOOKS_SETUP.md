# Claude Code — Hooks لـ Dealix (إعداد اختياري)

السكربتات تقرأ **JSON من stdin** (حدث `PreToolUse` من Claude Code). إذا لم يكن الشكل متوقعاً، تخرج `0` ولا تمنع (fail-open) لتجنب كسر الجلسة.

## السكربتات

- `dealix/scripts/guard_dealix_changes.py` — لأدوات تعديل ملفات (`Edit`, `Write`, `MultiEdit`, …)
- `dealix/scripts/guard_dealix_bash.py` — لأمر `Bash`

شغّلها من **جذر الريبو** (كما في الأمثلة أدناه). على Windows إذا لم يكن الأمر `python` في الـ PATH، استبدله بـ `py -3` في إعدادات الـ hooks وفي اختبار stdin أدناه.

## مثال `hooks` في `.claude/settings.json`

انسخ إلى إعدادات المشروع وادمج مع المفاتيح الموجودة (لا تحذف `projectInstructions` إلخ):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python dealix/scripts/guard_dealix_changes.py"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python dealix/scripts/guard_dealix_bash.py"
          }
        ]
      }
    ]
  }
}
```

> تحقق من صيغة المخطط لدى نسخة Claude Code لديك؛ قد يختلف اسم المفتاح أو شكل الـ matcher.

## خروج الحظر

- عند منع العملية: سكربتاتنا تطبع سبباً على **stderr** وتخرج برمز **2** (أو غير صفر حسب ما يتوقعه عميل الـ hooks).

## اختبار يدوي

```bash
echo "{\"hook_event_name\":\"PreToolUse\",\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"dealix/api/main.py\"}}" | python dealix/scripts/guard_dealix_changes.py
echo "{\"hook_event_name\":\"PreToolUse\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push --force\"}}" | python dealix/scripts/guard_dealix_bash.py
```
