#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
# ssh_harden.sh — قوالب تقسية SSH + fail2ban + UFW
# USAGE (as root):  bash scripts/infra/ssh_harden.sh
# ─────────────────────────────────────────────────────
set -euo pipefail

SSHD=/etc/ssh/sshd_config
STAMP=$(date +%Y%m%d%H%M%S)

if [[ $EUID -ne 0 ]]; then
  echo "✗ Run as root" >&2
  exit 1
fi

cp "$SSHD" "${SSHD}.bak.${STAMP}"
echo "✓ Backup: ${SSHD}.bak.${STAMP}"

# Apply hardening idempotently
declare -A CFG=(
  [Port]="2222"
  [PermitRootLogin]="prohibit-password"
  [PasswordAuthentication]="no"
  [PubkeyAuthentication]="yes"
  [ChallengeResponseAuthentication]="no"
  [UsePAM]="yes"
  [X11Forwarding]="no"
  [PermitEmptyPasswords]="no"
  [ClientAliveInterval]="300"
  [ClientAliveCountMax]="2"
  [MaxAuthTries]="4"
  [LoginGraceTime]="30"
  [AllowTcpForwarding]="no"
  [Protocol]="2"
)

for key in "${!CFG[@]}"; do
  val="${CFG[$key]}"
  if grep -qE "^\s*#?\s*${key}\s+" "$SSHD"; then
    sed -i "s|^\s*#\?\s*${key}\s\+.*|${key} ${val}|" "$SSHD"
  else
    echo "${key} ${val}" >> "$SSHD"
  fi
done

echo "✓ sshd_config updated"
sshd -t  # validate
echo "✓ sshd_config syntax OK"

# Install fail2ban if missing
if ! command -v fail2ban-client >/dev/null; then
  apt-get update -qq
  apt-get install -y -qq fail2ban
fi

cat > /etc/fail2ban/jail.d/ssh.local <<EOF
[sshd]
enabled = true
port    = 2222
maxretry = 5
findtime = 10m
bantime  = 1h
EOF

systemctl enable --now fail2ban
systemctl restart fail2ban
echo "✓ fail2ban enabled"

# UFW
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 2222/tcp comment 'SSH'
ufw allow 80/tcp   comment 'HTTP'
ufw allow 443/tcp  comment 'HTTPS'
ufw --force enable
echo "✓ UFW enabled (2222/80/443)"

# Restart sshd (careful! — keep current session alive)
systemctl restart ssh || systemctl restart sshd
echo ""
echo "✅ SSH hardened on port 2222."
echo "   Open a NEW session on :2222 BEFORE closing this one to verify."
