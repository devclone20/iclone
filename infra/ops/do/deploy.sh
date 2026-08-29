#!/bin/bash
# iCLONE — Deploy code + config from Mac to DigitalOcean (v2)
# Usage: bash ops/do/deploy.sh <droplet-ip>
set -euo pipefail

DROPLET_IP="${1:?Usage: deploy.sh <droplet-ip>}"
REMOTE_DIR="/opt/iclone"
LOCAL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
HOME_LOCAL="${HOME}"

echo "================================================"
echo "  iCLONE Deploy → ${DROPLET_IP}"
echo "================================================"

# ── 1. Remote dir ─────────────────────────────────────
ssh root@${DROPLET_IP} "mkdir -p ${REMOTE_DIR} && chown -R iclone:iclone ${REMOTE_DIR}"

# ── 2. Code (no venv, no caches, no Mac launchd) ──────
echo "── Syncing code... ──────────────────────────────"
rsync -avz --delete \
    --exclude='.git' \
    --exclude='venv312' --exclude='.venv312' --exclude='venv' \
    --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='ops/launchd' \
    --exclude='node_modules' \
    "${LOCAL_DIR}/" "root@${DROPLET_IP}:${REMOTE_DIR}/"
echo "✓ Code synced"

# ── 3. Secrets: .env (repo) + .env.local (HOME, real keys) ─
if [ -f "${LOCAL_DIR}/.env" ]; then
    scp -q "${LOCAL_DIR}/.env" "root@${DROPLET_IP}:${REMOTE_DIR}/.env"
fi
if [ -f "${HOME_LOCAL}/.env.local" ]; then
    scp -q "${HOME_LOCAL}/.env.local" "root@${DROPLET_IP}:/home/iclone/.env.local"
    echo "✓ ~/.env.local copied (ANTHROPIC_API_KEY)"
else
    echo "⚠ ~/.env.local not found — ANTHROPIC_API_KEY must be set in ${REMOTE_DIR}/.env"
fi

# ── 4. ACP agent metadata (config.json for both agents) ─
for agent in acp-iclone acp-vegeta; do
    SRC="${HOME_LOCAL}/.config/${agent}/acp/config.json"
    if [ -f "${SRC}" ]; then
        ssh root@${DROPLET_IP} "mkdir -p /home/iclone/.config/${agent}/acp"
        scp -q "${SRC}" "root@${DROPLET_IP}:/home/iclone/.config/${agent}/acp/config.json"
        echo "✓ ${agent}/config.json copied"
    else
        echo "⚠ ${SRC} missing"
    fi
done

# ── 5. Signer keys (P256 — required for deny-all signer) ─
SIGNER="${HOME_LOCAL}/Library/Application Support/acp-cli/signer-keys.json"
if [ -f "${SIGNER}" ]; then
    ssh root@${DROPLET_IP} "mkdir -p '/home/iclone/.config/acp-cli' '/home/iclone/.local/share/acp-cli'"
    # acp-cli on Linux reads signer keys from XDG dirs; place in both likely locations.
    scp -q "${SIGNER}" "root@${DROPLET_IP}:/home/iclone/.config/acp-cli/signer-keys.json"
    scp -q "${SIGNER}" "root@${DROPLET_IP}:/home/iclone/.local/share/acp-cli/signer-keys.json"
    echo "✓ signer-keys.json copied"
else
    echo "⚠ signer-keys.json not found"
fi

# ── 6. Ownership + perms ──────────────────────────────
ssh root@${DROPLET_IP} bash -s <<'REMOTE'
chown -R iclone:iclone /opt/iclone /home/iclone/.config /home/iclone/.local /home/iclone/.env.local 2>/dev/null || true
chmod 600 /opt/iclone/.env /home/iclone/.env.local 2>/dev/null || true
find /home/iclone/.config -name config.json -exec chmod 600 {} \; 2>/dev/null || true
find /home/iclone -name 'signer-keys.json' -exec chmod 600 {} \; 2>/dev/null || true
REMOTE

echo ""
echo "✓ Deploy complete."
echo ""
echo "NEXT:"
echo "  1. (first deploy) python deps:"
echo "     ssh iclone@${DROPLET_IP} 'cd /opt/iclone && python3.12 -m venv venv312 && venv312/bin/pip install -U pip && venv312/bin/pip install -r ops/do/requirements.txt'"
echo "  2. Migrate ACP tokens (from Mac keychain):"
echo "     bash ops/do/migrate-tokens.sh ${DROPLET_IP}"
echo "  3. Start services:"
echo "     ssh root@${DROPLET_IP} 'bash /opt/iclone/ops/do/start-services.sh'"
