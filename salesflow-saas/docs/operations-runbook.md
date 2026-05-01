# Operations Runbook — Launch Day

## Incident Severity
- **SEV-1:** تعطل كامل/فقدان خدمة أساسية.
- **SEV-2:** خلل مؤثر جزئياً مع بديل متاح.
- **SEV-3:** خلل منخفض التأثير.

## Triage Workflow
1. استلام التنبيه.
2. تحديد النطاق (tenant/region/service).
3. تقييم الشدة.
4. تعيين Incident Commander.
5. تنفيذ mitigations.
6. تحديث الحالة كل 15 دقيقة.

## Quick Commands (Template)
```bash
# health check
curl -fsS http://localhost:8000/health || echo "health failed"

# restart app service (example)
systemctl restart dealix-api
systemctl restart dealix-worker

# logs (last 200 lines)
journalctl -u dealix-api -n 200 --no-pager
journalctl -u dealix-worker -n 200 --no-pager
```

## AI Failure Handling
- إذا النموذج المحلي فشل:
  1) تأكيد endpoint
  2) تفعيل/تأكيد fallback
  3) اختبار smoke سريع
  4) متابعة الجودة والتكلفة

## Rollback Decision Matrix
- rollback فوري عند SEV-1 مستمر > 10 دقائق.
- rollback إذا معدلات الأخطاء تتجاوز threshold المتفق.

## Communication Template
- الحالة: Investigating / Identified / Monitoring / Resolved
- الأثر: من المتأثر؟
- الإجراء الحالي: ماذا فعلنا؟
- ETA: متى التحديث القادم؟

## Postmortem (within 24h)
- Root cause
- Detection gaps
- Corrective actions
- Preventive actions + owners + deadlines
