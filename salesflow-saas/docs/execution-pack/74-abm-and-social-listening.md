# ABM & Social Listening

## Account-Based Marketing (ABM)

### Account Targeting Process
```
1. Define ICP criteria per sector
2. Build target account list (100-500 per sector)
3. Map stakeholders (decision maker, influencer, user)
4. Score accounts by fit + intent signals
5. Assign to outbound sequences
6. Track engagement across all touchpoints
7. Prioritize by activity/response
```

### Stakeholder Mapping
```json
{
  "account": "عيادة الصحة",
  "industry": "healthcare",
  "stakeholders": [
    {
      "name": "د. أحمد",
      "title": "المدير التنفيذي",
      "role": "decision_maker",
      "linkedin": "...",
      "phone": "+966...",
      "engagement_score": 75
    },
    {
      "name": "سارة",
      "title": "مديرة العمليات",
      "role": "influencer",
      "engagement_score": 40
    }
  ]
}
```

### Signal-Based Prioritization

| Signal | Weight | Source |
|--------|--------|--------|
| Visited pricing page | High | Website tracking |
| Downloaded lead magnet | High | Form submission |
| Engaged with social content | Medium | Social listening |
| Company hiring sales roles | Medium | LinkedIn |
| Competitor mentioned negatively | High | Social listening |
| Industry event attendance | Low | Event tracking |

## Social Listening System

### Architecture (Current)
```
Listening Streams (configured per tenant)
  → Platform APIs / monitoring
    → AI analysis (relevance, ICP match, priority)
      → Store as SocialPost
        → AI draft comment (if relevant)
          → Human approval queue
            → Publish (if approved)
              → Track attribution (did they become a lead?)
```

### Listening Stream Configuration
```python
class ListeningStream(TenantModel):
    name = Column(String(255))
    platform = Column(String(50))      # twitter, linkedin, instagram
    stream_type = Column(String(50))   # keyword, competitor, hashtag
    keywords = Column(JSONB)           # ["CRM عيادات", "نظام مبيعات"]
    competitors = Column(JSONB)        # ["HubSpot", "Salesforce"]
    hashtags = Column(JSONB)           # ["#B2B_السعودية"]
    is_active = Column(Boolean)
    auto_draft = Column(Boolean)       # Auto-generate comment drafts
    check_interval_minutes = Column(Integer, default=60)
```

### Comment Engagement Workflow

```
Post detected → AI scores relevance (0-100)
  → If score >= 60:
    → AI drafts value-add comment
      → Comment enters approval queue
        → Human reviews:
          → Approve → Publish → Track
          → Edit → Update → Approve → Publish → Track
          → Reject → Log reason → Skip
  → If score < 60:
    → Store for reference, skip comment
```

### Comment Draft Rules
1. **Never sell directly** — Add value first
2. **Never fake identity** — Comment from brand account
3. **Always be helpful** — Share insight, not pitch
4. **Arabic preferred** — Match post language
5. **Professional tone** — No emojis overload, no slang
6. **Include subtle CTA** — Only if natural ("نسوينا دليل عن هالموضوع...")

### Warm Lead Creation
When a social engagement leads to a response or DM:
1. Create lead with `source=social_listening`
2. Link to original SocialPost
3. Include engagement context in lead notes
4. Assign to social-trained agent
5. Track full attribution chain

### API Endpoints (Current)
```
GET    /social/streams              # List listening streams
POST   /social/streams              # Create stream
PUT    /social/streams/{id}         # Update stream
GET    /social/posts                # List detected posts
GET    /social/comments/pending     # Pending approval queue
POST   /social/comments/{id}/review # Approve/reject comment
GET    /social/stats                # Performance metrics
```

## Sales Enablement Assets

### For Sales Team
- One-pager per ICP (Arabic + English)
- ROI calculator (interactive)
- Demo script per industry
- Objection handling playbook
- Case study library
- Competitive battle cards

### For Partners
- Co-branded presentation deck
- Partner onboarding guide
- Client proposal template
- Training videos (Arabic)
- Marketing materials library
