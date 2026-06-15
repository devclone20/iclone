#!/bin/bash
# iCLONE — DigitalOcean Droplet Setup (v2 — iCLONE + VEGETA topology)
# Run once as root on a fresh Ubuntu 22.04/24.04 droplet:
#   bash setup.sh
set -euo pipefail

ICLONE_USER="iclone"
ICLONE_DIR="/opt/iclone"
LOG_DIR="/var/log/iclone"
NODE_VERSION="20"
PYTHON_VERSION="3.12"

echo "================================================"
echo "  iCLONE Cloud Setup — Ubuntu (1GB droplet)"
echo "================================================"

# ── Swap (CRITICAL on 1GB: npm + pip OOM without it) ─
if ! swapon --show | grep -q '/swapfile'; then
    echo "── Creating 2GB swap (prevents OOM on 1GB droplet) ──"
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
    sysctl -w vm.swappiness=10
    grep -q 'vm.swappiness' /etc/sysctl.conf || echo 'vm.swappiness=10' >> /etc/sysctl.conf
    echo "✓ Swap active"
fi

# ── System packages ──────────────────────────────────
apt-get update -qq
apt-get install -y -qq \
    curl wget git build-essential \
    software-properties-common \
    ufw fail2ban rsync \
    python3-pip python3-venv

# ── Python 3.12 ──────────────────────────────────────
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update -qq
apt-get install -y -qq python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev

# ── Node.js 20 LTS + acp-cli ─────────────────────────
curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
apt-get install -y -qq nodejs
npm install -g @virtuals-protocol/acp-cli@latest
echo "acp version: $(acp --version 2>/dev/null || echo 'installed')"

# ── Dedicated user ───────────────────────────────────
id -u ${ICLONE_USER} &>/dev/null || useradd -m -s /bin/bash ${ICLONE_USER}

# ── Directories ──────────────────────────────────────
mkdir -p ${ICLONE_DIR} ${LOG_DIR}
mkdir -p /home/${ICLONE_USER}/.config/acp-iclone/acp
mkdir -p /home/${ICLONE_USER}/.config/acp-vegeta/acp
mkdir -p "/home/${ICLONE_USER}/.local/share"
chown -R ${ICLONE_USER}:${ICLONE_USER} ${ICLONE_DIR} ${LOG_DIR} /home/${ICLONE_USER}/.config

# ── Firewall (outbound-only app; only SSH inbound) ───
ufw --force enable
ufw allow ssh
ufw default deny incoming
ufw default allow outgoing

# ── fail2ban (SSH brute-force protection) ────────────
systemctl enable fail2ban
systemctl start fail2ban

echo ""
echo "✓ System setup complete (swap + python3.12 + node20 + acp-cli + ufw + fail2ban)."
echo ""
echo "Next (from the Mac):"
echo "  bash ops/do/deploy.sh <DROPLET_IP>"
echo "  bash ops/do/migrate-tokens.sh <DROPLET_IP>"
