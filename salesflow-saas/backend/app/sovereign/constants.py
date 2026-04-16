"""Sovereign OS — required surfaces, program lock defaults, and Saudi compliance references."""

from __future__ import annotations

from datetime import datetime, timezone

from app.sovereign.schemas import (
    ActionClass,
    AgentRole,
    ApprovalClass,
    BusinessTrack,
    PlaneType,
    ProgramLock,
    ReversibilityClass,
)

REQUIRED_SURFACES: list[tuple[str, str]] = [
    ("Decision Sovereignty Console", "وحدة سيادة القرار"),
    ("Executive Briefing Surface", "سطح الإحاطة التنفيذية"),
    ("Investment Committee Workspace", "مساحة عمل لجنة الاستثمار"),
    ("Risk & Compliance Cockpit", "لوحة المخاطر والامتثال"),
    ("Revenue Acceleration Studio", "استوديو تسارع الإيرادات"),
    ("Pipeline Truth Surface", "سطح دقة مسار المبيعات"),
    ("Partner Ecosystem Graph", "مخطط منظومة الشركاء"),
    ("Alliance Governance Desk", "مكتب حوكمة التحالفات"),
    ("M&A Deal Room", "غرفة صفقات الاندماج والاستحواذ"),
    ("Corporate Development Intelligence", "ذكاء التطوير المؤسسي"),
    ("Greenfield Expansion Map", "خريطة التوسع الجديد"),
    ("Market Entry Playbook", "دليل دخول السوق"),
    ("PMI Integration Tracker", "متتبع تكامل ما بعد الدمج"),
    ("PMO Portfolio Command", "قيادة محفظة المشاريع"),
    ("Board Papers & Resolutions", "أوراق وقرارات مجلس الإدارة"),
    ("Stakeholder Trust Ledger", "سجل ثقة أصحاب المصلحة"),
    ("Enterprise Data Fabric", "نسيج بيانات المؤسسة"),
    ("Operating Rhythm Control Tower", "برج ضبط الإيقاع التشغيلي"),
]

SAUDI_COMPLIANCE_FRAMEWORKS: tuple[str, ...] = (
    "PDPL",
    "NCA_ECC_2024",
    "NIST_AI_RMF",
    "OWASP_LLM_TOP_10",
)

DEFAULT_PROGRAM_LOCK: ProgramLock = ProgramLock(
    lock_id="sovereign-program-lock-default-v1",
    planes=list(PlaneType),
    tracks=list(BusinessTrack),
    agent_roles=list(AgentRole),
    action_classes=list(ActionClass),
    approval_classes=list(ApprovalClass),
    reversibility_classes=list(ReversibilityClass),
    sensitivity_model={
        "default_level": "INTERNAL",
        "arabic_customer_content": "CONFIDENTIAL",
        "board_materials": "RESTRICTED",
        "cross_border_transfer": "APPROVAL_REQUIRED",
    },
    locked_at=datetime.now(timezone.utc),
    locked_by="system@dealix.sovereign",
)

SOVEREIGNTY_READINESS_CRITERIA: list[str] = [
    "Program lock is defined, versioned, and enforced across all five planes (تم تعريف قفل البرنامج وإصداره وفرضه عبر جميع المستويات الخمسة).",
    "Every outbound connector has a signed ConnectorContract with audit mapping and rollback notes (لكل موصل صادر عقد موصل موقّع مع تعيين التدقيق وملاحظات التراجع).",
    "Evidence packs carry bilingual titles and summaries with provenance for all recommendations (تحمل حزم الأدلة عناوين وملخصات ثنائية اللغة مع مصدر لجميع التوصيات).",
    "Action class, approval class, reversibility, and sensitivity are evaluated before execution (يتم تقييم فئة الإجراء والموافقة والعكسية والحساسية قبل التنفيذ).",
    "Contradiction detection is wired for agent tool calls with resolution workflows (تم ربط كشف التناقض لمكالمات أدوات الوكيل مع مسارات الحل).",
    "Model routing respects Arabic quality requirements and cost/latency ceilings (يحترم توجيه النموذج متطلبات جودة العربية وحدود التكلفة/زمن الاستجابة).",
    "Saudi compliance frameworks (PDPL, NCA ECC, NIST AI RMF, OWASP LLM Top 10) are mapped to controls and tests (تم ربط أطر الامتسال السعودية بالضوابط والاختبارات).",
    "Eighteen sovereign surfaces are provisioned, monitored, and owner-assigned per track (تم توفير ومراقبة وتعيين مالك للأسطح السيادية الثمانية عشر لكل مسار).",
]
