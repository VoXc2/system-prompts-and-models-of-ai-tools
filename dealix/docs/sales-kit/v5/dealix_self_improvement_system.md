# Dealix — Self-Improvement System (نظام التطوير الذاتي)

> نظام Dealix يطوّر نفسه تلقائياً: يحلّل استخدامه، يكتشف فرص التحسين، ويطرح PRs على نفسه. بدون تدخّل بشري يومي.

**آخر تحديث**: أبريل 2026 | **الحالة**: Phase 1 تشغيل، Phase 2-3 roadmap

---

## 🎯 الفلسفة

> **"منتج لا يتطوّر تلقائياً = منتج ميّت."**

Dealix يعمل على 3 أبعاد للتطوير الذاتي:
1. **تطوير المنتج** (features + fixes تلقائية)
2. **تطوير التسويق** (conversion optimization)
3. **تطوير العمليات** (internal processes)

كل بُعد فيه **loop** يشتغل تلقائياً بدون تدخّل يومي.

---

## 🔄 Loop 1: Product Self-Improvement

### الـ Input: بيانات الاستخدام
- **Sentry errors**: كل خطأ يحصل عند عميل
- **User analytics** (PostHog): أي feature يُستخدم كم مرة
- **Session recordings** (Hotjar): أين العميل يتوقّف/يرتبك
- **Support tickets**: المشاكل المتكرّرة
- **NPS feedback**: التعليقات النصية
- **A/B test results**: ما يحوّل أفضل

### الـ Processing: AI Agent
**دور الوكيل**: Daily cron في `0 7 * * *` (7 AM AST)

```python
# api/self_improvement/product_loop.py

def run_product_loop():
    # 1. جمع البيانات من آخر 24 ساعة
    sentry_errors = fetch_sentry_issues(since=yesterday)
    posthog_events = fetch_posthog_metrics(since=yesterday)
    support_tickets = fetch_intercom_conversations(since=yesterday)
    nps_feedback = fetch_nps_comments(since=yesterday)
    
    # 2. تصنيف وفرز
    issues = categorize({
        'bugs': sentry_errors,
        'feature_requests': support_tickets + nps_feedback,
        'ux_friction': posthog_events,
    })
    
    # 3. Priority scoring عبر GPT-4
    prioritized = ai_prioritize(issues, criteria={
        'impact': '# users affected × severity',
        'effort': 'estimated dev hours',
        'strategic': 'alignment with roadmap',
    })
    
    # 4. الإجراءات التلقائية
    for item in prioritized.top_5:
        if item.category == 'critical_bug':
            create_github_issue(item, priority='P0')
            notify_founder_via_slack(item)
        elif item.category == 'high_priority_feature':
            create_github_issue(item, priority='P1', label='ai-suggested')
        elif item.category == 'minor_fix':
            # AI generate PR draft
            pr = ai_generate_pr(item)
            create_draft_pr(pr, label='ai-generated', review_required=True)
    
    # 5. Daily Report
    send_daily_digest(sami, prioritized)
```

### الـ Output: تحسينات فعلية
**أسبوعياً يتوقع**:
- 2-5 issues تُفتح تلقائياً
- 1-3 draft PRs من الـ AI (يراجعها الإنسان)
- Daily digest من 300 كلمة
- Weekly trend report (Friday)

### Guard Rails (حواجز الأمان)
- ❌ AI ما يدمج PRs تلقائياً — إنسان فقط
- ❌ AI ما يعدّل production database
- ❌ AI ما يتصل بـ APIs مدفوعة بدون approval
- ❌ AI ما يرد على العملاء مباشرة (يصيغ فقط)
- ✅ AI يقترح + إنسان يقرّر

---

## 📈 Loop 2: Marketing Self-Improvement

### الـ Input
- **Website analytics** (Plausible + Google Analytics)
- **Ad performance** (Meta Ads + Google Ads APIs)
- **Email metrics** (Open rate, CTR من SendGrid)
- **Social media engagement** (LinkedIn + Twitter APIs)
- **SEO rankings** (Google Search Console)
- **Competitors' content** (RSS feeds + web monitoring)

### الـ Processing
**Cron schedules**:
- **Daily 8 AM**: Ad performance review + budget reallocation
- **Weekly Monday**: Content calendar suggestions
- **Monthly 1st**: Competitive analysis deep-dive

