# Dealix — Invoice & Collection Flow

## Flow
```
Demo → Interest → Payment Link → Payment → Invoice → Activate → Report
```

## Step-by-step

### 1. After Demo (interested)
```
أرسل:
"شكراً [الاسم]. كما اتفقنا: Pilot 7 أيام بـ 499 ريال مع ضمان استرداد.
رابط الدفع: [checkout link]
أو تحويل بنكي: [bank details]"
```

### 2. Payment Received
- Record in scorecard
- Send confirmation:
```
"تم استلام الدفع. نبدأ خلال 24 ساعة.
أحتاج: رقم واتساب البزنس + 3 أسئلة تأهيل لعملائك."
```

### 3. Invoice
- Generate e-invoice (ZATCA compliant when applicable)
- Send via email
- Record invoice number

### 4. Pilot Period (7 days)
- Daily report to client
- Day 6: "النتائج + نكمّل بـ Starter 990/شهر؟"

### 5. Conversion
- If yes → Starter invoice → monthly billing
- If no → refund if requested → ask for feedback

## Collection Rules
- Payment before activation (no exceptions for pilot)
- Starter: monthly invoice, 7-day grace period
- Agency: setup fee upfront, MRR monthly
