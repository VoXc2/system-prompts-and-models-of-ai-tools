# Dealix (ديل اي اكس) — Go-Live Checklist

> قائمة التحقق النهائية قبل الإطلاق الرسمي
> Last updated: 2026-03-31

---

## Infrastructure / البنية التحتية

- [ ] Domain configured and DNS fully propagated (A, CNAME, MX)
- [ ] SSL certificate active (Let's Encrypt or Cloudflare) — verify with `curl -I https://dealix.sa`
- [ ] Nginx reverse proxy configured and tested
- [ ] Firewall rules set (only 80, 443, 22 open)

## Frontend / الواجهة الأمامية

- [ ] Frontend deployed and accessible at production URL
- [ ] Landing page loads in < 3 seconds (test with GTmetrix or Lighthouse)
- [ ] Arabic RTL renders correctly on all pages
- [ ] Responsive design verified on mobile (375px), tablet (768px), desktop (1440px)
- [ ] No console errors in browser DevTools
- [ ] Favicon and meta tags set correctly
- [ ] Open Graph / social sharing meta tags configured

## Backend / الخادم الخلفي

- [ ] Backend deployed and `/api/v1/health` returns HTTP 200
- [ ] DEBUG = False in production environment
- [ ] CORS configured to allow only production frontend domain
- [ ] Rate limiting active on auth endpoints
- [ ] API documentation accessible (if intended for public)

## Database / قاعدة البيانات

- [ ] PostgreSQL running on production server
- [ ] Database migrated to latest schema (`alembic upgrade head`)
- [ ] Seed data loaded (roles, permissions, plans, commission tiers)
- [ ] Database user has minimal required permissions (not superuser)
- [ ] Connection pooling configured

## Cache & Workers / الكاش والعمال

- [ ] Redis running and responding to PING
- [ ] Celery workers running (verify with `celery -A app inspect active`)
- [ ] Celery beat running (scheduled tasks: follow-ups, report generation)
- [ ] Flower or monitoring dashboard accessible for Celery

## Communication Channels / قنوات التواصل

- [ ] WhatsApp Business API connected and verified with Meta
- [ ] WhatsApp message templates approved
- [ ] Email SMTP verified — test send from `noreply@dealix.sa`
- [ ] Email templates rendering correctly (Arabic RTL)
- [ ] SMS via Unifonic verified — test send to Saudi number
- [ ] SPF, DKIM, DMARC records configured for email deliverability

## Core Features / الميزات الأساسية

- [ ] Admin login works (admin@dealix.sa)
- [ ] Affiliate registration flow works end-to-end
- [ ] Lead creation works (manual + API)
- [ ] Deal creation works with stage transitions
- [ ] Commission calculation triggers correctly on deal close
- [ ] Commission tiers applied correctly (5%, 7%, 10%)
- [ ] Dashboard loads correctly with real-time data
- [ ] Notification system sends WhatsApp + Email + SMS

## Legal / القانوني

- [ ] Privacy policy accessible at `/privacy`
- [ ] Terms of service accessible at `/terms`
- [ ] Guarantee terms accessible at `/guarantee`
- [ ] Cookie consent banner (if applicable)
- [ ] PDPL (Saudi Personal Data Protection Law) compliance verified

## Monitoring & Operations / المراقبة والعمليات

- [ ] Application logging configured (structured JSON logs)
- [ ] Error tracking active (Sentry or equivalent)
- [ ] Uptime monitoring configured (UptimeRobot, Pingdom, or equivalent)
- [ ] Automated daily database backup configured
- [ ] Backup restoration tested at least once
- [ ] Server resource alerts configured (CPU > 80%, disk > 90%)

## Emergency Preparedness / الجاهزية للطوارئ

- [ ] Emergency contacts documented (see below)
- [ ] Rollback procedure documented and tested
- [ ] Database restore procedure tested
- [ ] On-call rotation defined (if team > 1)

---

## Emergency Contacts / جهات الاتصال للطوارئ

| Role / الدور | Name / الاسم | Phone / الهاتف | Email |
|---|---|---|---|
| Technical Lead | __________ | +966 5XX XXX XXXX | __________ |
| DevOps | __________ | +966 5XX XXX XXXX | __________ |
| Product Owner | __________ | +966 5XX XXX XXXX | __________ |
| Hosting Provider Support | __________ | __________ | __________ |

---

## Sign-Off / التوقيع النهائي

| Approver / المعتمد | Date / التاريخ | Signature / التوقيع |
|---|---|---|
| Technical Lead | ____/____/____ | __________ |
| Product Owner | ____/____/____ | __________ |
| QA Lead | ____/____/____ | __________ |

> لا يتم الإطلاق حتى يتم التوقيع من جميع المعتمدين أعلاه.
> Go-live requires sign-off from all approvers above.
