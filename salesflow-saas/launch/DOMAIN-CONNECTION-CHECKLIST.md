# Dealix (ديل اي اكس) — Domain Connection Checklist

> خطوات ربط النطاق بالكامل — من الشراء إلى التشغيل
> Last updated: 2026-03-31

---

## Step 1: Purchase Domain / شراء النطاق

- [ ] Choose domain name:
  - **Primary:** `dealix.sa` (requires Saudi Commercial Registration / سجل تجاري)
  - **Alternative:** `dealix.com` or `dealix.com.sa`
- [ ] Purchase from registrar:
  - For `.sa`: [nic.sa](https://nic.sa) or authorized registrars (SaudiNIC)
  - For `.com`: Namecheap, Cloudflare Registrar, GoDaddy
- [ ] Verify domain ownership via registrar email confirmation
- [ ] Enable domain privacy protection (WHOIS privacy)
- [ ] Enable auto-renewal to prevent accidental expiration

---

## Step 2: DNS A Record / سجل A

- [ ] Log in to DNS management panel (registrar or Cloudflare)
- [ ] Create A record:
  ```
  Type: A
  Name: @
  Value: <SERVER_IP_ADDRESS>
  TTL: 300 (5 minutes initially, increase to 3600 after verification)
  ```
- [ ] Verify: `dig dealix.sa A` should return server IP

---

## Step 3: CNAME for www / سجل CNAME

- [ ] Create CNAME record:
  ```
  Type: CNAME
  Name: www
  Value: dealix.sa
  TTL: 300
  ```
- [ ] Verify: `dig www.dealix.sa CNAME` should return `dealix.sa`

---

## Step 4: MX Records for Email / سجلات البريد

- [ ] Create MX records based on email provider:

  **Google Workspace:**
  ```
  Priority 1:  ASPMX.L.GOOGLE.COM
  Priority 5:  ALT1.ASPMX.L.GOOGLE.COM
  Priority 5:  ALT2.ASPMX.L.GOOGLE.COM
  Priority 10: ALT3.ASPMX.L.GOOGLE.COM
  Priority 10: ALT4.ASPMX.L.GOOGLE.COM
  ```

  **Zoho Mail:**
  ```
  Priority 10: mx.zoho.com
  Priority 20: mx2.zoho.com
  Priority 50: mx3.zoho.com
  ```

- [ ] Verify: `dig dealix.sa MX` should return configured records

---

## Step 5: SPF Record

- [ ] Create TXT record for SPF:

  **Google Workspace:**
  ```
  Type: TXT
  Name: @
  Value: v=spf1 include:_spf.google.com ~all
  ```

  **Zoho Mail:**
  ```
  Type: TXT
  Name: @
  Value: v=spf1 include:zoho.com ~all
  ```

  **With Unifonic SMS (append before ~all):**
  ```
  v=spf1 include:_spf.google.com include:unifonic.com ~all
  ```

- [ ] Verify: `dig dealix.sa TXT` should show SPF record

---

## Step 6: DKIM Record

- [ ] Generate DKIM key in email provider admin panel
- [ ] Create TXT record:
  ```
  Type: TXT
  Name: google._domainkey (or as provided by email provider)
  Value: <DKIM_KEY_FROM_PROVIDER>
  TTL: 3600
  ```
- [ ] Verify in email provider admin panel (shows "authenticated")

---

## Step 7: DMARC Record

- [ ] Create TXT record for DMARC:
  ```
  Type: TXT
  Name: _dmarc
  Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@dealix.sa; ruf=mailto:dmarc@dealix.sa; fo=1
  ```
  - Start with `p=none` for monitoring, then move to `p=quarantine`, then `p=reject`
- [ ] Verify: `dig _dmarc.dealix.sa TXT`

---

## Step 8: SSL Certificate

### Option A: Let's Encrypt (Direct)
- [ ] Install Certbot: `sudo apt install certbot python3-certbot-nginx`
- [ ] Generate certificate:
  ```bash
  sudo certbot --nginx -d dealix.sa -d www.dealix.sa
  ```
- [ ] Verify auto-renewal: `sudo certbot renew --dry-run`
- [ ] Add cron job: `0 0 1 * * certbot renew --quiet`

### Option B: Cloudflare (Recommended)
- [ ] Add site to Cloudflare
- [ ] Change nameservers at registrar to Cloudflare's
- [ ] Enable "Full (Strict)" SSL mode in Cloudflare
- [ ] Enable "Always Use HTTPS"
- [ ] Enable "Automatic HTTPS Rewrites"
- [ ] Generate Origin Certificate for server (15-year validity)

---

## Step 9: Verify Propagation / التحقق من الانتشار

- [ ] Check with online tool: [whatsmydns.net](https://www.whatsmydns.net/)
- [ ] Verify A record propagation globally
- [ ] Verify MX record propagation
- [ ] Test HTTPS access: `curl -I https://dealix.sa`
- [ ] Test www redirect: `curl -I https://www.dealix.sa`
- [ ] Test email delivery: send test from external to info@dealix.sa

> ملاحظة: الانتشار قد يستغرق 24-48 ساعة. عادةً يكتمل خلال 1-4 ساعات.
> Note: Propagation can take 24-48 hours but usually completes within 1-4 hours.

---

## Step 10: Update Nginx Configuration

- [ ] Update `/etc/nginx/sites-available/dealix`:
  ```nginx
  server {
      listen 80;
      server_name dealix.sa www.dealix.sa;
      return 301 https://$server_name$request_uri;
  }

  server {
      listen 443 ssl http2;
      server_name dealix.sa www.dealix.sa;

      ssl_certificate /etc/letsencrypt/live/dealix.sa/fullchain.pem;
      ssl_certificate_key /etc/letsencrypt/live/dealix.sa/privkey.pem;

      # Frontend
      location / {
          proxy_pass http://localhost:3000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }

      # Backend API
      location /api/ {
          proxy_pass http://localhost:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```
- [ ] Test config: `sudo nginx -t`
- [ ] Reload: `sudo systemctl reload nginx`

---

## Step 11: Update .env

- [ ] Update production `.env`:
  ```
  API_URL=https://dealix.sa/api
  FRONTEND_URL=https://dealix.sa
  ```
- [ ] Restart backend services
- [ ] Verify health check: `curl https://dealix.sa/api/v1/health`

---

## DNS Records Summary / ملخص سجلات DNS

| Type | Name | Value | TTL |
|---|---|---|---|
| A | @ | `<SERVER_IP>` | 3600 |
| CNAME | www | dealix.sa | 3600 |
| MX | @ | (per email provider) | 3600 |
| TXT | @ | SPF record | 3600 |
| TXT | google._domainkey | DKIM key | 3600 |
| TXT | _dmarc | DMARC policy | 3600 |
