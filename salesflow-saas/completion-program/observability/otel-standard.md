# Observability Standard — OpenTelemetry

> **Version:** 1.0 — 2026-04-16
> **Standard:** OpenTelemetry (OTel) — vendor-neutral traces, metrics, logs.
> **Authority:** Platform Engineer — all new services and agents must comply.
> **Goal:** Every traceable surface has OTel telemetry + correlation IDs. Observability is a release gate, not an afterthought.

---

## Signals

### Traces

Every HTTP request, agent decision, tool call, and Temporal activity must produce an OTel trace span.

**Required span attributes (all spans):**

```python
span.set_attribute("tenant.id", tenant_id)
span.set_attribute("trace.id", trace_id)         # OTel trace_id (hex)
span.set_attribute("correlation.id", correlation_id)  # Business-level ID (deal_id or workflow_id)
span.set_attribute("service.name", "dealix-backend")
span.set_attribute("service.version", os.getenv("APP_VERSION", "unknown"))
span.set_attribute("deployment.environment", os.getenv("ENVIRONMENT", "development"))
```

**Additional attributes by span type:**

| Span Type | Extra Attributes |
|-----------|----------------|
| HTTP request | `http.method`, `http.route`, `http.status_code`, `http.url` |
| Agent decision | `agent.name`, `agent.role`, `agent.track`, `agent.output_schema`, `agent.confidence_score` |
| Tool call | `tool.name`, `tool.action`, `tool.connector_version`, `tool.idempotency_key` |
| Temporal activity | `temporal.workflow_id`, `temporal.activity_type`, `temporal.attempt` |
| LLM call | `llm.provider`, `llm.model`, `llm.prompt_tokens`, `llm.completion_tokens`, `llm.response_format` |

### Metrics

All metrics use Prometheus naming convention (`snake_case`), exported via OTel collector.

**Core metrics:**

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `dealix_agent_decisions_total` | Counter | `track`, `agent_role`, `output_schema`, `tenant_id` | Total agent decisions emitted |
| `dealix_agent_confidence_score` | Histogram | `track`, `agent_role` | Distribution of confidence scores |
| `dealix_tool_calls_total` | Counter | `tool_name`, `action`, `status` | Total tool calls |
| `dealix_tool_call_duration_seconds` | Histogram | `tool_name`, `action` | Tool call latency |
| `dealix_tool_contradictions_total` | Counter | `tool_name`, `contradiction_status` | Tool verification contradictions |
| `dealix_workflow_duration_seconds` | Histogram | `workflow_type`, `track` | Temporal workflow duration |
| `dealix_approval_wait_seconds` | Histogram | `track`, `sensitivity` | Time waiting for HITL approval |
| `dealix_connector_errors_total` | Counter | `connector_name`, `action`, `error_type` | Connector failures |
| `dealix_llm_tokens_total` | Counter | `provider`, `model`, `type` | LLM token usage |
| `dealix_pdpl_consent_checks_total` | Counter | `purpose`, `result` | PDPL consent check outcomes |
| `dealix_opa_policy_decisions_total` | Counter | `policy`, `result` | OPA policy decision outcomes |

### Logs

All logs must be structured JSON and include:

```json
{
  "timestamp": "ISO-8601",
  "level": "INFO|WARNING|ERROR|CRITICAL",
  "service": "dealix-backend",
  "environment": "production",
  "trace_id": "otel-trace-id-hex",
  "span_id": "otel-span-id-hex",
  "correlation_id": "deal-or-workflow-id",
  "tenant_id": "uuid",
  "message": "...",
  "event": "...",
  "extra": {}
}
```

**Forbidden in logs:**
- Raw personal data (name, email, phone, national ID)
- API keys or tokens
- Cleartext passwords

---

## Correlation ID Strategy

Every business operation carries a `correlation_id` from creation to completion:

