# Dealix — نظام الفوترة (عمل حر + ZATCA جاهز)

> دليل عملي + قوالب جاهزة لإصدار فواتير احترافية من وثيقة العمل الحر، متوافقة مع ZATCA، جاهزة للاستخدام اليوم.

**آخر تحديث**: أبريل 2026 | **الحالة**: جاهز للتشغيل

---

## 🎯 الواقع الحالي لـ Sami

**عندك**:
- ✅ حساب بنكي تجاري
- ✅ وثيقة عمل حر (من منصة "عمل")
- ✅ قدرة إصدار فواتير

**نبغى نستثمر هذا كاملاً** من اليوم الأول — قبل حتى تسجيل LLC.

---

## 📋 الخيارات المتاحة لإصدار الفواتير

### الخيار 1: منصة "عمل" (الأسرع — اليوم)
**المنصة**: freelance.sa  
**المزايا**:
- ✅ معتمدة حكومياً
- ✅ VAT + ZATCA integration تلقائي
- ✅ رسوم بسيطة (1.5% من قيمة الفاتورة)
- ✅ توثيق تلقائي للـ Freelance Permit
- ✅ تعامل مباشر مع جهات حكومية وشركات

**كيف تصدر فاتورة**:
1. سجّل دخول على [freelance.sa](https://freelance.sa)
2. Dashboard → "إصدار فاتورة جديدة"
3. عبّي:
   - اسم العميل + الرقم الضريبي
   - الخدمة + السعر
   - تاريخ الاستحقاق
4. المنصة تولّد فاتورة:
   - رقم فاتورة فريد
   - QR Code للـ ZATCA
   - XML متوافق
   - PDF بتصميم احترافي
5. إرسال تلقائي للعميل بالإيميل
6. تتبّع حالة الدفع

**التكلفة**:
- 0 ر.س اشتراك
- 1.5% من كل فاتورة (10 ر.س لفاتورة 999 ر.س)

---

### الخيار 2: Invoice Generator مخصّص (أفضل طويل المدى)
**الأداة**: Dealix Invoicing Module  
**المزايا**:
- ✅ بعلامتك التجارية بالكامل
- ✅ تكامل مباشر مع Moyasar (دفع فوري)
- ✅ automated reminders
- ✅ revenue analytics
- ✅ تصدير ZATCA-compliant

**الكود المقترح** (api/invoicing/zatca.py):
```python
from datetime import datetime
from uuid import uuid4
import hashlib
import base64

class DealixInvoice:
    def __init__(self, customer, items, issue_date=None):
        self.uuid = str(uuid4())
        self.invoice_number = self._generate_number()
        self.customer = customer
        self.items = items
        self.issue_date = issue_date or datetime.now()
        self.vat_rate = 0.15
        
    def _generate_number(self):
        """INV-YYYYMMDD-XXXX format"""
        timestamp = datetime.now().strftime('%Y%m%d')
        seq = self._get_daily_sequence()
        return f"INV-{timestamp}-{seq:04d}"
    
    def subtotal(self):
        return sum(item['price'] * item['qty'] for item in self.items)
    
    def vat_amount(self):
        return round(self.subtotal() * self.vat_rate, 2)
    
    def total(self):
        return self.subtotal() + self.vat_amount()
    
    def generate_qr_tlv(self):
        """ZATCA TLV QR code format."""
        def tlv(tag, value):
            val = value.encode('utf-8') if isinstance(value, str) else value
            return bytes([tag, len(val)]) + val
        
        seller_name = "Dealix / سامي العسيري"
        vat_number = "YOUR_VAT_NUMBER"
        timestamp = self.issue_date.isoformat()
        total = f"{self.total():.2f}"
        vat = f"{self.vat_amount():.2f}"
        
        tlv_data = (
            tlv(1, seller_name) +
            tlv(2, vat_number) +
            tlv(3, timestamp) +
            tlv(4, total) +
            tlv(5, vat)
        )
        return base64.b64encode(tlv_data).decode('utf-8')
    
    def generate_pdf(self):
        """Generate ZATCA-compliant PDF with QR code."""
        # Uses WeasyPrint + jinja2 template
        return render_invoice_pdf(self)
    
    def send_to_customer(self):
        """Email the invoice + payment link via Moyasar."""
        payment_url = create_moyasar_payment_url(
            amount=int(self.total() * 100),
            description=f"Invoice {self.invoice_number}"
        )
        send_email(
            to=self.customer.email,
            subject=f"فاتورة Dealix #{self.invoice_number}",
            template='invoice_email',
            context={
                'invoice': self,
                'payment_url': payment_url,
                'pdf_attachment': self.generate_pdf()
            }
        )
```

---

### الخيار 3: مزوّد خارجي (للسرعة القصوى)
**الخيارات**:
- **Moyasar Invoices** — مدمجة مع المدفوعات
- **Odoo Saudi** — ERP كامل
- **Zoho Invoice** — رخيص + عربي

**الأنسب للمرحلة**: **Moyasar Invoices** — لأنك أصلاً مربوط معهم للـ payment processing.

---

## 📄 قوالب فواتير جاهزة (للاستخدام الفوري)

### قالب 1: فاتورة Pilot (1 ر.س)
```
┌─────────────────────────────────────────────────┐
│  DEALIX                                         │
│  الذكاء الاصطناعي للتجارة السعودية              │
│                                                 │
│  فاتورة ضريبية مبسّطة                            │
│  Simplified Tax Invoice                         │
│─────────────────────────────────────────────────│
│                                                 │
│  رقم الفاتورة: INV-20260423-0001                │
│  التاريخ: 23 أبريل 2026                         │
│                                                 │
│  البائع:                                        │
│  سامي العسيري                                   │
│  وثيقة عمل حر: [رقم الوثيقة]                    │
│  الرقم الضريبي: [عند التسجيل]                   │
│                                                 │
│  المشتري:                                       │
│  [اسم العميل]                                   │
│                                                 │
│─────────────────────────────────────────────────│
│  الوصف          | الكمية | السعر   | الإجمالي  │
│─────────────────────────────────────────────────│
│  اشتراك Dealix  |   1    | 0.87    | 0.87      │
│  تجربة 7 أيام   |        |         |           │
│─────────────────────────────────────────────────│
│                                                 │
│  المجموع قبل الضريبة:                   0.87    │
│  ضريبة القيمة المضافة (15%):             0.13   │
│  المجموع النهائي:                       1.00    │
│                                                 │
│  [QR Code ZATCA]                                │
│                                                 │
│  طريقة الدفع: بطاقة ائتمان عبر Moyasar          │
│  حالة الدفع: مدفوع ✓                            │
│                                                 │
│  شكراً لتعاملك مع Dealix                        │
│─────────────────────────────────────────────────┘
```

### قالب 2: فاتورة Starter Monthly (999 ر.س)
```
┌─────────────────────────────────────────────────┐
│  DEALIX                                         │
│  فاتورة ضريبية                                  │
│  Tax Invoice                                    │
│─────────────────────────────────────────────────│
│  رقم: INV-20260501-0015                        │
│  التاريخ: 1 مايو 2026                           │
│  استحقاق: 15 مايو 2026                          │
│─────────────────────────────────────────────────│
│                                                 │
│  من: سامي العسيري (Dealix)                      │
│  وثيقة عمل حر: XX-XXXXXX                        │
│                                                 │
│  إلى: [شركة العميل]                             │
│  الرقم الضريبي: 3XX-XXX-XX-X                    │
│  العنوان: الرياض، المملكة العربية السعودية       │
│                                                 │
│─────────────────────────────────────────────────│
│  الوصف                      | الإجمالي         │
│─────────────────────────────────────────────────│
│  اشتراك Starter - مايو 2026 | 868.70           │
│  منصة Dealix AI للتسويق     |                  │
│─────────────────────────────────────────────────│
│                                                 │
│  المجموع قبل الضريبة:            868.70 ر.س     │
│  ضريبة القيمة المضافة (15%):     130.30 ر.س     │
│  المجموع النهائي:                999.00 ر.س     │
│                                                 │
│  رقم الـ IBAN للتحويل:                          │
│  SAXXXXXXXXXXXXXXXXXXXXXXXXX                    │
│  بنك: الراجحي                                    │
│  اسم المستفيد: سامي العسيري                      │
│                                                 │
│  [QR Code ZATCA]                                │
│                                                 │
│  ملاحظات:                                       │
│  - الدفع خلال 15 يوم من تاريخ الفاتورة          │
│  - للاستفسار: sami.assiri11@gmail.com          │
│                                                 │
└─────────────────────────────────────────────────┘
```

### قالب 3: فاتورة خدمة One-time (5,000 ر.س)
```
┌─────────────────────────────────────────────────┐
│  DEALIX — Marketing Strategy Audit              │
│  فاتورة ضريبية                                  │
│─────────────────────────────────────────────────│
│  رقم: INV-20260610-0089                        │
│  التاريخ: 10 يونيو 2026                         │
│─────────────────────────────────────────────────│
│                                                 │
│  الخدمة: Marketing Strategy Audit              │
│  المدة: 2 أسابيع (15-30 مايو 2026)             │
│                                                 │
│  Deliverables المُسلّمة:                         │
│  ✓ 30-point audit report (PDF - 45 صفحة)       │
│  ✓ SWOT analysis مفصّل                          │
│  ✓ Competitor benchmarking (5 منافسين)         │
│  ✓ 12-month roadmap                            │
│  ✓ Top 10 quick wins report                    │
│  ✓ Workshop presentation (90 دقيقة)            │
│                                                 │
│─────────────────────────────────────────────────│
│  المجموع قبل الضريبة:        4,347.83 ر.س       │
│  ضريبة القيمة المضافة (15%):   652.17 ر.س       │
│  المجموع النهائي:            5,000.00 ر.س       │
│─────────────────────────────────────────────────│
│                                                 │
│  شروط الدفع:                                    │
│  - 50% مقدماً (تم استلامه)                      │
│  - 50% عند التسليم (هذه الفاتورة)              │
│  - طريقة الدفع: تحويل بنكي أو Moyasar          │
│                                                 │
│  [QR Code ZATCA]                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔢 ترقيم الفواتير

### النمط المقترح
`INV-YYYYMMDD-XXXX`

- **INV**: prefix ثابت
- **YYYYMMDD**: تاريخ الإصدار
- **XXXX**: رقم تسلسلي يومي (يبدأ 0001)

**أمثلة**:
- `INV-20260423-0001` → أول فاتورة في 23 أبريل
- `INV-20260501-0023` → الفاتورة #23 في 1 مايو

### تتبّع الأرقام
استخدم spreadsheet بسيط (Google Sheets):

| Date | INV Number | Customer | Amount | VAT | Total | Status | Payment Method |
|------|-----------|----------|--------|-----|-------|--------|----------------|
| 2026-04-23 | INV-20260423-0001 | شركة أ | 868.70 | 130.30 | 999.00 | Paid | Moyasar |
| 2026-04-25 | INV-20260425-0001 | شركة ب | 2,607.83 | 391.30 | 2,999.13 | Pending | Bank Transfer |

---

## 💳 إعداد الدفعات (Payment Methods)

### المزيج الموصى به

| الطريقة | متى نستخدمها | الرسوم |
|---------|--------------|--------|
| **Moyasar** | SaaS subscriptions + small invoices (< 10k) | 2.75% |
| **تحويل بنكي (الراجحي)** | Enterprise + invoices > 10k | 0 ر.س |
| **STC Pay** | small consulting < 5k | 1% |
| **PayPal** (للخارج فقط) | أمريكا/أوروبا | 4.4% + 0.30 $ |
| **Crypto** (USDT) | للعملاء الدوليين فقط | 0.5% |

### قواعد الدفع في الفواتير
1. **دائماً قدّم طريقتين على الأقل** (بنك + Moyasar)
2. **اذكر الـ IBAN صريح** في الفاتورة
3. **شروط الدفع**: Net 15 للـ SaaS، Net 30 للـ enterprise
4. **خصم على الدفع المبكر**: 2% إذا دفع خلال 7 أيام
5. **غرامة على التأخير**: 1.5%/شهر بعد 30 يوم (يُذكر في TOS)

---

## 📋 Checklist لكل فاتورة (قبل الإرسال)

- [ ] رقم الفاتورة مُصدَر صحيح (sequence)
- [ ] تاريخ الإصدار + الاستحقاق واضح
- [ ] اسم العميل كامل + رقم ضريبي (إذا مسجّل VAT)
- [ ] الوصف دقيق (مو "خدمات عامة")
- [ ] المبلغ قبل الضريبة + VAT 15% + الإجمالي
- [ ] QR Code من ZATCA (إذا مسجّل VAT)
- [ ] شروط الدفع واضحة
- [ ] IBAN صحيح (راجع!)
- [ ] إمضاء أو logo رقمي
- [ ] CC: نسخة للـ accounting email

---

## 🤖 Automation — جعل كل شي تلقائياً

### المستوى 1: Today (يمكن التشغيل فوراً)
**Tool**: Google Sheets + Apps Script

```javascript
// google apps script - on new row in "Invoices" sheet
function onInvoiceCreated() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const row = sheet.getActiveRange().getRow();
  const invoice = sheet.getRange(row, 1, 1, 10).getValues()[0];
  
  // Generate PDF
  const pdf = generatePDF(invoice);
  
  // Send email
  GmailApp.sendEmail(
    invoice[3], // customer email
    `فاتورة Dealix #${invoice[1]}`,
    `مرفقة فاتورتك.\nالرجاء الدفع خلال ${invoice[6]} يوم.\n\nسامي`,
    { attachments: [pdf] }
  );
  
  // Update status
  sheet.getRange(row, 10).setValue('Sent');
}
```

### المستوى 2: Q3 2026 (بعد Hire #1)
**Tool**: Dealix Invoicing Module (بناء داخلي)
- إصدار من dashboard
- تكامل مع Moyasar
- automated reminders (3, 7, 14 يوم)
- late payment handling
- monthly revenue reports

### المستوى 3: Q1 2027 (Maturity)
**Tool**: Full AR (Accounts Receivable) system
- Aging reports
- Credit notes
- Multi-currency
- Subscription billing
- Revenue recognition (ASC 606)

---

## 📊 تقارير مالية أسبوعية (تلقائياً)

### Every Monday Morning Email
```
📊 Dealix Financial Snapshot — الأسبوع [X]