```python
# api/self_improvement/marketing_loop.py

def optimize_ad_spend():
    """Daily ad budget optimization."""
    campaigns = fetch_all_active_campaigns()
    
    for campaign in campaigns:
        performance = get_last_7_days(campaign)
        
        if performance.cpa > threshold * 1.5:
            # Under-performing → reduce budget 20%
            suggestion = {
                'action': 'reduce_budget',
                'from': campaign.budget,
                'to': campaign.budget * 0.8,
                'reason': f'CPA {performance.cpa} > target {threshold}'
            }
            send_for_approval(suggestion, channel='#marketing-alerts')
        
        elif performance.cpa < threshold * 0.7 and performance.volume > 10:
            # Over-performing → increase budget 30%
            suggestion = {
                'action': 'increase_budget',
                'from': campaign.budget,
                'to': campaign.budget * 1.3,
                'reason': f'Strong CPA {performance.cpa}, scaling up'
            }
            auto_apply(suggestion)  # Auto-approved for scaling up
    
    log_daily_changes()


def generate_weekly_content():
    """Every Monday: suggest 5 posts for the week."""
    trends = fetch_saudi_marketing_trends()
    competitor_content = fetch_competitor_recent_posts()
    our_historical_winners = fetch_our_top_posts()
    
    suggestions = ai_generate_content(
        style='dealix_brand_voice_ar',
        topics=['AI', 'Marketing', 'Saudi SMEs', 'ZATCA'],
        trends=trends,
        avoid=competitor_content,
        inspiration=our_historical_winners,
        count=5
    )
    
    create_content_calendar_entries(suggestions)
    notify_content_team()
```

### Auto-Actions المسموحة
- ✅ **زيادة ميزانية** حملة ناجحة (حتى 30% بدون approval)
- ✅ **إيقاف إعلانات فاشلة** (CPA > 3x target)
- ✅ **إنشاء variants جديدة** للـ A/B testing
- ✅ **Schedule social posts** (drafts للمراجعة)
- ✅ **Email personalization** بناء على behavior

### Actions تحتاج approval
- ❌ **تخفيض ميزانية حملة** > 20%
- ❌ **إطلاق حملة جديدة** بميزانية > 5,000 ر.س
- ❌ **تغيير brand messaging**
- ❌ **بعث email جماعي** > 100 شخص

---

## ⚙️ Loop 3: Operations Self-Improvement

### الـ Input
- **Financial data** (Moyasar + Banking APIs)
- **Customer data** (CRM في PostgreSQL)
- **Team productivity** (GitHub + Linear velocity)
- **Server metrics** (Railway + Sentry + Uptime Robot)
- **Customer health scores** (computed metric)

### Daily Checks (0 6 * * *)
```python
def daily_operations_review():
    # 1. Financial Health
    yesterday_revenue = get_yesterday_revenue()
    yesterday_expenses = get_yesterday_expenses()
    runway = calculate_runway()
    
    if runway < 6_months:
        alert_sami(severity='high', message=f'Runway at {runway} months')
    
    # 2. Customer Health
    at_risk_customers = find_customers_low_usage(days=7)
    for customer in at_risk_customers:
        create_cs_task(
            owner='customer_success',
            action='personal_outreach',
            priority='high',
            customer=customer
        )
    
    # 3. System Health
    uptime = calculate_7d_uptime()
    if uptime < 99.5:
        create_post_mortem_template()
    
    # 4. Team Productivity
    velocity = get_team_velocity_7d()
    if velocity < baseline * 0.7:
        schedule_retro_with_team()
    
    # 5. Send daily digest
    send_sami_morning_digest({
        'revenue': yesterday_revenue,
        'new_customers': count_new_customers(1),
        'at_risk': len(at_risk_customers),
        'system_health': uptime,
        'action_items': extract_top_3_priorities()
    })
```

### Smart Alerts (not spam)
**Rule**: تنبيه فقط إذا:
- تغيير > 20% vs baseline
- حدث مالي > 1,000 ر.س
- ملف أمني critical
- عميل Enterprise متأثر

**لا تنبيه لـ**:
- تقلّبات طبيعية (normal noise)
- مشاكل مؤقتة تحلّ نفسها في < 5 دقائق
- أمور "nice to know"

---

## 🧠 AI Brain: GPT-4 + Context

### النظام الأساسي
Dealix عنده **"brain"** مركزي — GPT-4 model مع:
- **System prompt** يحدّد شخصية Dealix (Saudi Gulf، reliable، measurement-first)
- **Context window** فيها:
  - Dealix KB (جميع الملفات من `docs/sales-kit/` + `DEALIX_MASTER_PLAYBOOK`)
  - Recent changes (last 7 days commits, issues, PRs)
  - Customer feedback (last 30 days)
  - Financial state (runway, MRR, burn rate)

