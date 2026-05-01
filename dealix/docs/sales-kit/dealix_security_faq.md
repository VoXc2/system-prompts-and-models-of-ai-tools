# 🛡️ Dealix — Security & Compliance FAQ

**للإرسال عند طلب فريق IT/Security من العميل**
**مُحدّث:** أبريل 2026

---

## 📋 ملخص الأمان في Dealix

| المجال | الحالة |
|--------|---------|
| Encryption at rest | AES-256 |
| Encryption in transit | TLS 1.3 |
| Hosting | AWS Frankfurt (eu-central-1) |
| SOC 2 | Type I ✅ / Type II Q4 2026 |
| ISO 27001 | في التقدم (Q1 2027) |
| PDPL (Saudi) | Compliant |
| GDPR | Compliant |
| Data residency | EU / KSA (عند الطلب) |
| Penetration testing | Annual (Q4) |
| Bug bounty | Hacker One — private program |

---

## 🔐 الأسئلة الشائعة

### 1. أين تُستضاف بيانات عملائي؟
**الجواب:**
Dealix مستضاف على AWS في منطقة Frankfurt (eu-central-1) افتراضياً. عملاء Enterprise يمكنهم طلب data residency في السعودية (AWS me-south-1) بتكلفة إضافية.

### 2. من يستطيع الوصول لبيانات شركتي؟
**الجواب:**
- 3 مهندسين فقط من Dealix (founders + lead engineer) لديهم production access
- كل وصول مُسجّل عبر AWS CloudTrail
- لا أحد يستطيع قراءة محادثات العملاء بدون ticket صريح من العميل
- لا نستخدم بيانات العميل لتدريب نماذج خارجية أو داخلية

### 3. كيف تُشفّر بياناتي؟
**الجواب:**
- **At rest:** AES-256 (AWS KMS-managed keys)
- **In transit:** TLS 1.3 مع certificate pinning
- **Backups:** مُشفّرة بـ AES-256 + stored cross-region
- **Database:** PostgreSQL encryption on + column-level encryption للـ PII

### 4. ما هي سياسة الاحتفاظ بالبيانات؟
**الجواب:**
- **Lead data:** يُحفظ ما دام الاشتراك فعّال
- **عند الإلغاء:** 30 يوم grace period ثم حذف كامل خلال 7 أيام
- **Logs:** 90 يوم ثم حذف تلقائي
- **حق النسيان:** حذف فوري عند طلب العميل (خلال 72 ساعة)

### 5. هل تتوافقون مع PDPL السعودي؟
**الجواب:** نعم.
- Legal basis للـ processing: consent + legitimate interest
- Data Subject Rights (DSR): export + deletion خلال 30 يوم
- DPO (Data Protection Officer) مُعيّن (sami.assiri11@gmail.com)
- نشارك DPA (Data Processing Agreement) كامل عند التوقيع

### 6. هل تتوافقون مع GDPR؟
**الجواب:** نعم.
- Privacy by design principles مُطبّقة
- DPIA (Data Protection Impact Assessment) مُتاح للعملاء Enterprise
- Data Transfer Mechanisms: Standard Contractual Clauses (SCCs)
- EU representative: [عند الحاجة]

### 7. هل عندكم SOC 2 report؟
**الجواب:**
- **SOC 2 Type I:** ✅ مُكتمل (ديسمبر 2025)
- **SOC 2 Type II:** في التقدم (متوقع Q4 2026)
- نشارك SOC 2 Type I report تحت NDA

### 8. كيف تتعاملون مع security incidents؟
**الجواب:**
- **Detection:** 24/7 monitoring عبر Sentry + Datadog
- **Response:** SLA للـ critical incidents = ساعة واحدة
- **Communication:** نُبلّغ العملاء المتأثرين خلال 24 ساعة
- **Post-mortem:** مُشاركة بعد كل major incident
- **Breach notification:** خلال 72 ساعة حسب GDPR/PDPL

### 9. هل تستخدمون third-party services؟
**الجواب:** نعم، محدودة ومُدقّقة:
- **LLM Provider:** Anthropic Claude (SOC 2 Type II, HIPAA-ready)
- **Hosting:** AWS (SOC 2 Type II, ISO 27001, PCI DSS)
- **Analytics:** PostHog (self-hosted) — لا third-party tracking
- **Email:** SendGrid (SOC 2)
- **Payments:** Moyasar (PCI DSS Level 1)

كل sub-processor مُدقّق و DPA موقّع معهم.

### 10. ما هي سياسة الـ passwords/authentication؟
**الجواب:**
- Hashing: bcrypt + pepper
- Minimum length: 12 characters
- MFA: اختياري الآن، إجباري Q3 2026
- Session timeout: 24 ساعة (قابل للتخصيص)
- API keys: rotatable، with IP allowlist support

### 11. هل تُجرون penetration tests؟
**الجواب:** نعم.
- **Annual:** pen test خارجي مستقل (Q4 كل سنة)
- **Quarterly:** vulnerability scanning (Trivy, Snyk)
- **Continuous:** dependency scanning (Dependabot)
- **Bug bounty:** private program على HackerOne — مُتاح للباحثين عند الطلب

