# Dealix — Payment Test Runbook

## Prerequisites
- [ ] Moyasar account created (moyasar.com)
- [ ] API keys obtained (Secret + Publishable)
- [ ] Keys added to Railway Variables
- [ ] Railway redeployed

## Test Steps

### Step 1: Add Keys to Railway
```
MOYASAR_SECRET_KEY=sk_test_...
MOYASAR_PUBLISHABLE_KEY=pk_test_...
```

### Step 2: Test 1 SAR Checkout
```bash
curl -X POST https://api.dealix.me/api/v1/pricing/checkout \
  -H "Content-Type: application/json" \
  -d '{"plan_id":"pilot","customer_name":"Sami Test","customer_email":"sami@dealix.me","customer_phone":"966597788539"}'
```

### Step 3: Verify Response
Expected: checkout URL or payment link
If error: check Railway logs

### Step 4: Complete Payment
- Open checkout URL
- Use test card: 4111 1111 1111 1111
- Verify success redirect

### Step 5: Verify Webhook
- Check Railway logs for payment confirmation
- Verify customer record updated

## Manual Payment Fallback (ACTIVE — use until Moyasar works)
1. Send bank transfer details:
   ```
   البنك: مصرف الإنماء
   الاسم: سامي محمد زايد عسيري — ذكاء الاعمال
   رقم الحساب: 68207328877000
   IBAN: SA3305000068207328877000
   SWIFT: INMASARIXXX
   المبلغ: 499 ريال (Pilot) أو 990 ريال (Starter)
   المرجع: Dealix Pilot - [اسم الشركة]
   ```
2. العميل يرسل إيصال التحويل
3. تأكد من وصول المبلغ في تطبيق الإنماء
4. أرسل رسالة تأكيد + ابدأ onboarding
5. سجّل في scorecard

## Verdict After Test
- Payment works → Revenue Live
- Payment fails → Debug with Moyasar docs
- Manual payment received → Revenue Live (manual)
