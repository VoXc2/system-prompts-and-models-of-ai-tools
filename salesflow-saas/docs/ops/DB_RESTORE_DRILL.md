# Dealix — DB Restore Drill

## متى تحتاج restore
- corruption بعد migration فاشل
- حذف data بالغلط
- ransomware (unlikely)

## الخطوات
1. Railway Dashboard → Database → Backups
2. اختر آخر backup قبل المشكلة
3. Restore → confirm
4. Verify: test API endpoints
5. Check data integrity
6. إذا ما فيه backup: اتصل بـ Railway support

## الوقاية
- Railway يسوي daily backup تلقائي
- قبل أي migration: تأكد من backup حديث
