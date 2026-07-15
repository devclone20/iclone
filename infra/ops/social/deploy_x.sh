#!/usr/bin/env bash
# ============================================================================
# Deploy iCLONE's Public Voice (X) engine to the droplet as a SEPARATE
# automation: its own service (iclone-x.service), its own runtime dir
# (/opt/iclone-x) and its own env (/opt/iclone-x/x.env).
#
# Idempotent. Safe to re-run. Defaults to X_ENABLED=false so NOTHING posts
# until you fill x.env and flip the switch.
#
# Usage:
#   ops/social/deploy_x.sh <DROPLET_IP>            # deploy + install (disabled)
#   ops/social/deploy_x.sh <DROPLET_IP> enable     # enable + start the service
#   ops/social/deploy_x.sh <DROPLET_IP> disable    # stop + disable (kill-switch)
#   ops/social/deploy_x.sh <DROPLET_IP> status     # show status + recent logs
# ============================================================================
set -euo pipefail

IP="${1:?usage: deploy_x.sh <DROPLET_IP> [enable|disable|status]}"
ACTION="${2:-deploy}"
SSH="ssh -o ConnectTimeout=15 root@${IP}"
REPO_DIR="/opt/iclone"
X_HOME="/opt/iclone-x"

case "$ACTION" in
  status)
    $SSH "systemctl status iclone-x.service --no-pager -l | head -20; echo '--- last logs ---'; tail -n 40 /var/log/iclone/x.log 2>/dev/null || true"
    exit 0 ;;
  enable)
    $SSH "systemctl enable --now iclone-x.service && sleep 2 && systemctl is-active iclone-x.service && tail -n 20 /var/log/iclone/x.log 2>/dev/null || true"
    exit 0 ;;
  disable)
    $SSH "systemctl disable --now iclone-x.service && echo 'iclone-x stopped + disabled (kill-switch engaged)'"
    exit 0 ;;
esac

echo "→ Pulling latest iclone code on droplet…"
$SSH "cd ${REPO_DIR} && git pull --ff-only || echo 'WARN: git pull skipped (manual sync may be needed)'"

echo "→ Ensuring tweepy is installed in the venv…"
$SSH "${REPO_DIR}/venv312/bin/python3.12 -m pip install -q --upgrade 'tweepy>=4.14' 'anthropic>=0.25' python-dotenv"

echo "→ Creating separate runtime dir ${X_HOME} (owned by iclone)…"
$SSH "mkdir -p ${X_HOME} && mkdir -p /var/log/iclone && chown -R iclone:iclone ${X_HOME} /var/log/iclone"

echo "→ Installing x.env template if absent (kept private, chmod 600)…"
$SSH "test -f ${X_HOME}/x.env || (cp ${REPO_DIR}/ops/social/x.env.example ${X_HOME}/x.env && chown iclone:iclone ${X_HOME}/x.env && chmod 600 ${X_HOME}/x.env && echo 'created ${X_HOME}/x.env — FILL IN YOUR X KEYS')"

echo "→ Installing systemd unit…"
$SSH "cp ${REPO_DIR}/ops/social/iclone-x.service /etc/systemd/system/iclone-x.service && systemctl daemon-reload"

echo "→ Running offline self-test (doctor) as the iclone user…"
$SSH "cd ${REPO_DIR} && sudo -u iclone ICLONE_X_HOME=${X_HOME} PYTHONPATH=. ${REPO_DIR}/venv312/bin/python3.12 -m agent.iclone.social.run --doctor"

cat <<EOF

✓ Deployed (service NOT started — safe).
Next:
  1. Put your X API keys in ${X_HOME}/x.env  (ssh root@${IP})
  2. Verify creds:   ssh root@${IP} "cd ${REPO_DIR} && sudo -u iclone ICLONE_X_HOME=${X_HOME} bash -c 'set -a; . ${X_HOME}/x.env; set +a; PYTHONPATH=. venv312/bin/python3.12 -m agent.iclone.social.run --verify'"
  3. Set X_ENABLED=true in x.env, then:  ops/social/deploy_x.sh ${IP} enable
  4. Kill-switch anytime:                 ops/social/deploy_x.sh ${IP} disable
EOF
