"""Three-door UX map + vertical hints for Service Tower."""

from __future__ import annotations

from typing import Any


def build_vertical_service_map() -> dict[str, Any]:
    return {
        "doors": [
            {
                "door_id": "more_customers",
                "title_ar": "أريد عملاء أكثر",
                "service_ids": [
                    "first_10_opportunities",
                    "growth_os",
                    "linkedin_lead_gen_setup",
                    "meeting_booking_sprint",
                ],
            },
            {
                "door_id": "use_my_data",
                "title_ar": "عندي بيانات وأريد أستفيد منها",
                "service_ids": [
                    "list_intelligence",
                    "email_revenue_rescue",
                    "whatsapp_compliance_setup",
                    "free_growth_diagnostic",
                ],
            },
            {
                "door_id": "scale_strategy",
                "title_ar": "أريد توسع وشراكات",
                "service_ids": [
                    "partner_sprint",
                    "agency_partner_program",
                    "executive_growth_brief",
                    "self_growth_operator",
                ],
            },
        ],
        "verticals": [
            {"id": "agency", "label_ar": "وكالات", "priority_services": ["agency_partner_program", "first_10_opportunities"]},
            {"id": "training", "label_ar": "تدريب واستشارات", "priority_services": ["first_10_opportunities", "meeting_booking_sprint"]},
            {"id": "saas", "label_ar": "SaaS صغير", "priority_services": ["list_intelligence", "growth_os"]},
            {"id": "local", "label_ar": "محلي (عيادات/متاجر)", "priority_services": ["local_growth_os", "whatsapp_compliance_setup"]},
        ],
        "demo": True,
    }
