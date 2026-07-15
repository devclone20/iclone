#!/bin/bash
# iCLONE — Register fresh ACP signers on the droplet (REQUIRED step).
#
# WHY: the signer P256 private keys in ~/Library/Application Support/acp-cli/
# signer-keys.json are HARDWARE-BOUND to the Mac (Secure Enclave wraps the
# decryption secret). Copying the file to Linux fails with
# "decryption failed: cipher: message authentication failed".
# The droplet must generate and register its OWN signer keypair per agent.
# This is non-destructive — the Mac signer stays valid; an agent can hold
# multiple signers.
#
# Policy: restricted = autonomous for ALL ACP transactions (matches the Mac).
#
# Usage: bash ops/do/register-signers.sh <droplet-ip>
# Then approve each printed URL in the browser (Privy), and run:
#        bash ops/do/register-signers.sh <droplet-ip> status
set -euo pipefail

IP="${1:?Usage: register-signers.sh <droplet-ip> [status]}"
MODE="${2:-issue}"

ICLONE_ID="019eae06-96cd-77d0-8f8b-a6abb71f0cd7"
ICLONE_CFG="/home/iclone/.config/acp-iclone/acp"
VEGETA_ID="019ec5ec-4b48-750d-894a-7f1fedebb988"
VEGETA_CFG="/home/iclone/.config/acp-vegeta/acp"

remote() { ssh root@${IP} "sudo -u iclone env HOME=/home/iclone ACP_CONFIG_DIR=$1 acp ${*:2}"; }

if [ "${MODE}" = "issue" ]; then
    echo "── iCLONE signer ──"
    remote "${ICLONE_CFG}" agent add-signer --agent-id ${ICLONE_ID} --policy restricted --no-wait \
        | grep -E "signerUrl|requestId|publicKey"
    echo ""
    echo "── VEGETA signer ──"
    remote "${VEGETA_CFG}" agent add-signer --agent-id ${VEGETA_ID} --policy restricted --no-wait \
        | grep -E "signerUrl|requestId|publicKey"
    echo ""
    echo ">>> Approve BOTH signerUrl in the browser (Privy), then run:"
    echo "    bash ops/do/register-signers.sh ${IP} status"
    echo "    (you'll be prompted for each requestId + publicKey)"
else
    read -rp "iCLONE requestId: " IRID; read -rp "iCLONE publicKey: " IPK
    remote "${ICLONE_CFG}" agent signer-status --agent-id ${ICLONE_ID} --request-id "${IRID}" --public-key "${IPK}" | tail -4
    echo ""
    read -rp "VEGETA requestId: " VRID; read -rp "VEGETA publicKey: " VPK
    remote "${VEGETA_CFG}" agent signer-status --agent-id ${VEGETA_ID} --request-id "${VRID}" --public-key "${VPK}" | tail -4
fi
