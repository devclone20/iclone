#!/bin/bash
# iCLONE Production Server — start script
# Run: bash start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/venv312"
SERVER="$SCRIPT_DIR/agent/server.py"
SMART_WALLET="0x44cc25d55a4291b92f52062ba023ca1f14206664"
RPC_URL="https://mainnet.base.org"

echo "================================================"
echo "  iCLONE ACP Server"
echo "  Smart wallet: $SMART_WALLET"
echo "================================================"
echo ""

# Check smart wallet is deployed
echo "Checking smart wallet deployment..."
DEPLOYED=$("$VENV/bin/python3.12" -c "
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('$RPC_URL'))
code = w3.eth.get_code(Web3.to_checksum_address('$SMART_WALLET'))
print('yes' if len(code) > 0 else 'no')
" 2>/dev/null)

if [ "$DEPLOYED" != "yes" ]; then
    echo ""
    echo "ERROR: Smart wallet not deployed on Base mainnet."
    echo "Run: acp agent use (select CLONE) and retry."
    exit 1
fi

# Check acp-cli auth
echo "Checking acp-cli authentication..."
if ! acp agent whoami --json 2>/dev/null | grep -q '"name"'; then
    echo ""
    echo "ERROR: acp-cli not authenticated."
    echo "Run: acp configure && acp agent use"
    exit 1
fi

echo "Smart wallet deployed. acp-cli authenticated. Starting server..."
echo ""
exec "$VENV/bin/python3.12" "$SERVER"
