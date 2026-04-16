"""Sovereign OS — five planes (decision, execution, trust, data, operating)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException, Response, status
from pydantic import BaseModel, BeforeValidator, Field

from app.api.v1.sovereign.tenant import TenantIdQuery
from app.sovereign.data_plane import DataPlane
from app.sovereign.decision_plane import DecisionPlane
from app.sovereign.execution_plane import ExecutionPlane
from app.sovereign.execution_plane.engine import WorkflowState
from app.sovereign.operating_plane import OperatingPlane
from app.sovereign.schemas import (
    ConnectorHealthStatus,
    ContradictionRecord,
    DataQualityResult,
    DeploymentStatus,
    EventValidationResult,
    EvidencePack,
    ExtractionResult,
    ProvenanceResult,
    RecommendationPayload,
    ReleaseGateResult,
    RulesetEnforcementResult,
    SemanticQueryResult,
)
from app.sovereign.decision_plane_schemas import (
    DecisionSignal,
    ForecastResult,
    RankedAction,
    ScenarioAnalysisReport,
    SignalKind,
    StructuredMemo,
    TriagedSignal,
)
from app.sovereign.trust_plane import TrustPlane
from app.sovereign.trust_plane.engine import (
    AIGovernanceResult,
    AuditEntryPayload,
    AuthorizationResult,
    PolicyDecision,
    RoutedApproval,
    ToolVerificationResult,
)

decision_plane = DecisionPlane()
execution_plane = ExecutionPlane()
trust_plane = TrustPlane()
data_plane = DataPlane()
operating_plane = OperatingPlane()

decision_router = APIRouter(prefix="/decision", tags=["Sovereign — Decision"])
execution_router = APIRouter(prefix="/execution", tags=["Sovereign — Execution"])
trust_router = APIRouter(prefix="/trust", tags=["Sovereign — Trust"])
data_router = APIRouter(prefix="/data", tags=["Sovereign — Data"])
operating_router = APIRouter(prefix="/operating", tags=["Sovereign — Operating"])


# --- Decision plane bodies ---


class SignalDetectBody(BaseModel):
    track: str = Field(default="REVENUE", description="Business track context")
    raw_data: dict[str, Any] = Field(default_factory=dict)


def _coerce_signal_dicts(v: Any) -> list[DecisionSignal]:
    if not isinstance(v, list):
        return []
    out: list[DecisionSignal] = []
    for item in v:
        if isinstance(item, DecisionSignal):
            out.append(item)
            continue
        if not isinstance(item, dict):
            continue
        d = dict(item)
        kind_raw = str(d.get("kind", SignalKind.OPPORTUNITY)).lower()
        try:
            kind = SignalKind(kind_raw)
        except ValueError:
            kind = SignalKind.OPPORTUNITY
        sid = str(d.get("signal_id", "")) or "signal_stub"
        track = str(d.get("track", "REVENUE"))
        strength = float(d.get("strength", d.get("urgency", 0.5)))
        strength = max(0.0, min(1.0, strength if strength <= 1.0 else strength / 100.0))
        out.append(
            DecisionSignal(
                signal_id=sid,
                kind=kind,
                track=track,
                strength=strength,
                payload=dict(d.get("payload", {})),
                description_en=str(d.get("description_en", "Inferred signal from client payload.")),
                description_ar=str(d.get("description_ar", "إشارة مستنتجة من الطلب.")),
            ),
        )
    return out


class TriageBody(BaseModel):
    signals: Annotated[list[DecisionSignal], BeforeValidator(_coerce_signal_dicts)] = Field(default_factory=list)


class ScenarioBody(BaseModel):
    context: dict[str, Any] = Field(default_factory=dict)
    scenarios: list[dict[str, Any]] = Field(default_factory=list)


class MemoBody(BaseModel):
    track: str = "REVENUE"
    context: dict[str, Any] = Field(default_factory=dict)
    language: str = "ar"


def _normalize_forecast_history(v: Any) -> list[dict[str, Any]]:
    if not isinstance(v, list):
        return []
    out: list[dict[str, Any]] = []
    for i, row in enumerate(v):
        if isinstance(row, dict):
            out.append(dict(row))
            continue
        if isinstance(row, (int, float)):
            out.append({"period": i, "value": float(row)})
            continue
        if isinstance(row, str):
            try:
                out.append({"period": i, "value": float(row)})
            except ValueError:
                out.append({"period": i, "value": 0.0})
    return out


class ForecastBody(BaseModel):
    track: str = "REVENUE"
    historical_data: Annotated[list[dict[str, Any]], BeforeValidator(_normalize_forecast_history)] = Field(
        default_factory=list,
    )
    horizon_days: int = Field(default=14, ge=1, le=365)


class RecommendBody(BaseModel):
    track: str = "REVENUE"
    context: dict[str, Any] = Field(default_factory=dict)


class NextActionBody(BaseModel):
    track: str = "REVENUE"
    current_state: dict[str, Any] = Field(default_factory=dict)


class EvidencePackBody(BaseModel):
    track: str = "REVENUE"
    items: list[dict[str, Any]] = Field(default_factory=list)


@decision_router.post(
    "/signals/detect",
    response_model=list[DecisionSignal],
    summary="Detect decision signals",
)
async def decision_signals_detect(
    tenant_id: TenantIdQuery,
    body: SignalDetectBody = Body(default_factory=SignalDetectBody),
) -> list[DecisionSignal]:
    try:
        return await decision_plane.detect_signals(tenant_id, body.track, body.raw_data)
    except Exception as exc:  # noqa: BLE001 — surface stub/plane errors consistently
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Signal detection failed.",
                "message_ar": "فشل اكتشاف الإشارات.",
                "error": str(exc),
            },
        ) from exc


@decision_router.post(
    "/triage",
    response_model=list[TriagedSignal],
    summary="Triage signals",
)
async def decision_triage(
    tenant_id: TenantIdQuery,
    body: TriageBody = Body(default_factory=TriageBody),
) -> list[TriagedSignal]:
    if not body.signals:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message_en": "At least one signal is required for triage.",
                "message_ar": "مطلوب إشارة واحدة على الأقل للفرز.",
            },
        )
    try:
        return await decision_plane.triage(tenant_id, body.signals)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Triage failed.",
                "message_ar": "فشل الفرز.",
                "error": str(exc),
            },
        ) from exc


@decision_router.post(
    "/scenarios",
    response_model=ScenarioAnalysisReport,
    summary="Analyze scenarios",
)
async def decision_scenarios(
    tenant_id: TenantIdQuery,
    body: ScenarioBody = Body(default_factory=ScenarioBody),
) -> ScenarioAnalysisReport:
    try:
        return await decision_plane.analyze_scenarios(tenant_id, body.context, body.scenarios)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Scenario analysis failed.",
                "message_ar": "فشل تحليل السيناريوهات.",
                "error": str(exc),
            },
        ) from exc


@decision_router.post(
    "/memo",
    response_model=StructuredMemo,
    summary="Generate structured memo",
)
async def decision_memo(
    tenant_id: TenantIdQuery,
    body: MemoBody = Body(default_factory=MemoBody),
) -> StructuredMemo:
    try:
        return await decision_plane.generate_memo(tenant_id, body.track, body.context, body.language)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Memo generation failed.",
                "message_ar": "فشل إنشاء المذكرة.",
                "error": str(exc),
            },
        ) from exc


@decision_router.post(
    "/forecast",
    response_model=ForecastResult,
    summary="Forecast",
)
async def decision_forecast(
    tenant_id: TenantIdQuery,
    body: ForecastBody = Body(default_factory=ForecastBody),
) -> ForecastResult:
    try:
        return await decision_plane.forecast(
            tenant_id,
            body.track,
            body.historical_data,
            body.horizon_days,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Forecast failed.",
                "message_ar": "فشل التنبؤ.",
                "error": str(exc),
            },
        ) from exc


@decision_router.post(
    "/recommend",
    response_model=RecommendationPayload,
    summary="Get recommendation",
)
async def decision_recommend(
    tenant_id: TenantIdQuery,
    body: RecommendBody = Body(default_factory=RecommendBody),
) -> RecommendationPayload:
    try:
        return await decision_plane.recommend(tenant_id, body.track, body.context)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Recommendation failed.",
                "message_ar": "فشلت التوصية.",
                "error": str(exc),
            },
        ) from exc


@decision_router.post(
    "/next-action",
    response_model=list[RankedAction],
    summary="Next best actions",
)
async def decision_next_action(
    tenant_id: TenantIdQuery,
    body: NextActionBody = Body(default_factory=NextActionBody),
) -> list[RankedAction]:
    try:
        return await decision_plane.next_best_action(tenant_id, body.track, body.current_state)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Next-action ranking failed.",
                "message_ar": "فشل ترتيب الإجراء التالي.",
                "error": str(exc),
            },
        ) from exc


@decision_router.post(
    "/evidence-pack",
    response_model=EvidencePack,
    summary="Assemble evidence pack",
)
async def decision_evidence_pack(
    tenant_id: TenantIdQuery,
    body: EvidencePackBody = Body(default_factory=EvidencePackBody),
) -> EvidencePack:
    try:
        return await decision_plane.assemble_evidence_pack(tenant_id, body.track, body.items)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Evidence pack assembly failed.",
                "message_ar": "فشل تجميع حزمة الأدلة.",
                "error": str(exc),
            },
        ) from exc


# --- Execution plane ---


class WorkflowStartBody(BaseModel):
    workflow_type: str = Field(..., description="Temporal / durable workflow type name")
    payload: dict[str, Any] = Field(default_factory=dict)
    approval_class: str = "TEAM_LEAD"


class WorkflowReasonBody(BaseModel):
    reason: str = ""


class PauseApprovalBody(BaseModel):
    approval_class: str = "TEAM_LEAD"
    reason: str = "Awaiting human approval"


@execution_router.post(
    "/workflow/start",
    response_model=dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Start durable workflow",
)
async def execution_workflow_start(
    tenant_id: TenantIdQuery,
    body: WorkflowStartBody = Body(default_factory=WorkflowStartBody),
) -> dict[str, str]:
    try:
        workflow_id = await execution_plane.start_workflow(
            tenant_id,
            body.workflow_type,
            body.payload,
            body.approval_class,
        )
        return {
            "workflow_id": workflow_id,
            "message_en": "Workflow started.",
            "message_ar": "تم بدء سير العمل.",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Failed to start workflow.",
                "message_ar": "فشل بدء سير العمل.",
                "error": str(exc),
            },
        ) from exc


@execution_router.post(
    "/workflow/{workflow_id}/resume",
    response_model=dict[str, Any],
    summary="Resume workflow",
)
async def execution_workflow_resume(
    tenant_id: TenantIdQuery,
    workflow_id: str,
) -> dict[str, Any]:
    try:
        state = await execution_plane.resume_workflow(tenant_id, workflow_id)
        return {
            "workflow_id": workflow_id,
            "state": state.value if isinstance(state, WorkflowState) else str(state),
            "message_en": "Resume processed.",
            "message_ar": "تمت معالجة الاستئناف.",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Resume failed.",
                "message_ar": "فشل الاستئناف.",
                "error": str(exc),
            },
        ) from exc


@execution_router.post(
    "/workflow/{workflow_id}/compensate",
    response_model=dict[str, Any],
    summary="Compensate workflow",
)
async def execution_workflow_compensate(
    tenant_id: TenantIdQuery,
    workflow_id: str,
    body: WorkflowReasonBody = Body(default_factory=WorkflowReasonBody),
) -> dict[str, Any]:
    try:
        result = await execution_plane.compensate(tenant_id, workflow_id, body.reason)
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Compensation failed.",
                "message_ar": "فشل التعويض.",
                "error": str(exc),
            },
        ) from exc


@execution_router.get(
    "/workflow/{workflow_id}/status",
    response_model=dict[str, Any],
    summary="Workflow status",
)
async def execution_workflow_status(
    tenant_id: TenantIdQuery,
    workflow_id: str,
) -> dict[str, Any]:
    try:
        st = await execution_plane.get_workflow_status(tenant_id, workflow_id)
        return st.model_dump(mode="json")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Status lookup failed.",
                "message_ar": "فشل جلب الحالة.",
                "error": str(exc),
            },
        ) from exc


@execution_router.post(
    "/workflow/{workflow_id}/pause",
    response_model=dict[str, Any],
    summary="Pause for approval",
)
async def execution_workflow_pause(
    tenant_id: TenantIdQuery,
    workflow_id: str,
    body: PauseApprovalBody = Body(default_factory=PauseApprovalBody),
) -> dict[str, Any]:
    try:
        result = await execution_plane.pause_for_approval(
            tenant_id,
            workflow_id,
            body.approval_class,
            body.reason,
        )
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Pause for approval failed.",
                "message_ar": "فشل التوقف لانتظار الموافقة.",
                "error": str(exc),
            },
        ) from exc


# --- Trust plane ---


class PolicyEvaluateBody(BaseModel):
    action: str
    context: dict[str, Any] = Field(default_factory=dict)


class AuthorizationCheckBody(BaseModel):
    user_id: str
    resource: str
    action: str


class ApprovalRouteBody(BaseModel):
    request: dict[str, Any] = Field(default_factory=dict)
    approval_class: str = "TEAM_LEAD"


class ToolVerifyBody(BaseModel):
    agent_id: str
    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)


def _coerce_contradiction_side(v: Any, *, role: str) -> dict[str, Any]:
    if isinstance(v, dict):
        return dict(v)
    if isinstance(v, str):
        if role == "intended":
            return {"action": v}
        if role == "claimed":
            return {"action": v}
        return {"tool": v}
    return {}


class ContradictionDetectBody(BaseModel):
    intended: Annotated[dict[str, Any], BeforeValidator(lambda v: _coerce_contradiction_side(v, role="intended"))] = (
        Field(default_factory=dict)
    )
    claimed: Annotated[dict[str, Any], BeforeValidator(lambda v: _coerce_contradiction_side(v, role="claimed"))] = (
        Field(default_factory=dict)
    )
    actual: Annotated[dict[str, Any], BeforeValidator(lambda v: _coerce_contradiction_side(v, role="actual"))] = (
        Field(default_factory=dict)
    )


class AIGovernanceBody(BaseModel):
    model_id: str = "gpt-4o-mini"
    task_type: str = "default"


@trust_router.post(
    "/policy/evaluate",
    response_model=PolicyDecision,
    summary="Evaluate policy",
)
async def trust_policy_evaluate(
    tenant_id: TenantIdQuery,
    body: PolicyEvaluateBody = Body(...),
) -> PolicyDecision:
    try:
        return await trust_plane.evaluate_policy(tenant_id, body.action, body.context)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Policy evaluation failed.",
                "message_ar": "فشل تقييم السياسة.",
                "error": str(exc),
            },
        ) from exc


@trust_router.post(
    "/authorization/check",
    response_model=AuthorizationResult,
    summary="Check authorization",
)
async def trust_authorization_check(
    tenant_id: TenantIdQuery,
    body: AuthorizationCheckBody = Body(...),
) -> AuthorizationResult:
    try:
        return await trust_plane.check_authorization(
            tenant_id,
            body.user_id,
            body.resource,
            body.action,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Authorization check failed.",
                "message_ar": "فشل فحص التفويض.",
                "error": str(exc),
            },
        ) from exc


@trust_router.post(
    "/approval/route",
    response_model=RoutedApproval,
    summary="Route approval",
)
async def trust_approval_route(
    tenant_id: TenantIdQuery,
    body: ApprovalRouteBody = Body(default_factory=ApprovalRouteBody),
) -> RoutedApproval:
    try:
        return await trust_plane.route_approval(tenant_id, body.request, body.approval_class)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Approval routing failed.",
                "message_ar": "فشل توجيه الموافقة.",
                "error": str(exc),
            },
        ) from exc


@trust_router.post(
    "/tool/verify",
    response_model=ToolVerificationResult,
    summary="Verify tool call",
)
async def trust_tool_verify(
    tenant_id: TenantIdQuery,
    body: ToolVerifyBody = Body(...),
) -> ToolVerificationResult:
    try:
        return await trust_plane.verify_tool_call(
            tenant_id,
            body.agent_id,
            body.tool_name,
            body.parameters,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Tool verification failed.",
                "message_ar": "فشل التحقق من أداة الوكيل.",
                "error": str(exc),
            },
        ) from exc


@trust_router.post(
    "/audit/log",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log audit entry",
    response_class=Response,
)
async def trust_audit_log(
    tenant_id: TenantIdQuery,
    body: AuditEntryPayload = Body(...),
) -> Response:
    try:
        await trust_plane.log_audit_entry(tenant_id, body)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Audit logging failed.",
                "message_ar": "فشل تسجيل التدقيق.",
                "error": str(exc),
            },
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@trust_router.post(
    "/contradiction/detect",
    response_model=ContradictionRecord,
    summary="Detect contradiction",
)
async def trust_contradiction_detect(
    tenant_id: TenantIdQuery,
    body: ContradictionDetectBody = Body(default_factory=ContradictionDetectBody),
) -> ContradictionRecord:
    try:
        return await trust_plane.detect_contradiction(tenant_id, body.intended, body.claimed, body.actual)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Contradiction detection failed.",
                "message_ar": "فشل كشف التناقض.",
                "error": str(exc),
            },
        ) from exc


@trust_router.post(
    "/ai-governance/evaluate",
    response_model=AIGovernanceResult,
    summary="Evaluate AI governance",
)
async def trust_ai_governance(
    tenant_id: TenantIdQuery,
    body: AIGovernanceBody = Body(default_factory=AIGovernanceBody),
) -> AIGovernanceResult:
    try:
        return await trust_plane.evaluate_ai_governance(tenant_id, body.model_id, body.task_type)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "AI governance evaluation failed.",
                "message_ar": "فشل تقييم حوكمة الذكاء الاصطناعي.",
                "error": str(exc),
            },
        ) from exc


# --- Data plane ---


class DataQualityBody(BaseModel):
    dataset_name: str
    data: list[dict[str, Any]] = Field(default_factory=list)


class EventContractBody(BaseModel):
    event_type: str
    contract_schema: dict[str, Any] = Field(default_factory=dict)


class EventValidateBody(BaseModel):
    event_type: str
    event_data: dict[str, Any] = Field(default_factory=dict)


class DocumentIngestBody(BaseModel):
    document_path: str
    extraction_config: dict[str, Any] = Field(default_factory=dict)


class SemanticQueryBody(BaseModel):
    query: str
    collection: str = "default"
    top_k: int = Field(default=5, ge=1, le=50)


@data_router.post(
    "/quality/validate",
    response_model=DataQualityResult,
    summary="Validate data quality",
)
async def data_quality_validate(
    tenant_id: TenantIdQuery,
    body: DataQualityBody = Body(...),
) -> DataQualityResult:
    try:
        return await data_plane.validate_data_quality(tenant_id, body.dataset_name, body.data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Data quality validation failed.",
                "message_ar": "فشل التحقق من جودة البيانات.",
                "error": str(exc),
            },
        ) from exc


@data_router.post(
    "/event-contract/register",
    response_model=dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="Register event contract",
)
async def data_event_contract_register(
    tenant_id: TenantIdQuery,
    body: EventContractBody = Body(...),
) -> dict[str, str]:
    try:
        contract_id = await data_plane.register_event_contract(
            tenant_id,
            body.event_type,
            body.contract_schema,
        )
        return {
            "contract_id": contract_id,
            "message_en": "Event contract registered.",
            "message_ar": "تم تسجيل عقد الحدث.",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Contract registration failed.",
                "message_ar": "فشل تسجيل العقد.",
                "error": str(exc),
            },
        ) from exc


@data_router.post(
    "/event/validate",
    response_model=EventValidationResult,
    summary="Validate event",
)
async def data_event_validate(
    tenant_id: TenantIdQuery,
    body: EventValidateBody = Body(...),
) -> EventValidationResult:
    try:
        return await data_plane.validate_event(tenant_id, body.event_type, body.event_data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Event validation failed.",
                "message_ar": "فشل التحقق من الحدث.",
                "error": str(exc),
            },
        ) from exc


@data_router.post(
    "/document/ingest",
    response_model=ExtractionResult,
    summary="Ingest document",
)
async def data_document_ingest(
    tenant_id: TenantIdQuery,
    body: DocumentIngestBody = Body(...),
) -> ExtractionResult:
    try:
        return await data_plane.ingest_document(tenant_id, body.document_path, body.extraction_config)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Document ingestion failed.",
                "message_ar": "فشل استيعاب المستند.",
                "error": str(exc),
            },
        ) from exc


@data_router.post(
    "/semantic/query",
    response_model=SemanticQueryResult,
    summary="Semantic query",
)
async def data_semantic_query(
    tenant_id: TenantIdQuery,
    body: SemanticQueryBody = Body(default_factory=SemanticQueryBody),
) -> SemanticQueryResult:
    try:
        return await data_plane.query_semantic(tenant_id, body.query, body.collection, body.top_k)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Semantic query failed.",
                "message_ar": "فشل الاستعلام الدلالي.",
                "error": str(exc),
            },
        ) from exc


@data_router.get(
    "/connector/health",
    response_model=list[ConnectorHealthStatus],
    summary="Connector health",
)
async def data_connector_health(
    tenant_id: TenantIdQuery,
) -> list[ConnectorHealthStatus]:
    try:
        return await data_plane.get_connector_health(tenant_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Connector health check failed.",
                "message_ar": "فشل فحص صحة الموصلات.",
                "error": str(exc),
            },
        ) from exc


# --- Operating plane ---


class RulesetEnforceBody(BaseModel):
    branch: str = "main"
    rules: dict[str, Any] = Field(default_factory=dict)


@operating_router.get(
    "/release/{release_id}/gate",
    response_model=ReleaseGateResult,
    summary="Release gate",
)
async def operating_release_gate(
    tenant_id: TenantIdQuery,
    release_id: str,
) -> ReleaseGateResult:
    try:
        return await operating_plane.check_release_gate(tenant_id, release_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Release gate check failed.",
                "message_ar": "فشل فحص بوابة الإصدار.",
                "error": str(exc),
            },
        ) from exc


@operating_router.get(
    "/artifact/{artifact_id}/provenance",
    response_model=ProvenanceResult,
    summary="Artifact provenance",
)
async def operating_artifact_provenance(
    tenant_id: TenantIdQuery,
    artifact_id: str,
) -> ProvenanceResult:
    try:
        return await operating_plane.verify_artifact_provenance(tenant_id, artifact_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Provenance verification failed.",
                "message_ar": "فشل التحقق من المصدرية.",
                "error": str(exc),
            },
        ) from exc


@operating_router.get(
    "/deployment/{environment}/status",
    response_model=DeploymentStatus,
    summary="Deployment status",
)
async def operating_deployment_status(
    tenant_id: TenantIdQuery,
    environment: str,
) -> DeploymentStatus:
    try:
        return await operating_plane.get_deployment_status(tenant_id, environment)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Deployment status lookup failed.",
                "message_ar": "فشل جلب حالة النشر.",
                "error": str(exc),
            },
        ) from exc


@operating_router.post(
    "/ruleset/enforce",
    response_model=RulesetEnforcementResult,
    summary="Enforce ruleset",
)
async def operating_ruleset_enforce(
    tenant_id: TenantIdQuery,
    body: RulesetEnforceBody = Body(default_factory=RulesetEnforceBody),
) -> RulesetEnforcementResult:
    try:
        return await operating_plane.enforce_ruleset(tenant_id, body.branch, body.rules)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Ruleset enforcement failed.",
                "message_ar": "فشل فرض مجموعة القواعد.",
                "error": str(exc),
            },
        ) from exc
