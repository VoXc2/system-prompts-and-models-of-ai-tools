# Invoice Flow

## Current: Manual (via Moyasar dashboard)
1. Customer agrees to purchase
2. Create invoice in Moyasar: amount + description + customer email
3. Copy invoice URL
4. Send to customer via WhatsApp/email
5. Customer pays
6. Moyasar confirms (webhook if backend running, else dashboard)
7. Manual welcome email
8. Manual onboarding

## Future: Automated (after Railway deploy)
See `api/routers/webhooks.py` for the backend flow.

## Invoice numbering
Format: DLX-YYYY-NNNNN (sequential)

## VAT/ZATCA
Currently below threshold. Consult accountant when approaching 187,500 SAR annual.
