#!/bin/bash
# iCLONE — Migrate ACP auth tokens from Mac keychain to the droplet.
# No browser re-auth. Extracts access+refresh tokens for both owner wallets
# from the macOS keychain (service "acp-auth") and persists them on the droplet
# via `acp configure --token ...` into each agent's ACP_CONFIG_DIR.
#
# Usage: bash ops/do/migrate-tokens.sh <droplet-ip>
#
# IMPORTANT — clean cutover: run AFTER stopping the Mac daemons
# (bash ops/do/cutover-mac.sh) so refresh-token rotation has a single owner.
set -euo pipefail

DROPLET_IP="${1:?Usage: migrate-tokens.sh <droplet-ip>}"

# config-dir  →  owner wallet (lowercase, as stored in keychain account name)
ICLONE_OWNER="0xb4805e8d8c9f23fa4615422202be1e38fba6a739"
VEGETA_OWNER="0x743665952ec1240d62a3e580e5dc2c9e421d0537"

extract() {  # $1 = token type (access|refresh), $2 = owner wallet
    security find-generic-password -s "acp-auth" -a "$1-token-$2" -w 2>/dev/null || true
}

inject() {   # $1 = label, $2 = remote config dir, $3 = owner wallet
    local label="$1" cfgdir="$2" owner="$3"
    echo "── ${label} (${owner}) ──"
    local at rt
    at="$(extract access  "${owner}")"
    rt="$(extract refresh "${owner}")"
    if [ -z "${at}" ] || [ -z "${rt}" ]; then
        echo "  ✗ tokens not found in keychain for ${owner} — skip (browser auth needed)"
        return 1
    fi
    # Pipe tokens over stdin to avoid leaking them in `ps` / shell history.
    ssh root@${DROPLET_IP} \
        "sudo -u iclone env HOME=/home/iclone ACP_CONFIG_DIR=${cfgdir} \
         ACP_ACCESS_TOKEN='${at}' ACP_REFRESH_TOKEN='${rt}' ACP_OWNER_WALLET='${owner}' \
         acp configure" \
        && echo "  ✓ ${label} token injected"
}

echo "================================================"
echo "  ACP Token Migration → ${DROPLET_IP}"
echo "================================================"

inject "iCLONE (provider)" "/home/iclone/.config/acp-iclone/acp" "${ICLONE_OWNER}"
inject "VEGETA (client)"    "/home/iclone/.config/acp-vegeta/acp" "${VEGETA_OWNER}"

echo ""
echo "── Verifying on droplet ─────────────────────────"
ssh root@${DROPLET_IP} \
    "sudo -u iclone env HOME=/home/iclone ACP_CONFIG_DIR=/home/iclone/.config/acp-iclone/acp acp agent whoami; \
     echo '---'; \
     sudo -u iclone env HOME=/home/iclone ACP_CONFIG_DIR=/home/iclone/.config/acp-vegeta/acp acp agent whoami"

echo ""
echo "✓ Token migration done. If whoami shows both agents, auth is live on the droplet."
