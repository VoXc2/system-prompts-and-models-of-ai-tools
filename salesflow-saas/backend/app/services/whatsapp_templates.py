"""
Dealix WhatsApp Template Library - Pre-built Arabic message templates.
Provides templates for common sales scenarios across the full customer
lifecycle: lead acquisition, appointments, payments, delivery, and retention.
"""
from typing import Optional


class WhatsAppTemplateLibrary:
    """
    A library of WhatsApp Business API message templates in Arabic.

    Each template uses numbered placeholders ({{1}}, {{2}}, etc.) that map
    to positional values supplied at render time. Templates are organized
    by category following the WhatsApp Business Platform conventions:
    marketing, utility, and authentication.
    """

    TEMPLATES: dict[str, dict] = {
        "welcome_new_lead": {
            "name": "welcome_new_lead",
            "name_ar": "ترحيب عميل جديد",
            "category": "marketing",
            "language": "ar",
            "body": (
                "أهلاً وسهلاً {{1}} 👋\n"
                "شكراً لاهتمامك بخدماتنا في {{2}}.\n"
                "أنا {{3}}، وسأكون مسؤول حسابك الشخصي.\n"
                "كيف أقدر أساعدك اليوم؟"
            ),
            "example_values": ["أحمد", "ديليكس", "سارة"],
            "description_ar": "يُرسل تلقائياً عند تسجيل عميل محتمل جديد في النظام للترحيب به وتعريفه بمسؤول حسابه.",
        },
        "appointment_reminder": {
            "name": "appointment_reminder",
            "name_ar": "تذكير موعد",
            "category": "utility",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "نذكّرك بموعدك القادم يوم {{2}} الساعة {{3}}.\n"
                "📍 الموقع: {{4}}\n"
                "إذا احتجت تغيير الموعد، تواصل معنا قبل ٢٤ ساعة."
            ),
            "example_values": ["خالد", "الأحد ١٥ يناير", "١٠:٠٠ صباحاً", "المكتب الرئيسي - الرياض"],
            "description_ar": "يُرسل قبل الموعد المحدد بيوم واحد لتذكير العميل بتفاصيل الموعد.",
        },
        "appointment_confirmation": {
            "name": "appointment_confirmation",
            "name_ar": "تأكيد موعد",
            "category": "utility",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "تم تأكيد موعدك بنجاح ✅\n"
                "📅 التاريخ: {{2}}\n"
                "🕐 الوقت: {{3}}\n"
                "📍 الموقع: {{4}}\n"
                "نتطلع لرؤيتك!"
            ),
            "example_values": ["فاطمة", "٢٠ فبراير ٢٠٢٥", "٢:٠٠ مساءً", "فرع جدة"],
            "description_ar": "يُرسل فور حجز العميل لموعد جديد أو عند تأكيد موعد معلّق.",
        },
        "proposal_followup": {
            "name": "proposal_followup",
            "name_ar": "متابعة عرض سعر",
            "category": "marketing",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "أتمنى أنك بخير 🙏\n"
                "أحببت أتابع معك بخصوص عرض السعر رقم {{2}} اللي أرسلناه لك بتاريخ {{3}}.\n"
                "العرض يشمل {{4}} وصالح حتى {{5}}.\n"
                "هل عندك أي استفسار أو تحتاج تعديل على العرض؟"
            ),
            "example_values": [
                "عبدالله",
                "QT-2025-0042",
                "١٠ يناير",
                "باقة النمو المتقدمة",
                "٣٠ يناير",
            ],
            "description_ar": "يُرسل بعد مرور عدة أيام من إرسال عرض سعر لم يُرد عليه لمتابعة العميل.",
        },
        "payment_reminder": {
            "name": "payment_reminder",
            "name_ar": "تذكير دفعة",
            "category": "utility",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "نود تذكيرك بأن الدفعة المستحقة بمبلغ {{2}} ريال بتاريخ {{3}} لم تُسدد بعد.\n"
                "رقم الفاتورة: {{4}}\n"
                "يرجى السداد في أقرب وقت لتجنب أي رسوم إضافية.\n"
                "لأي استفسار، نحن هنا لمساعدتك."
            ),
            "example_values": ["محمد", "٥,٠٠٠", "١ فبراير ٢٠٢٥", "INV-2025-0078"],
            "description_ar": "يُرسل عند اقتراب أو تجاوز تاريخ استحقاق دفعة لتذكير العميل بالسداد.",
        },
        "payment_confirmation": {
            "name": "payment_confirmation",
            "name_ar": "تأكيد دفعة",
            "category": "utility",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "تم استلام دفعتك بنجاح ✅\n"
                "💰 المبلغ: {{2}} ريال\n"
                "🧾 رقم الفاتورة: {{3}}\n"
                "📅 تاريخ السداد: {{4}}\n"
                "شكراً لك! سيتم إرسال الإيصال على بريدك الإلكتروني."
            ),
            "example_values": ["نورة", "٣,٥٠٠", "INV-2025-0065", "١٥ يناير ٢٠٢٥"],
            "description_ar": "يُرسل فور تأكيد استلام دفعة من العميل.",
        },
        "delivery_update": {
            "name": "delivery_update",
            "name_ar": "تحديث توصيل",
            "category": "utility",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "تحديث على طلبك رقم {{2}} 📦\n"
                "الحالة: {{3}}\n"
                "الوصول المتوقع: {{4}}\n"
                "لتتبع شحنتك: {{5}}"
            ),
            "example_values": [
                "سعد",
                "ORD-2025-1234",
                "في الطريق إليك",
                "غداً بين ٩ ص - ١٢ م",
                "https://track.example.com/1234",
            ],
            "description_ar": "يُرسل عند تحديث حالة التوصيل أو الشحن لإبقاء العميل على اطلاع.",
        },
        "feedback_request": {
            "name": "feedback_request",
            "name_ar": "طلب تقييم",
            "category": "marketing",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "نتمنى أن تجربتك مع {{2}} كانت ممتازة! ⭐\n"
                "رأيك يهمنا جداً ويساعدنا نتحسن.\n"
                "ممكن تعطينا تقييمك من خلال الرابط التالي؟\n"
                "{{3}}\n"
                "شكراً لوقتك 🙏"
            ),
            "example_values": [
                "هند",
                "خدمة الاستشارات",
                "https://feedback.example.com/r/abc",
            ],
            "description_ar": "يُرسل بعد اكتمال خدمة أو تسليم منتج لجمع تقييم العميل.",
        },
        "seasonal_offer": {
            "name": "seasonal_offer",
            "name_ar": "عرض موسمي",
            "category": "marketing",
            "language": "ar",
            "body": (
                "مرحباً {{1}} 🎉\n"
                "بمناسبة {{2}}، نقدم لك عرض خاص!\n"
                "{{3}}\n"
                "🔥 خصم {{4}}٪ على {{5}}\n"
                "العرض ساري حتى {{6}}.\n"
                "لا تفوّت الفرصة!"
            ),
            "example_values": [
                "ريم",
                "اليوم الوطني",
                "احتفل معنا بأقوى العروض",
                "٣٠",
                "جميع الباقات",
                "٣٠ سبتمبر",
            ],
            "description_ar": "يُرسل خلال المواسم والمناسبات للترويج لعروض خاصة.",
        },
        "reactivation": {
            "name": "reactivation",
            "name_ar": "إعادة تنشيط",
            "category": "marketing",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "افتقدناك! 💙\n"
                "لاحظنا أنك ما تواصلت معنا من فترة.\n"
                "حابين نطمّن عليك ونخبرك إن عندنا جديد يهمك:\n"
                "{{2}}\n"
                "كهديّة ترحيبية، حصلت على {{3}}.\n"
                "نتطلع نشوفك مرة ثانية!"
            ),
            "example_values": [
                "ياسر",
                "أطلقنا خدمة التحليلات الذكية الجديدة",
                "خصم ٢٠٪ على أول طلب",
            ],
            "description_ar": "يُرسل للعملاء غير النشطين لفترة طويلة لإعادة تفاعلهم مع الخدمة.",
        },
        "referral_request": {
            "name": "referral_request",
            "name_ar": "طلب إحالة",
            "category": "marketing",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "سعداء إنك من عملائنا المميزين! 🌟\n"
                "إذا عندك أحد يستفيد من خدماتنا، شاركه رابط الإحالة الخاص فيك:\n"
                "{{2}}\n"
                "مع كل إحالة ناجحة، تحصل على {{3}}.\n"
                "شكراً لثقتك فينا!"
            ),
            "example_values": [
                "منى",
                "https://refer.example.com/u/mona",
                "رصيد ٢٠٠ ريال في حسابك",
            ],
            "description_ar": "يُرسل للعملاء الراضين لتشجيعهم على إحالة عملاء جدد مقابل مكافآت.",
        },
        "service_update": {
            "name": "service_update",
            "name_ar": "تحديث خدمة",
            "category": "utility",
            "language": "ar",
            "body": (
                "مرحباً {{1}}،\n"
                "نود إعلامك بتحديث مهم على {{2}}:\n"
                "{{3}}\n"
                "📅 يبدأ التطبيق: {{4}}\n"
                "للمزيد من التفاصيل: {{5}}\n"
                "لأي استفسار، لا تتردد بالتواصل معنا."
            ),
            "example_values": [
                "عمر",
                "باقة الأعمال",
                "تمت إضافة ميزة التقارير التفاعلية مجاناً",
                "١ مارس ٢٠٢٥",
                "https://help.example.com/updates",
            ],
            "description_ar": "يُرسل عند وجود تحديث أو تغيير على خدمة يستخدمها العميل.",
        },
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def get_template(cls, name: str) -> dict:
        """Return a single template by its English key name.

        Args:
            name: The template key (e.g. ``"welcome_new_lead"``).

        Returns:
            A copy of the template dict.

        Raises:
            KeyError: If the template name does not exist.
        """
        if name not in cls.TEMPLATES:
            available = ", ".join(sorted(cls.TEMPLATES.keys()))
            raise KeyError(
                f"Template '{name}' not found. Available templates: {available}"
            )
        return dict(cls.TEMPLATES[name])

    @classmethod
    def render_template(cls, name: str, values: list) -> str:
        """Render a template by replacing placeholders with the given values.

        Placeholders follow the WhatsApp convention: ``{{1}}``, ``{{2}}``, etc.

        Args:
            name: The template key.
            values: Positional values that map to ``{{1}}``, ``{{2}}``, ...

        Returns:
            The rendered message body as a string.

        Raises:
            KeyError: If the template name does not exist.
            ValueError: If the number of values does not match the number
                of placeholders in the template body.
        """
        template = cls.get_template(name)
        body: str = template["body"]

        expected_count = body.count("{{")
        if len(values) != expected_count:
            raise ValueError(
                f"Template '{name}' expects {expected_count} values, "
                f"but {len(values)} were provided."
            )

        rendered = body
        for i, value in enumerate(values, start=1):
            rendered = rendered.replace(f"{{{{{i}}}}}", str(value))
        return rendered

    @classmethod
    def get_templates_by_category(cls, category: str) -> list[dict]:
        """Return all templates that belong to the given category.

        Args:
            category: One of ``"marketing"``, ``"utility"``, or
                ``"authentication"``.

        Returns:
            A list of template dicts matching the category.
        """
        return [
            dict(t)
            for t in cls.TEMPLATES.values()
            if t["category"] == category
        ]

    @classmethod
    def list_all(cls) -> list[dict]:
        """Return a list of all available templates.

        Returns:
            A list of template dicts, one per registered template.
        """
        return [dict(t) for t in cls.TEMPLATES.values()]
