#!/bin/bash
# Activate a prepared-but-inactive agent (DoctorWHO / SuperSayatin / MATRIX).
# Run ON the droplet (as root). Prereq: the agent's wallet is FUNDED with USDC.
#
# Phases:
#   activate-agent.sh <slug> setup    → create config dir (shared owner) + add-signer (prints URL)
#   <approve the signerUrl in the browser>
#   activate-agent.sh <slug> finish <requestId> <publicKey>
#                                     → persist signer + publish offerings + enable+start units
#
# slugs: doctorwho | supersayatin | matrix
set -uo pipefail

SLUG="${1:?Usage: activate-agent.sh <slug> <setup|finish> [...]}"
PHASE="${2:?phase: setup | finish}"

declare -A AID=(
  [doctorwho]=019ebb92-93e8-7b4e-b2e8-39c3419843c9
  [supersayatin]=019ebb92-7415-7baa-93e9-ee19a7742877
  [matrix]=019ebb92-b4be-7660-82d3-4b1647843e6a )
declare -A WALLET=(
  [doctorwho]=0x875242eb5c91270ca80ed7753a87d6e22e4f5acf
  [supersayatin]=0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3
  [matrix]=0x07924dea2c8212969d5dc5655785aa5063adb2bc )

[ -n "${AID[$SLUG]:-}" ] || { echo "unknown slug: $SLUG"; exit 1; }
AGENT_ID="${AID[$SLUG]}"
AGENT_WALLET="${WALLET[$SLUG]}"
CFG="/home/iclone/.config/acp-${SLUG}/acp"
ICLONE_CFG="/home/iclone/.config/acp-iclone/acp"
RUN_AGENT="sudo -u iclone env HOME=/home/iclone ACP_CONFIG_DIR=${CFG} acp"

if [ "$PHASE" = "setup" ]; then
  echo "── Creating config dir for ${SLUG} (shared owner session) ──"
  sudo -u iclone mkdir -p "${CFG}"
  # Share the owner's config (owner 0xb480 owns all 5 agents), set active wallet
  sudo -u iclone python3 - "$ICLONE_CFG/config.json" "$CFG/config.json" "$AGENT_WALLET" <<'PY'
import json,sys
src,dst,wallet=sys.argv[1],sys.argv[2],sys.argv[3].lower()
c=json.load(open(src)); c["activeWallet"]=wallet; json.dump(c,open(dst,"w"),indent=2)
print("  config.json written, activeWallet=",wallet)
PY
  sudo -u iclone chmod 600 "${CFG}/config.json"
  echo "── Registering signer (restricted) — approve the URL in the browser ──"
  ${RUN_AGENT} agent add-signer --agent-id "${AGENT_ID}" --policy restricted --no-wait 2>&1 \
    | grep -E "signerUrl|requestId|publicKey"
  echo ""
  echo ">>> Approve the signerUrl, then run:"
  echo "    bash $0 ${SLUG} finish <requestId> <publicKey>"

elif [ "$PHASE" = "finish" ]; then
  RID="${3:?requestId}"; PK="${4:?publicKey}"
  echo "── Persisting signer ──"
  ${RUN_AGENT} agent signer-status --agent-id "${AGENT_ID}" --request-id "${RID}" --public-key "${PK}" 2>&1 | tail -3
  echo ""
  echo "── Publishing offerings from published_offerings_${SLUG}.json ──"
  sudo -u iclone python3 - "/opt/iclone/published_offerings_${SLUG}.json" "${CFG}" <<'PY'
import json,sys,subprocess,os
cat=json.load(open(sys.argv[1])); cfg=sys.argv[2]
env={**os.environ,"HOME":"/home/iclone","ACP_CONFIG_DIR":cfg}
ok=0
for o in cat["published"]:
    r=subprocess.run(["acp","offering","create",
        "--name",o["name"],"--description",o["description"],
        "--price-type","fixed","--price-value",str(o["price_usdc"]),
        "--sla-minutes",str(o.get("sla_minutes",120)),
        "--requirements",o.get("requirements",""),"--deliverable",o.get("deliverable",""),
        "--no-required-funds","--no-hidden"],
        capture_output=True,text=True,env=env)
    if r.returncode==0 or "success" in (r.stdout+r.stderr).lower(): ok+=1
    else: print("  ! ",o["name"],(r.stderr or r.stdout)[:80])
print(f"  published {ok}/{len(cat['published'])} offerings")
PY
  echo ""
  echo "── Enabling + starting services ──"
  systemctl enable --now "iclone-${SLUG}-server"
  sleep 4
  systemctl enable --now "iclone-${SLUG}-client"
  systemctl is-active "iclone-${SLUG}-server" "iclone-${SLUG}-client"
  echo "✓ ${SLUG} activated."
else
  echo "unknown phase: $PHASE"; exit 1
fi