### 12. كيف تتعاملون مع PII (معلومات شخصية)?
**الجواب:**
- **Identification:** كل PII فيلد marked في schema
- **Encryption:** column-level encryption للـ email, phone, name
- **Access:** محدود بالـ need-to-know
- **Logging:** PII never in logs (redaction تلقائي)
- **Export:** عميل يقدر يصدّر كل PII بصيغة JSON/CSV أي وقت

### 13. هل عندكم data breach insurance؟
**الجواب:**
- **Cyber liability:** $1M coverage
- **Errors & Omissions:** $500K
- **Product liability:** $500K
- Policy details مشاركة مع enterprise customers تحت NDA

### 14. كيف ننهي العقد ونسحب بياناتنا؟
**الجواب:**
- **Data export:** CSV + JSON للـ full dataset (خلال 48 ساعة من الطلب)
- **Deletion:** كامل خلال 7 أيام من تأكيد الإلغاء
- **Certification of deletion:** نرسل email رسمي بتأكيد الحذف
- **Backups:** rolling 30-day backups تُحذف تلقائياً بعد deletion

### 15. ما هي خطة business continuity عندكم؟
**الجواب:**
- **RTO (Recovery Time Objective):** 4 ساعات
- **RPO (Recovery Point Objective):** 1 ساعة (max data loss)
- **Backups:** automated hourly، cross-region replication
- **Disaster recovery test:** quarterly
- **Failover:** automatic إلى backup region خلال 10 دقائق

### 16. هل فريقكم يمر بـ background checks؟
**الجواب:**
- كل موظف يوقّع NDA + IP assignment
- Background checks للـ roles اللي تلمس production
- Security training إجباري annually
- عدد الفريق حالياً: 3 (سيزداد)

### 17. هل تشاركون بيانات مع الحكومة؟
**الجواب:**
- **موقفنا:** لا نشارك بيانات إلا بأمر قضائي رسمي
- **Transparency:** نُشعر العميل بأي طلب (إلا منعه القانون)
- **Canary warrant:** نُنشر في تقرير سنوي عدد الطلبات المُتلقّاة
- **Data residency:** عملاء Enterprise لديهم خيار hosting في السعودية لتبسيط الامتثال

### 18. كيف تُحدّثون الـ security ونماذج AI؟
**الجواب:**
- **Patches:** critical patches خلال 48 ساعة
- **Major updates:** monthly release cycle
- **AI model updates:** staged rollout مع rollback قدرة
- **Testing:** كل update يمر بـ regression + security tests
- **Customer notification:** 14 يوم قبل أي breaking change

### 19. هل عندكم تأمين privacy للعملاء الخليجيين تحديداً؟
**الجواب:** نعم، Dealix مبني للسوق الخليجي:
- Data residency option في السعودية (AWS me-south-1)
- Arabic-first privacy policy
- Customer support بالعربية (founders سعوديون)
- Integration مع Saudi infrastructure (Nafath, Absher, Moyasar)

### 20. ماذا يحدث إذا Dealix أغلق أبوابه؟
**الجواب:**
- **Escrow code:** لعملاء Enterprise — كود المصدر مُودع مع third-party
- **Data export guarantee:** 90 يوم notice period مع full data export
- **Continuity plan:** Dealix financial health shared quarterly مع enterprise accounts

---

## 📄 مستندات مُتاحة للطلب

| المستند | متاح للـ | طريقة الطلب |
|---------|----------|-------------|
| SOC 2 Type I Report | Enterprise | email + NDA |
| Penetration Test Report | Enterprise | email + NDA |
| DPA (Data Processing Agreement) | كل العملاء | توقيع مع العقد |
| Security Whitepaper | public | download |
| Privacy Policy | public | dealix.ai/privacy |
| Terms of Service | public | dealix.ai/terms |
| Sub-processors List | public | dealix.ai/subprocessors |

---

## 🔒 أسئلة خاصة بـ Vendor Risk Management

إذا فريق Security عندكم يستخدم:

### CAIQ (Cloud Security Alliance)
Dealix أكمل CAIQ v4.0.3 — متاح عبر STAR registry أو email.

### SIG (Shared Assessments)
SIG Lite مُتاح مكتمل.

### Custom questionnaire
نُكمل أي security questionnaire مخصّص خلال 5 أيام عمل.

---

## 📞 تواصل Security

**Security reports:** security@dealix.ai (coming — حالياً sami.assiri11@gmail.com)
**Bug bounty:** hackerone.com/dealix (private — request invite)
**Abuse/compliance:** legal@dealix.ai
**DPO contact:** sami.assiri11@gmail.com

**Response time للـ security reports:**
- Critical: خلال ساعة
- High: خلال 4 ساعات
- Medium: خلال 24 ساعة
- Low: خلال 72 ساعة

---

*هذا المستند يُحدّث ربع سنوياً. آخر تحديث: أبريل 2026.*
*PGP key متاح عند الطلب للـ security-sensitive communications.*
