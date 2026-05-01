# Deployment Guide

## 🐳 Docker (recommended for most teams)

### Single container (app only)

```bash
docker build -t ai-company-saudi:2.0.0 .
docker run -d \
  --name ai-company \
  --env-file .env \
  -p 8000:8000 \
  --restart unless-stopped \
  ai-company-saudi:2.0.0
```

### Full stack with docker-compose

```bash
make docker-up
# app + PostgreSQL 16 + Redis 7 + MongoDB 7
```

Stop:
```bash
make docker-down
```

Logs:
```bash
make docker-logs
```

---

## ☁️ Production VPS (bare metal / DigitalOcean / Hetzner / AWS EC2)

### 1. Prep the server

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install -y python3.12 python3.12-venv git nginx postgresql redis
```

### 2. Clone & configure

```bash
git clone https://github.com/YOUR-ORG/ai-company-saudi.git /opt/ai-company
cd /opt/ai-company

python3.12 -m venv venv
source venv/bin/activate
pip install -e .

cp .env.example .env
# edit .env with your secrets
```

### 3. Systemd service

`/etc/systemd/system/ai-company.service`:

```ini
[Unit]
Description=AI Company Saudi API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=appuser
WorkingDirectory=/opt/ai-company
Environment="PATH=/opt/ai-company/venv/bin"
EnvironmentFile=/opt/ai-company/.env
ExecStart=/opt/ai-company/venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ai-company
sudo systemctl status ai-company
```

### 4. nginx reverse proxy

`/etc/nginx/sites-available/ai-company`:

```nginx
server {
    listen 80;
    server_name api.ai-company.sa;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Enable + TLS:
```bash
sudo ln -s /etc/nginx/sites-available/ai-company /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Let's Encrypt (certbot)
sudo certbot --nginx -d api.ai-company.sa
```

### 5. Database init

```bash
sudo -u postgres psql -c "CREATE USER ai_user WITH PASSWORD 'strong-password';"
sudo -u postgres psql -c "CREATE DATABASE ai_company OWNER ai_user;"
make db-init
```

---

## ☁️ Kubernetes (advanced)

Basic Deployment + Service manifests are available in `docs/k8s/` (coming). Use the published Docker image from GHCR:

```
ghcr.io/YOUR-ORG/ai-company-saudi:v2.0.0
```

Essentials:
- Use a **Secret** for `.env` contents
- Use a **ConfigMap** for non-sensitive settings
- Set up liveness (`/live`), readiness (`/ready`), and startup probes
- Request 500m CPU / 512Mi memory; limit 2 CPU / 2Gi memory

---

## ☁️ Managed Python platforms

### Railway / Render / Fly.io

All three support auto-deploy from GitHub. Steps:
1. Create a new app, connect this repo.
2. Add all env vars from `.env.example` as secrets.
3. Set start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 2`.
4. Attach a managed PostgreSQL add-on, copy its URL to `DATABASE_URL`.

---

## 📊 Health monitoring

Every deployment should configure:
- **Uptime checks** against `/health` (30s interval)
- **Alerts** on:
  - `/health` returning non-200 for > 2 minutes
  - Error rate > 1% over 5 minutes
  - p95 latency > 10s for > 5 minutes
- **Log aggregation** — ship structlog JSON to Grafana Loki, Datadog, or Elastic

---

## 🔐 Production hardening checklist

- [ ] `.env` has real keys, `APP_ENV=production`, `APP_DEBUG=false`
- [ ] `APP_SECRET_KEY` is a 64-char random string
- [ ] `CORS_ORIGINS` restricted to your actual domains
- [ ] Rate limiting in nginx / Cloudflare
- [ ] TLS certificate valid
- [ ] Database credentials strong + rotated quarterly
- [ ] Backup schedule for Postgres (daily, 30-day retention)
- [ ] Dependabot alerts enabled on GitHub
- [ ] Branch protection on `main`
- [ ] Required reviews on PRs
- [ ] No `.env` committed (run `gitleaks detect --source .`)
