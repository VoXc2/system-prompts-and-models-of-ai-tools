# Dealix (ديل اي اكس) — Email Connection Checklist

> خطوات إعداد البريد الإلكتروني بالكامل
> Last updated: 2026-03-31

---

## Step 1: Choose Email Provider / اختيار مزود البريد

| Provider | Cost/mo | Pros | Cons |
|---|---|---|---|
| **Google Workspace** | ~$7/user | Best deliverability, familiar UI | Cost per user |
| **Zoho Mail** | Free (5 users) | Free tier, decent UI | Less known |
| **Custom SMTP (Postfix)** | Free | Full control | Complex setup, deliverability risk |
| **SendGrid** | Free (100/day) | API-first, great for transactional | Not for daily email |

**Recommendation:** Google Workspace for team email + SendGrid for transactional/automated emails.

---

## Step 2: Configure MX Records / إعداد سجلات MX

> Must be done at DNS provider (Cloudflare, registrar, etc.)

### Google Workspace:
```
Priority  Host    Value
1         @       ASPMX.L.GOOGLE.COM
5         @       ALT1.ASPMX.L.GOOGLE.COM
5         @       ALT2.ASPMX.L.GOOGLE.COM
10        @       ALT3.ASPMX.L.GOOGLE.COM
10        @       ALT4.ASPMX.L.GOOGLE.COM
```

### Zoho Mail:
```
Priority  Host    Value
10        @       mx.zoho.com
20        @       mx2.zoho.com
50        @       mx3.zoho.com
```

- [ ] MX records created in DNS
- [ ] Verified with: `dig dealix.sa MX`
- [ ] Propagation confirmed (allow 1-24 hours)

---

## Step 3: Set Up SPF Record

- [ ] Create TXT record at DNS:

**Google Workspace + SendGrid:**
```
Type: TXT
Name: @
Value: v=spf1 include:_spf.google.com include:sendgrid.net ~all
```

**Zoho + SendGrid:**
```
Type: TXT
Name: @
Value: v=spf1 include:zoho.com include:sendgrid.net ~all
```

- [ ] Verified with: `dig dealix.sa TXT | grep spf`
- [ ] Only ONE SPF record exists (multiple will break delivery)

---

## Step 4: Set Up DKIM

- [ ] Generate DKIM key pair in email provider admin panel
- [ ] Create TXT record:
  ```
  Type: TXT
  Name: <selector>._domainkey    (e.g., google._domainkey)
  Value: <DKIM_PUBLIC_KEY_FROM_PROVIDER>
  TTL: 3600
  ```
- [ ] If using SendGrid, also add SendGrid DKIM records (CNAME-based):
  ```
  Type: CNAME
  Name: s1._domainkey
  Value: s1.domainkey.uXXXXXX.wlXXX.sendgrid.net
  ```
- [ ] Verified DKIM shows "Pass" in email provider admin
- [ ] Send test email and check headers for `dkim=pass`

---

## Step 5: Set Up DMARC

- [ ] Create TXT record:
  ```
  Type: TXT
  Name: _dmarc
  Value: v=DMARC1; p=none; rua=mailto:dmarc@dealix.sa; ruf=mailto:dmarc@dealix.sa; fo=1; pct=100
  ```
- [ ] Start with `p=none` (monitor only)
- [ ] After 2 weeks of clean reports, upgrade to `p=quarantine`
- [ ] After 2 more weeks, upgrade to `p=reject`
- [ ] Verified with: `dig _dmarc.dealix.sa TXT`

---

## Step 6: Create Email Accounts / إنشاء حسابات البريد

| Account | Purpose / الغرض | Notes |
|---|---|---|
| `info@dealix.sa` | General inquiries / استفسارات عامة | Public-facing, on website |
| `support@dealix.sa` | Customer support / الدعم الفني | Ticketing system integration |
| `sales@dealix.sa` | Sales inquiries / المبيعات | For affiliate and client comms |
| `noreply@dealix.sa` | System notifications / إشعارات النظام | Transactional emails only |
| `privacy@dealix.sa` | PDPL/privacy requests / طلبات الخصوصية | Required by Saudi PDPL |
| `dmarc@dealix.sa` | DMARC reports / تقارير DMARC | Receives aggregate reports |
| `admin@dealix.sa` | Admin access / وصول المدير | Internal use only |

- [ ] All accounts created
- [ ] Passwords stored securely (password manager, not plain text)
- [ ] 2FA enabled on all accounts

---

## Step 7: Update .env SMTP Settings

```bash
# For Google Workspace SMTP:
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@dealix.sa
SMTP_PASSWORD=<APP_PASSWORD>     # Generate App Password in Google, not account password
EMAIL_FROM_NAME=Dealix
EMAIL_FROM_ADDRESS=noreply@dealix.sa

# For SendGrid (transactional):
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx
```

- [ ] `.env` updated with real SMTP credentials
- [ ] App Password generated (not regular password) if using Google
- [ ] SendGrid API key created with restricted permissions (Mail Send only)
- [ ] Backend service restarted after `.env` changes

---

## Step 8: Test Send/Receive / اختبار الإرسال والاستقبال

### Sending Tests:
- [ ] Send from `noreply@dealix.sa` to a Gmail address — check arrives in Inbox (not Spam)
- [ ] Send from `noreply@dealix.sa` to an Outlook address — check arrives in Inbox
- [ ] Check email headers for:
  - `spf=pass`
  - `dkim=pass`
  - `dmarc=pass`
- [ ] Verify sender name displays as "Dealix" (not raw email address)

### Receiving Tests:
- [ ] Send from external Gmail to `info@dealix.sa` — confirm delivery
- [ ] Send from external Gmail to `support@dealix.sa` — confirm delivery
- [ ] Reply from `support@dealix.sa` — confirm reply delivery

### Deliverability Check:
- [ ] Test with [mail-tester.com](https://www.mail-tester.com/) — aim for 9+/10 score
- [ ] Test with [mxtoolbox.com](https://mxtoolbox.com/) — no blacklist hits

---

## Step 9: Configure Email Templates / إعداد قوالب البريد

| Template | Trigger | Language |
|---|---|---|
| Welcome Email | New affiliate registration | Arabic |
| Email Verification | Account creation | Arabic |
| Password Reset | Forgot password request | Arabic |
| New Lead Notification | Lead assigned to affiliate | Arabic |
| Deal Stage Update | Deal moves to new stage | Arabic |
| Commission Earned | Deal closed, commission calculated | Arabic |
| Weekly Summary | Every Sunday 9 AM Riyadh | Arabic |
| Payment Confirmation | Commission paid | Arabic |

- [ ] All templates created with Arabic RTL support
- [ ] Templates use inline CSS (not external stylesheets)
- [ ] Templates tested in Gmail, Outlook, Apple Mail
- [ ] Unsubscribe link included in marketing emails
- [ ] Physical address included in footer (Saudi regulation)

---

## Troubleshooting / استكشاف الأخطاء

| Problem | Likely Cause | Fix |
|---|---|---|
| Emails go to spam | Missing SPF/DKIM/DMARC | Configure all three records |
| "550 Authentication required" | Wrong SMTP credentials | Check username/password, use App Password |
| "Connection refused on port 587" | Firewall blocking | Open port 587 outbound on server |
| Emails not received | MX records wrong | Verify MX with `dig` command |
| DKIM fails | Wrong selector or key | Regenerate in provider, update DNS |

---

> عند اكتمال جميع الخطوات، يجب أن يحقق البريد الإلكتروني نقاط 9+ على mail-tester.com
> When all steps are complete, email should score 9+/10 on mail-tester.com
