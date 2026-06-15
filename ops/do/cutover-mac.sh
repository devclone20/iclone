#!/bin/bash
# iCLONE — Clean cutover: stop ALL local Mac daemons before the droplet takes over.
# Run on the Mac. After this, the droplet is the sole owner of the rotating
# refresh tokens (running both machines would break auth).
#
# Usage: bash ops/do/cutover-mac.sh
set -uo pipefail

echo "================================================"
echo "  iCLONE Cutover — stopping Mac fleet"
echo "================================================"

LA_DIR="${HOME}/Library/LaunchAgents"
LABELS=(
    com.iclone.token-refresh
    com.iclone.vegeta-autopilot
    com.iclone.bootstrapper
    com.iclone.bootstrap
    com.iclone.offerings-manager
    com.iclone.daily-report
    com.iclone.watchdog
)

echo "── Unloading launchd agents ─────────────────────"
for label in "${LABELS[@]}"; do
    plist="${LA_DIR}/${label}.plist"
    if [ -f "${plist}" ]; then
        launchctl unload "${plist}" 2>/dev/null && echo "  ✓ unloaded ${label}" || echo "  · ${label} (not loaded)"
    fi
done

echo "── Killing stray processes (nohup server, autopilot) ──"
pkill -f "agent/server.py"        2>/dev/null && echo "  ✓ killed server.py"        || echo "  · no server.py"
pkill -f "vegeta_autopilot.py"    2>/dev/null && echo "  ✓ killed vegeta_autopilot"  || echo "  · no autopilot"
pkill -f "ops/token_refresh.py"   2>/dev/null && echo "  ✓ killed token_refresh"     || echo "  · no token_refresh"

echo ""
echo "── Verify nothing left ──────────────────────────"
left=$(ps aux | grep -iE "server.py|vegeta_autopilot|token_refresh" | grep -v grep | wc -l | tr -d ' ')
if [ "${left}" = "0" ]; then
    echo "  ✓ Mac is clean. Droplet is now the sole token owner."
else
    echo "  ⚠ ${left} process(es) still running:"
    ps aux | grep -iE "server.py|vegeta_autopilot|token_refresh" | grep -v grep | awk '{print "    PID", $2, $11, $12, $13}'
fi
echo ""
echo "Next: migrate tokens, then start the droplet fleet:"
echo "  bash ops/do/migrate-tokens.sh <DROPLET_IP>"
echo "  ssh root@<DROPLET_IP> 'bash /opt/iclone/ops/do/start-services.sh'"
