#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
# ssl_certbot.sh — إصدار شهادة SSL لـ api.dealix.sa
# USAGE:  bash scripts/infra/ssl_certbot.sh api.dealix.sa admin@dealix.sa
# ─────────────────────────────────────────────────────
set -euo pipefail

DOMAIN="${1:-api.dealix.sa}"
EMAIL="${2:-admin@dealix.sa}"

if [[ $EUID -ne 0 ]]; then
  echo "✗ Run as root" >&2
  exit 1
fi

apt-get update -qq
apt-get install -y -qq certbot python3-certbot-nginx nginx

# Minimal nginx vhost if missing
if [[ ! -f /etc/nginx/sites-available/dealix-api ]]; then
  cat > /etc/nginx/sites-available/dealix-api <<EOF
server {
    listen 80;
    server_name ${DOMAIN};
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
  ln -sf /etc/nginx/sites-available/dealix-api /etc/nginx/sites-enabled/dealix-api
  nginx -t
  systemctl reload nginx
fi

certbot --nginx --non-interactive --agree-tos -m "${EMAIL}" -d "${DOMAIN}" --redirect
systemctl enable --now certbot.timer
echo "✅ SSL issued for ${DOMAIN}. Auto-renewal via certbot.timer."
