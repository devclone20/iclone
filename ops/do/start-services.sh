#!/bin/bash
# iCLONE — Install systemd units and start the live fleet (v2)
# Fleet: iclone-server (provider) · iclone-vegeta (client) ·
#        iclone-token-refresh (keep-alive) · iclone-training.timer (2×/day)
# Run as root on the droplet.
set -euo pipefail

ICLONE_DIR="/opt/iclone"
SYSTEMD_DIR="/etc/systemd/system"
LOG_DIR="/var/log/iclone"

mkdir -p ${LOG_DIR}
chown -R iclone:iclone ${LOG_DIR}

echo "── Installing systemd units ─────────────────────"
cp ${ICLONE_DIR}/ops/systemd/iclone-server.service        ${SYSTEMD_DIR}/
cp ${ICLONE_DIR}/ops/systemd/iclone-vegeta.service        ${SYSTEMD_DIR}/
cp ${ICLONE_DIR}/ops/systemd/iclone-token-refresh.service ${SYSTEMD_DIR}/
cp ${ICLONE_DIR}/ops/systemd/iclone-training.service      ${SYSTEMD_DIR}/
cp ${ICLONE_DIR}/ops/systemd/iclone-training.timer        ${SYSTEMD_DIR}/

echo "── Installing logrotate ─────────────────────────"
cp ${ICLONE_DIR}/ops/systemd/iclone-logrotate.conf /etc/logrotate.d/iclone 2>/dev/null || true

echo "── Enabling + starting ──────────────────────────"
systemctl daemon-reload

systemctl enable --now iclone-token-refresh
sleep 3
systemctl enable --now iclone-server
sleep 5
systemctl enable --now iclone-vegeta
systemctl enable --now iclone-training.timer

echo ""
echo "── Status ───────────────────────────────────────"
for svc in iclone-token-refresh iclone-server iclone-vegeta; do
    systemctl --no-pager -l status ${svc} | head -4
    echo ""
done
echo "── Training timer ───────────────────────────────"
systemctl list-timers iclone-training.timer --no-pager || true

echo ""
echo "================================================"
echo "  ✓ Fleet live 24/7. Mac can be shut down."
echo "================================================"
echo ""
echo "Logs:"
echo "  tail -f ${LOG_DIR}/server.log"
echo "  tail -f ${LOG_DIR}/vegeta.log"
echo "  tail -f ${LOG_DIR}/token-refresh.log"
echo "  tail -f ${LOG_DIR}/training.log"
echo ""
echo "Control:"
echo "  systemctl restart iclone-server"
echo "  journalctl -u iclone-vegeta -f"
