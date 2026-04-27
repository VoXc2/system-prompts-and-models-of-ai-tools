"""Landing Page Engine — generates page plans for conversion."""

def generate_landing_plans() -> dict:
    return {
        "pages": [
            {"slug": "/", "type": "homepage", "hero": "ديليكس يحوّل الاستفسارات إلى متابعة وحجز وإيراد", "cta": "احجز ديمو"},
            {"slug": "/marketers", "type": "partner", "hero": "اربح من أول اشتراك مدفوع مؤهل", "cta": "كن شريك Dealix"},
            {"slug": "/partners", "type": "agency", "hero": "أضف خدمة متابعة leads لعملائك", "cta": "احجز مكالمة شراكة"},
            {"slug": "/pricing", "type": "offers", "hero": "باقات بسيطة وواضحة", "cta": "ابدأ Pilot"},
            {"slug": "/use-cases", "type": "sectors", "hero": "كل قطاع عنده leads تضيع", "cta": "احجز ديمو"},
            {"slug": "/trust", "type": "safety", "hero": "الأمان والثقة", "cta": "احجز ديمو آمن"},
        ],
        "sector_pages": [
            {"sector": "agencies", "pain": "عملاؤكم يخسرون leads بعد الإعلان"},
            {"sector": "real_estate", "pain": "60% من استفسارات الأسعار تضيع"},
            {"sector": "clinics", "pain": "حجوزات ضائعة من واتساب"},
            {"sector": "ecommerce", "pain": "محادثات ما تتحول لطلبات"},
        ],
    }
