"""
مسجل نقاط الأتمتة والوكلاء في Dealix — مرجع للمطورين (لا يُنفَّذ تلقائياً).

اربط أي مسار جديد هنا عند إضافة تدفق وكيل أو Celery.
"""

from __future__ import annotations

# مسار HTTP / خدمة → وصف مختصر
AUTOMATION_SURFACE: dict[str, str] = {
    "app.services.agents.executor.AgentExecutor": "تنفيذ وكلاء عبر LLM + موجهات ai-agents/prompts",
    "app.workers.agent_tasks.run_ai_agent": "Celery — تشغيل وكيل في الخلفية",
    "app.workers.agent_tasks.process_agent_event": "Celery — سلسلة أحداث وكلاء",
    "app.workers.agent_tasks.snapshot_agent_framework_stack": "Celery — لقطة إصدارات إطارات الوكلاء",
    "app.ai.autogen.factory": "Microsoft AutoGen — عميل OpenAI/Groq + AssistantAgent",
    "app.flows.self_improvement_flow": "حلقة تحسين ذاتي (DurableTaskFlow / checkpoints)",
    "app.ai.evolution.signals": "إشارات تطور من لقطة طبقة الوكلاء (frameworks) — تُحقَن في lifespan",
    "app.openclaw.durable_flow": "مهام متينة مع نقاط استئناف",
    "app.services.model_router.ModelRouter": "توجيه مهام سريعة إلى Groq/OpenAI",
    "app.api.v1.agent_system": "واجهات نظام الوكلاء (LangGraph/compiler)",
    "app.api.v1.autonomous_foundation": "تأسيس مستقل + بوابة go-live",
    "app.brain.service.ingest_event": "Central Brain — أحداث، ذاكرة، تسجيل، قرار، توجيه وكلاء",
    "app.api.v1.brain": "REST Brain — /api/v1/brain/events, agents, skills, sessions",
    "app.workers.brain_tasks": "Celery — brain_dispatch_agent_chain, brain_daily_learning",
    "app.brain.skills.registry.execute_skill": "تنفيذ مهارة مسجّلة مع صلاحيات",
    "app.services.upgrade_director": "مدير ترقيات تلقائي — لقطات تبعيات، دورات بحث، قرار",
    "app.workers.upgrade_director_tasks.upgrade_director_hourly_tick": "Celery — لقطة ساعية محلية (اختياري)",
    "app.api.v1.seo_engine": "SEO Intelligence — /api/v1/seo-engine/*",
    "app.services.seo_engine.runner": "تشغيل تدقيق تقني، منافسين، فجوات، مسودات",
    "app.workers.seo_tasks.seo_scheduled_technical_round": "Celery — تدقيق تقني مجدول (DEALIX_SEO_SCHEDULE_ENABLED)",
    "app.api.v1.lead_engine": "محرك الإيراد — ICP، تسجيل، توجيه، تعلم",
    "app.services.lead_engine.orchestrator": "إعادة حساب نقاط المسار وربط المسرحيات",
    "app.workers.lead_engine_tasks.lead_engine_daily_rescore": "Celery — إعادة تقييم يومية (DEALIX_LEAD_ENGINE_SCHEDULE_ENABLED)",
}