### كيف يعمل
```python
class DealixBrain:
    def __init__(self):
        self.context = self._load_context()
        self.model = 'gpt-4-turbo'
        self.system = self._build_system_prompt()
    
    def suggest(self, query):
        """اسأل Dealix عن أي قرار — يرد بناء على context."""
        response = openai.chat.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': self.system},
                {'role': 'system', 'content': f'Context: {self.context}'},
                {'role': 'user', 'content': query}
            ],
            temperature=0.3  # منخفض للـ consistency
        )
        return response
    
    def weekly_reflection(self):
        """كل أحد: يكتب reflection على الأسبوع الماضي."""
        return self.suggest("""
        Review last week:
        - What worked well?
        - What didn't?
        - What are the top 3 priorities for this week?
        - Any risks we should address?
        Write in Saudi Gulf Arabic, 400 words max.
        """)
    
    def pre_decision_check(self, decision):
        """قبل أي قرار كبير، دور عليه من dealix brain."""
        return self.suggest(f"""
        We're considering: {decision}
        
        Given our current state:
        - Runway: {self.context.runway}
        - MRR: {self.context.mrr}
        - Priorities: {self.context.priorities}
        
        Should we proceed? What are the risks?
        """)
```

### Brain Capabilities
- ✅ **Strategic advice** (بناء على context)
- ✅ **Content drafts** (posts, emails, docs)
- ✅ **Decision analysis** (pros/cons)
- ✅ **Pattern detection** (في الـ data)
- ✅ **Code review** (للـ PRs)
- ❌ **Final decisions** — إنسان فقط

---

## 🔒 Safety & Governance

### كل auto-action يسجّل
**Audit log** في `/audit/YYYY-MM-DD.jsonl`:
```json
{
  "timestamp": "2026-04-23T10:30:00Z",
  "action": "increase_ad_budget",
  "campaign_id": "camp_123",
  "from": 1000,
  "to": 1300,
  "reason": "CPA 45 < target 70",
  "auto_approved": true,
  "human_reviewer": null,
  "reverted": false
}
```

### Review weekly
كل جمعة، Sami يراجع:
- عدد auto-actions
- كم منها كان صحيح
- أي منها يحتاج revert

### Kill Switch
**دائماً متاح**: في أي لحظة، Sami يكتب في Slack:
```
/dealix-pause-ai
```
→ كل الـ loops تتوقّف فوراً.

### Red Lines (الحدود)
1. ❌ AI ما يتصرّف بالمال مباشرة (ما يحوّل، ما يستثمر)
2. ❌ AI ما يوظّف أو يفصل
3. ❌ AI ما يعلّق contracts
4. ❌ AI ما يتواصل مع media بدون approval
5. ❌ AI ما يخزّن credentials أو secrets

---

## 📊 مؤشرات نجاح الـ Self-Improvement

### Phase 1 Metrics (الحالي)
- ✅ Daily digest يُرسل يومياً
- ✅ Auto-issue creation من Sentry errors
- ✅ Weekly reflection من Brain
- Target: **50% من الـ bugs تُكتشف تلقائياً قبل العميل**

### Phase 2 Metrics (Q3 2026)
- AI generates 30% من الـ content
- AI manages ad budget بدون daily manual review
- Customer health scores تقود CS outreach

### Phase 3 Metrics (2027)
- AI يكتب 50% من الـ PRs (مراجعة إنسان)
- AI يدير onboarding الكامل للعملاء الجدد
- AI يقود A/B testing pipeline بدون تدخّل

---

## 🛠️ التقنيات المستخدمة

| الطبقة | الأداة | السبب |
|-------|--------|-------|
| LLM Brain | OpenAI GPT-4 Turbo | أفضل reasoning + Arabic |
| Fine-tuning | HuggingFace + AraBERT | للـ Saudi-specific tasks |
| Scheduling | Celery + Redis | موثوق + known |
| Monitoring | Sentry + Prometheus | visibility كامل |
| Analytics | PostHog (self-hosted) | privacy + flexibility |
| Messaging | Slack API | الفريق + alerts |
| Auto-PR | GitHub Actions + gh CLI | native integration |

---

## 🎯 The Meta Goal

> **Dealix يصير 'self-sustaining' بعد 18 شهر**:
> - المنتج يطوّر نفسه (90% bug fixes + 50% features)
> - التسويق يحسّن نفسه (budget + content + targeting)
> - العمليات تدير نفسها (CS + finance + ops)
> - الإنسان يركّز على **الاستراتيجية + العلاقات + الإبداع**

هذا هو الهدف الأسمى. ما يعني الإنسان يختفي — يعني الإنسان يرتفع لمستوى أعلى.

---

## 🚀 الخطوة التالية (This Week)

- [ ] بناء `api/self_improvement/` module أساسي
- [ ] ربط Sentry → auto-issue creation
- [ ] Daily digest cron (7 AM AST) 
- [ ] Dealix Brain system prompt + tests
- [ ] Audit log infrastructure
- [ ] Slack integration (`/dealix-*` commands)

---

**Dealix — يتنفّس وحده. يتعلّم وحده. يطوّر نفسه وحده.**