| Operation Type | Correlation ID |
|---------------|---------------|
| Deal-related | `deal:{deal_id}` |
| Partner-related | `partner:{partner_id}` |
| Temporal workflow | `workflow:{workflow_id}` |
| Outreach campaign | `campaign:{campaign_id}` |

The `correlation_id` is:
1. Set at the entry point (API endpoint or Temporal workflow start)
2. Propagated via OTel baggage through all downstream spans
3. Stored in every log entry
4. Stored in tool verification ledger entries

---

## OTel Collector Configuration (docker-compose)

```yaml
otel-collector:
  image: otel/opentelemetry-collector-contrib:0.120.0
  command: ["--config=/etc/otelcol/config.yaml"]
  volumes:
    - ./otel-collector-config.yaml:/etc/otelcol/config.yaml
  ports:
    - "4317:4317"    # OTLP gRPC
    - "4318:4318"    # OTLP HTTP
    - "8888:8888"    # Prometheus metrics (collector self)
    - "8889:8889"    # Prometheus exporter (app metrics)
```

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
  memory_limiter:
    limit_mib: 256
  resource:
    attributes:
      - action: insert
        key: deployment.environment
        from_attribute: ENVIRONMENT

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: dealix
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true
  logging:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/jaeger, logging]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [logging]
```

---

## FastAPI Instrumentation (backend/app/core/telemetry.py)

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
import os

OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")


def setup_telemetry(app) -> None:
    # Traces
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True),
        export_interval_millis=15_000,
    )
    metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))

    # Auto-instrumentation
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
```

---

## Eval Gates — Release Criteria

Every release must pass the following observability checks before promotion to production:

| Gate | Check | Pass Criteria |
|------|-------|--------------|
| Trace coverage | All critical paths produce traces | `dealix_agent_decisions_total` counter increments in staging smoke test |
| Metric emission | All 11 core metrics present | Prometheus scrape returns all metrics with non-null values |
| Correlation propagation | `correlation_id` present in all spans for a sample deal flow | Jaeger trace shows `correlation_id` in all child spans |
| Contradiction rate | Tool contradiction rate | `dealix_tool_contradictions_total{contradiction_status="critical"}` = 0 in last 24 h of staging |
| LLM token budget | Token usage within budget | `dealix_llm_tokens_total` < threshold per tenant per hour |
| Log PII scan | No personal data in logs | Automated regex scan on staging log sample — zero matches for patterns: `\d{10}` (phone), `\b[A-Z]{2}\d{7}\b` (ID) |

---

## Offline Eval Datasets

Maintained in `backend/tests/evals/`:

| Dataset | Contents | Update Frequency | Pass Criteria |
|---------|---------|-----------------|--------------|
| `deal_memo_eval.jsonl` | 50 sample deal contexts + expected memo outputs | Per sprint | Confidence score ≥ 0.8 on 90 % of samples |
| `tool_verification_eval.jsonl` | 20 injected contradiction scenarios | Per sprint | 100 % contradiction detected |
| `pdpl_consent_eval.jsonl` | 30 consent check scenarios (consent/no-consent/expired) | Per sprint | 100 % correct decision |
| `prompt_injection_eval.jsonl` | 50 prompt injection attempts | Per release | 100 % blocked |
| `schema_conformance_eval.jsonl` | 100 agent outputs → schema validation | Per sprint | 100 % conformance |

---

## Red-Team Coverage (per release)

| Surface | Red-Team Scenario | Automated? | Frequency |
|---------|-----------------|-----------|---------|
| Agent prompts | Prompt injection via deal name, contact notes | Yes (eval dataset) | Every release |
| Tool calls | Malformed tool response → agent behaviour | Yes (unit test) | Every sprint |
| API endpoints | Auth bypass, tenant isolation break | Semi-auto (OWASP ZAP) | Every release |
| Temporal workflows | Duplicate trigger, race condition | Yes (integration test) | Every release |
| LLM output schema | Non-conforming output passes validation | Yes (schema eval) | Every sprint |
