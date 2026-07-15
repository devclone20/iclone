#!/bin/bash
# iCLONE — Install launchd daemons (macOS)
# Run once after deploying smart wallet.
#
# Usage:
#   bash ops/install_daemons.sh           # install all
#   bash ops/install_daemons.sh --unload  # remove all

set -e

LAUNCHD_DIR="$(cd "$(dirname "$0")/launchd" && pwd)"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

WATCHDOG="com.iclone.watchdog"
REPORT="com.iclone.daily-report"

if [ "$1" = "--unload" ]; then
    echo "Removing iCLONE daemons..."
    launchctl unload "$LAUNCH_AGENTS/$WATCHDOG.plist" 2>/dev/null || true
    launchctl unload "$LAUNCH_AGENTS/$REPORT.plist" 2>/dev/null || true
    rm -f "$LAUNCH_AGENTS/$WATCHDOG.plist"
    rm -f "$LAUNCH_AGENTS/$REPORT.plist"
    echo "Done — daemons removed."
    exit 0
fi

echo "Installing iCLONE daemons..."

mkdir -p "$LAUNCH_AGENTS"
mkdir -p "$HOME/Library/Logs"
mkdir -p "$HOME/Library/Application Support/iclone"

# Copy plists
cp "$LAUNCHD_DIR/$WATCHDOG.plist" "$LAUNCH_AGENTS/"
cp "$LAUNCHD_DIR/$REPORT.plist" "$LAUNCH_AGENTS/"

# Unload if already running (clean reinstall)
launchctl unload "$LAUNCH_AGENTS/$WATCHDOG.plist" 2>/dev/null || true
launchctl unload "$LAUNCH_AGENTS/$REPORT.plist" 2>/dev/null || true

# Load
launchctl load "$LAUNCH_AGENTS/$WATCHDOG.plist"
launchctl load "$LAUNCH_AGENTS/$REPORT.plist"

echo ""
echo "✅ Daemons installed and running:"
echo ""
echo "  com.iclone.watchdog     → checks server every 5min, auto-restarts if down"
echo "  com.iclone.daily-report → performance report every day at 08:00"
echo ""
echo "Logs:"
echo "  tail -f ~/Library/Logs/iclone-watchdog.log"
echo "  tail -f ~/Library/Logs/iclone-server.log"
echo "  tail -f ~/Library/Logs/iclone-daily-report.log"
echo ""
echo "Status check:"
echo "  ~/Desktop/AI/iclone/venv312/bin/python3.12 ops/watchdog.py --status"
