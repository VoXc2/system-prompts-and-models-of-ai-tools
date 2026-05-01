# Connector Catalog — كتالوج التكاملات

> 14 تكامل، كل واحد له launch_phase + risk_level + allowed/blocked actions + Arabic risk notes.

## 1. القائمة

| key | الحالة | المرحلة | المخاطر | ملاحظة |
|-----|--------|---------|---------|--------|
| whatsapp_cloud | beta | phase_1 | high | PDPL: لا cold بدون opt-in |
| gmail | beta | phase_1 | high | drafts فقط افتراضياً |
| google_calendar | beta | phase_1 | medium | إدراج بموافقة |
| google_meet | beta | phase_2 | high | transcripts بموافقة الجميع |
| moyasar | beta | phase_1 | high | لا تخزّن بطاقات |
| linkedin_lead_forms | coming_soon | phase_2 | medium | leads مصرّح بها |
| google_business_profile | coming_soon | phase_2 | medium | ردود بموافقة |
| x_api | coming_soon | phase_3 | high | حسب خطة الـAPI |
| instagram_graph | coming_soon | phase_3 | high | لا auto-publish |
| google_sheets | beta | phase_1 | low | append بموافقة |
| crm_generic | beta | phase_2 | medium | اقرأ أولاً |
| website_forms | live | phase_1 | low | مصدر العميل |
| composio | coming_soon | phase_4 | medium | خلف Tool Gateway |
| mcp_gateway | coming_soon | phase_4 | high | allowlist + audit |

## 2. Launch Phases

- **Phase 1** (الإطلاق الخاص): WhatsApp + Gmail + Calendar + Moyasar + Sheets + Website Forms.
- **Phase 2** (Beta موسّع): LinkedIn Lead Forms + Google Business + Meet + CRM.
- **Phase 3** (السوشيال): X + Instagram.
- **Phase 4** (التوسع): Composio + MCP Gateway.

## 3. Endpoints

```
GET /api/v1/connector-catalog/catalog
GET /api/v1/connector-catalog/summary
GET /api/v1/connector-catalog/status
GET /api/v1/connector-catalog/risks
GET /api/v1/connector-catalog/{connector_key}
```

## 4. القاعدة الذهبية

كل tool action يمر من Tool Gateway في `platform_services` → Action Policy → draft/approval_required. الـCatalog هنا توثّق فقط ما هو متاح، **لا تنفّذ**.
