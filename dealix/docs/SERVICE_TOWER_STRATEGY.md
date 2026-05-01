# Service Tower — استراتيجية الخدمات القابلة للبيع

## الرؤية

تحويل قدرات Dealix (Targeting، المنصة، الذكاء، Growth Operator) إلى **خدمات منتَجة** لها: مدخلات، مسار عمل، مخرجات، تسعير، سياسة موافقة، Proof Pack، ومسار ترقية — دون إرسال حي أو شحن تلقائي في مسارات الـ MVP.

## العلاقة مع الكتالوجات الأخرى

- **`platform_services.service_catalog`**: مكونات تقنية واشتراكات/خدمات طبقة المنصة.
- **`service_tower.service_catalog`**: تعريف **بيعي تشغيلي** (برج الخدمات) مع `pricing_range_sar` و`workflow_steps` و`upgrade_path`.
- **`targeting_os`**: استهداف آمن، قوائم، LinkedIn Lead Gen — يغذي توصيات الـ wizard.

## مسارات API

| المسار | الوظيفة |
|--------|---------|
| `GET /api/v1/services/catalog` | برج الخدمات + لقطة من كتالوج المنصة |
| `POST /api/v1/services/recommend` | توصية خدمة من نوع الشركة والهدف |
| `POST /api/v1/services/start` | بدء تشغيل منطقي (تحقق مدخلات فقط) |
| `GET /api/v1/services/{id}/workflow` | خطوات المسار |
| `POST /api/v1/services/{id}/quote` | تقدير SAR (غير ملزم) |
| `GET /api/v1/services/demo/dashboard` | بطاقات عرض داخلية |
| `GET /api/v1/services/ceo/daily-brief` | موجز عربي + أزرار ≤٣ |
| `POST /api/v1/services/approval-card` | بطاقة موافقة لخدمة/إجراء |

التفاصيل في [`docs/architecture/API_CANONICAL_ALIASES.md`](architecture/API_CANONICAL_ALIASES.md).

## القواعد

- لا إرسال حي من هذه المسارات.
- واتساب بارد ممنوع افتراضياً (انظر `whatsapp_compliance_setup` و`targeting_os`).
- لا ضمان نتائج — التسعير والأثر **تقديرات عرض**.

## ترتيب الإطلاق التجاري المقترح

1. `free_growth_diagnostic` → جذب.
2. `list_intelligence` و`first_10_opportunities` → إثبات سريع.
3. `email_revenue_rescue` و`meeting_booking_sprint` → قيمة عالية بمسودات.
4. `growth_os` → اشتراك بعد Pilot.
