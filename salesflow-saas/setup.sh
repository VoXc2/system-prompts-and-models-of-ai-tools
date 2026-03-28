#!/bin/bash
set -e

echo "=============================="
echo "  Dealix - Setup Script"
echo "=============================="

# Step 1: Clone the repo
echo ""
echo "[1/5] Cloning repository..."
if [ -d "/root/salesflow-project" ]; then
    echo "Directory exists, pulling latest..."
    cd /root/salesflow-project
    git pull origin claude/fix-settings-table-a1bXv
else
    git clone -b claude/fix-settings-table-a1bXv https://github.com/VoXc2/system-prompts-and-models-of-ai-tools.git /root/salesflow-project
fi

cd /root/salesflow-project/salesflow-saas

# Step 2: Create .env file
echo ""
echo "[2/5] Creating .env file..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)

cat > .env << ENVEOF
DB_PASSWORD=Dealix2024SecureDB!
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=postgresql+asyncpg://salesflow:Dealix2024SecureDB!@db:5432/salesflow
REDIS_URL=redis://redis:6379/0
WHATSAPP_API_TOKEN=EAAP9TPQ1z2QBREZCHEg2RzJm1esQblTR8mqm1klCkyZA2qP8ZCyGZAvqZCdYtyGMtWq3ifVZB7OisZClPtQOOS0kF6nYmreQpntxVxDXkE4F8oCyfWB61ZCWlSaVEWRI9U2MuyCSz6MWcWa3GoWMcItF9dFHVSFO72LaLkGy1N6KFOhOd19fNefvZCtqH8xn9RZA5vWHWZB4YTQ9jHPEkb7e80TEjEPLIAw1ofIRZCPP
WHATSAPP_PHONE_NUMBER_ID=1068891919637293
WHATSAPP_BUSINESS_ACCOUNT_ID=2371037243416065
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
UNIFONIC_APP_SID=
UNIFONIC_SENDER_ID=Dealix
ENVEOF

echo ".env file created!"

# Step 3: Create WhatsApp message templates
echo ""
echo "[3/5] Creating WhatsApp message templates..."

WA_TOKEN="EAAP9TPQ1z2QBREZCHEg2RzJm1esQblTR8mqm1klCkyZA2qP8ZCyGZAvqZCdYtyGMtWq3ifVZB7OisZClPtQOOS0kF6nYmreQpntxVxDXkE4F8oCyfWB61ZCWlSaVEWRI9U2MuyCSz6MWcWa3GoWMcItF9dFHVSFO72LaLkGy1N6KFOhOd19fNefvZCtqH8xn9RZA5vWHWZB4YTQ9jHPEkb7e80TEjEPLIAw1ofIRZCPP"
WA_ACCOUNT="2371037243416065"
WA_URL="https://graph.facebook.com/v22.0/${WA_ACCOUNT}/message_templates"

echo "  Creating welcome template..."
curl -s -X POST "$WA_URL" \
  -H "Authorization: Bearer $WA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"dealix_welcome","category":"MARKETING","language":"ar","components":[{"type":"BODY","text":"\u0645\u0631\u062d\u0628\u0627\u064b {{1}}! \u0634\u0643\u0631\u0627\u064b \u0644\u062a\u0648\u0627\u0635\u0644\u0643 \u0645\u0639 Dealix. \u0643\u064a\u0641 \u0646\u0642\u062f\u0631 \u0646\u0633\u0627\u0639\u062f\u0643 \u0627\u0644\u064a\u0648\u0645\u061f","example":{"body_text":[["\u0623\u062d\u0645\u062f"]]}}]}' && echo " OK" || echo " SKIP"

echo "  Creating follow-up template..."
curl -s -X POST "$WA_URL" \
  -H "Authorization: Bearer $WA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"dealix_followup","category":"MARKETING","language":"ar","components":[{"type":"BODY","text":"\u0645\u0631\u062d\u0628\u0627\u064b {{1}}\u060c \u062a\u0648\u0627\u0635\u0644\u0646\u0627 \u0645\u0639\u0643 \u0633\u0627\u0628\u0642\u0627\u064b \u0628\u062e\u0635\u0648\u0635 {{2}}. \u0647\u0644 \u0639\u0646\u062f\u0643 \u0623\u064a \u0627\u0633\u062a\u0641\u0633\u0627\u0631\u061f","example":{"body_text":[["\u0623\u062d\u0645\u062f","\u062e\u062f\u0645\u0627\u062a\u0646\u0627"]]}}]}' && echo " OK" || echo " SKIP"

echo "  Creating offer template..."
curl -s -X POST "$WA_URL" \
  -H "Authorization: Bearer $WA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"dealix_offer","category":"MARKETING","language":"ar","components":[{"type":"BODY","text":"\u0645\u0631\u062d\u0628\u0627\u064b {{1}}! \u0639\u0646\u062f\u0646\u0627 \u0639\u0631\u0636 \u062e\u0627\u0635 \u0644\u0643: {{2}}. \u0627\u0644\u0639\u0631\u0636 \u0633\u0627\u0631\u064a \u062d\u062a\u0649 {{3}}.","example":{"body_text":[["\u0623\u062d\u0645\u062f","\u062e\u0635\u0645 20%","\u0646\u0647\u0627\u064a\u0629 \u0627\u0644\u0634\u0647\u0631"]]}}]}' && echo " OK" || echo " SKIP"

echo "  Creating appointment template..."
curl -s -X POST "$WA_URL" \
  -H "Authorization: Bearer $WA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"dealix_appointment","category":"UTILITY","language":"ar","components":[{"type":"BODY","text":"\u062a\u0630\u0643\u064a\u0631: \u0639\u0646\u062f\u0643 \u0645\u0648\u0639\u062f \u064a\u0648\u0645 {{1}} \u0627\u0644\u0633\u0627\u0639\u0629 {{2}}. \u0646\u062a\u0637\u0644\u0639 \u0644\u062e\u062f\u0645\u062a\u0643!","example":{"body_text":[["\u0627\u0644\u0623\u062d\u062f","10:00 \u0635\u0628\u0627\u062d\u0627\u064b"]]}}]}' && echo " OK" || echo " SKIP"

# Step 4: Check Docker
echo ""
echo "[4/5] Checking Docker..."
if command -v docker &> /dev/null; then
    echo "Docker found: $(docker --version)"
    if command -v docker compose &> /dev/null; then
        echo "Docker Compose found"
    else
        echo "Installing Docker Compose plugin..."
        apt-get update -qq && apt-get install -y -qq docker-compose-plugin 2>/dev/null || true
    fi
else
    echo "Docker not found. Installing..."
    curl -fsSL https://get.docker.com | sh
fi

# Step 5: Build and start
echo ""
echo "[5/5] Building and starting services..."
cd /root/salesflow-project/salesflow-saas
docker compose up -d --build 2>/dev/null || docker-compose up -d --build 2>/dev/null || echo "Docker build will be done manually"

echo ""
echo "=============================="
echo "  Setup Complete!"
echo "=============================="
echo ""
echo "Phone Number ID: 1068891919637293"
echo "WhatsApp Account: 2371037243416065"
echo "Server: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Test API: curl http://localhost:8000/api/v1/health"
echo "=============================="
