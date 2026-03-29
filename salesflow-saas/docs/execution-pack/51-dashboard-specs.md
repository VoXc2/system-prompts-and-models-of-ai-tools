# Dashboard Specifications

## Analytics API Endpoints (Current)

```
GET /analytics/overview     # KPI summary with period comparison
GET /analytics/pipeline     # Pipeline breakdown by stage
GET /analytics/revenue      # Revenue trends and projections
GET /analytics/leads        # Lead metrics by source/status
GET /analytics/team         # Per-agent performance
GET /analytics/campaigns    # Campaign ROI
GET /analytics/velocity     # Pipeline velocity + forecasting
GET /analytics/export       # CSV export
GET /sla/stats              # SLA compliance metrics
```

## Dashboard Data Contracts

### Overview Response
```json
{
  "period": "2026-03",
  "kpis": {
    "total_leads": 450,
    "total_leads_trend": 12.5,
    "total_deals": 85,
    "total_deals_trend": 8.3,
    "total_revenue": 750000,
    "total_revenue_trend": 15.2,
    "conversion_rate": 18.9,
    "conversion_rate_trend": 2.1,
    "avg_deal_value": 8824,
    "pipeline_velocity": 12500
  }
}
```

### Velocity Response
```json
{
  "pipeline_velocity": 12500,
  "avg_sales_cycle_days": 21,
  "avg_deal_size": 8824,
  "win_rate": 35.2,
  "open_pipeline_value": 850000,
  "weighted_pipeline": 425000,
  "forecast_30_days": 180000,
  "forecast_60_days": 320000,
  "forecast_90_days": 450000,
  "funnel": {
    "total": 85,
    "won": 30,
    "lost": 25,
    "open": 30
  }
}
```

### Team Performance Response
```json
{
  "agents": [
    {
      "user_id": "uuid",
      "name": "أحمد",
      "leads_assigned": 45,
      "deals_active": 12,
      "deals_won": 8,
      "revenue_generated": 200000,
      "avg_response_time_minutes": 25,
      "sla_compliance_pct": 92,
      "activities_this_week": 34
    }
  ]
}
```

## Anomaly Detection Signals

| Signal | Condition | Severity |
|--------|-----------|----------|
| Lead volume spike | > 3x daily average | Info |
| Lead volume drop | < 50% daily average | Warning |
| Win rate crash | < 50% of trailing average | Critical |
| Pipeline stall | No stage changes in 48h | Warning |
| Agent inactive | No activity in 24h (work day) | Warning |
| AI error spike | > 10% error rate in 1h | Critical |
| Integration failure | 3+ consecutive webhook failures | Critical |

## Alert Thresholds (Configurable)

```json
{
  "alerts": {
    "sla_breach": {"enabled": true, "channels": ["notification", "whatsapp"]},
    "lead_volume_drop": {"enabled": true, "threshold_pct": 50},
    "pipeline_stall": {"enabled": true, "hours": 48},
    "ai_error_rate": {"enabled": true, "threshold_pct": 10},
    "daily_summary": {"enabled": true, "time": "08:00", "timezone": "Asia/Riyadh"}
  }
}
```
