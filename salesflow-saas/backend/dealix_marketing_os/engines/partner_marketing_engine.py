"""Partner Marketing Engine — generates partner assets and campaigns."""

def generate_partner_assets() -> dict:
    return {
        "partner_one_pager": {
            "headline_ar": "اربح من أول اشتراك مدفوع مؤهل يأتي عن طريقك",
            "body_ar": "ديليكس مصمم عشان المسوقين والوكالات يقدرون يستفيدون من شبكتهم. إذا أحلت عميل مؤهل واشترك، تصبح مؤهلاً لعمولة حسب الشروط.",
            "earning_paths": [
                {"type": "referral", "desc": "عرّفنا على شركة. لك نسبة بعد الدفع المؤكد."},
                {"type": "reseller", "desc": "بيع Dealix ضمن خدماتك. احتفظ بهامشك."},
                {"type": "service_exchange", "desc": "ساعد بالمحتوى/الإحالات. نعطيك pilot مجاني."},
            ],
            "safe_wording": True,
            "no_guaranteed_profit": True,
            "payout_after_verified_payment": True,
        },
        "agency_pitch": "أضف خدمة متابعة leads لعملائك — 20% لك من كل عميل",
        "referral_pitch": "لو تعرف شركة تضيع leads، عرّفنا عليها ولك نسبة",
        "approval_required": True,
    }