💰 هذا الأسبوع:
   - فواتير مُصدَرة: 5 (قيمة 12,997 ر.س)
   - فواتير مدفوعة: 3 (قيمة 7,997 ر.س)
   - فواتير معلّقة: 2 (قيمة 5,000 ر.س)

📈 Month-to-date:
   - إجمالي الفواتير: 22
   - إيرادات: 47,985 ر.س
   - Collections rate: 87%
   - متوسط وقت الدفع: 11 يوم

⚠️  تنبيهات:
   - شركة X: فاتورة متأخرة 25 يوم (5,000 ر.س)
   - شركة Y: فاتورة متأخرة 8 أيام (2,999 ر.س)
   
🎯 الأسبوع القادم:
   - متوقع إصدار: 7 فواتير
   - متوقع استلام: 9,000 ر.س
```

---

## 🔒 قانونياً — ما يجب معرفته

### متطلبات ZATCA (2026)
1. **كل فاتورة عربي (إجباري)** — إنجليزي اختياري كـ secondary
2. **QR Code** لكل فاتورة (simplified) أو signed invoice (standard)
3. **XML format** UBL 2.1 للـ archiving
4. **المدة الاحتفاظ**: 6 سنوات
5. **e-invoicing** إلزامي منذ 2021 للمرحلة 1، 2023 للمرحلة 2

### عقوبات عدم الامتثال
- **غرامة**: 1,000 - 50,000 ر.س حسب نوع المخالفة
- **تكرار**: إغلاق المنشأة مؤقتاً
- **تجنّبها**: استخدم منصة معتمدة (freelance.sa أو Moyasar)

### استشارة قانونية
- **الخيار الرخيص**: Legal LinkedIn — 500 ر.س/ساعة
- **Enterprise**: Khoshaim & Associates — 2,000 ر.س/ساعة
- **Retainer**: 2,500 ر.س/شهر للإرشاد العام

---

## 🚀 خطة التنفيذ (30 يوم)

### الأسبوع 1: Setup
- [ ] سجّل على freelance.sa (إذا ما سجّلت)
- [ ] أضف الـ IBAN لحسابك التجاري
- [ ] أنشئ spreadsheet Invoice Tracker
- [ ] صمّم قالب فاتورة (Canva/Figma)
- [ ] اكتب Terms of Payment الرسمية

### الأسبوع 2: First Invoices
- [ ] أصدر فاتورة تجريبية (لنفسك) عشان تختبر
- [ ] اختبر payment flow كامل
- [ ] أصدر فاتورة لأول عميل pilot (1 ر.س)
- [ ] وثّق العملية

### الأسبوع 3: Automate
- [ ] اكتب Apps Script للـ automation
- [ ] ربط مع Gmail للإرسال التلقائي
- [ ] Setup reminders (3, 7, 14 يوم)

### الأسبوع 4: Scale
- [ ] قالب لكل tier (Starter, Growth, Scale, Services)
- [ ] Playbook للـ collections (متابعة المتأخرات)
- [ ] Weekly financial report تلقائي

---

## 📞 الدعم

- **ZATCA Helpdesk**: 19993
- **freelance.sa Support**: via platform
- **Moyasar Support**: support@moyasar.com
- **محاسب recommended**: نزار الشمري (500 ر.س/شهر للـ startups)

---

**Dealix — الفوترة بدون تعقيد. الربح بدون انتظار.**
