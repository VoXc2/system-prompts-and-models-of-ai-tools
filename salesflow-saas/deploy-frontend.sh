#!/usr/bin/env bash
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────
REPO_URL="https://github.com/VoXc2/system-prompts-and-models-of-ai-tools.git"
DEPLOY_DIR="/root/salesflow-frontend"
FRONTEND_REL="salesflow-saas/frontend"
CONTAINER_NAME="salesflow-frontend"
IMAGE_NAME="salesflow-frontend:latest"
PORT=3000

echo "========================================="
echo "  Dealix Frontend — Deploy Script"
echo "========================================="

# ── 1. Clone or pull the repository ────────────────────────────
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "[*] Repository exists, pulling latest changes..."
    cd "$DEPLOY_DIR"
    git fetch --all
    git checkout claude/fix-settings-table-a1bXv 2>/dev/null || git checkout -b claude/fix-settings-table-a1bXv origin/claude/fix-settings-table-a1bXv
    git reset --hard origin/claude/fix-settings-table-a1bXv
else
    echo "[*] Cloning repository..."
    mkdir -p "$DEPLOY_DIR"
    git clone -b claude/fix-settings-table-a1bXv "$REPO_URL" "$DEPLOY_DIR"
fi

cd "$DEPLOY_DIR/$FRONTEND_REL"
echo "[*] Working directory: $(pwd)"

# ── 2. Build Docker image ─────────────────────────────────────
echo "[*] Building Docker image..."
docker build -t "$IMAGE_NAME" .

# ── 3. Stop and remove existing container if running ───────────
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[*] Stopping existing container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# ── 4. Run new container ──────────────────────────────────────
echo "[*] Starting container on port $PORT..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p "$PORT:3000" \
    -e NEXT_PUBLIC_API_URL="http://46.225.123.110:9000/api/v1" \
    "$IMAGE_NAME"

# ── 5. Open firewall port if ufw is active ────────────────────
if command -v ufw &>/dev/null && ufw status | grep -q "active"; then
    if ! ufw status | grep -q "$PORT/tcp"; then
        echo "[*] Opening firewall port $PORT..."
        ufw allow "$PORT/tcp"
    else
        echo "[*] Firewall port $PORT already open."
    fi
else
    echo "[*] ufw not active — skipping firewall configuration."
    echo "    If using firewalld: firewall-cmd --permanent --add-port=$PORT/tcp && firewall-cmd --reload"
fi

# ── 6. Prune old images ──────────────────────────────────────
echo "[*] Pruning dangling images..."
docker image prune -f

# ── 7. Health check ───────────────────────────────────────────
echo "[*] Waiting for container to start..."
sleep 3
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[+] Container '$CONTAINER_NAME' is running."
    echo "[+] Frontend available at: http://$(hostname -I | awk '{print $1}'):$PORT"
else
    echo "[-] ERROR: Container failed to start. Check logs:"
    echo "    docker logs $CONTAINER_NAME"
    exit 1
fi

echo "========================================="
echo "  Deployment complete!"
echo "========================================="
