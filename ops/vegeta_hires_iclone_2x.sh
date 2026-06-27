#!/usr/bin/env bash
# One-off: VEGETA contrata iCLONE 2x para deepCryptoIntelReport ($2 cada), paga e completa.
# Run as: su -l iclone -s /bin/bash -c 'dbus-run-session -- bash /opt/iclone/ops/vegeta_hires_iclone_2x.sh'
ACP=/usr/bin/acp
VEGETA_CFG=/home/iclone/.config/acp-vegeta/acp
ICLONE_WALLET=0x44cc25d55a4291b92f52062ba023ca1f14206664
CHAIN=8453
DONE=0

log(){ echo "$(date '+%H:%M:%S') $*"; }

run_job(){
  local n="$1" token="$2"
  local req="{\"offering_id\":\"deepCryptoIntelReport\",\"token\":\"$token\",\"focus\":\"tokenomics, catalysts, risks\"}"
  log "== Job $n/2: deepCryptoIntelReport ($token) =="
  local out job_id status i
  out=$(ACP_CONFIG_DIR="$VEGETA_CFG" $ACP client create-job --provider "$ICLONE_WALLET" \
        --offering-name deepCryptoIntelReport --requirements "$req" --chain-id "$CHAIN" 2>&1) \
        || { log "  ERRO create: $out"; return 1; }
  job_id=$(echo "$out" | grep -oP '#\K\d{4,}' | head -1)
  [[ -z "$job_id" ]] && { log "  ERRO job_id: $out"; return 1; }
  log "  #$job_id criado"

  for i in $(seq 1 18); do
    sleep 10
    status=$(ACP_CONFIG_DIR="$VEGETA_CFG" $ACP job history --job-id "$job_id" --chain-id "$CHAIN" 2>/dev/null | awk 'NR==1{print tolower($2)}')
    [[ "$status" == "budget_set" || "$status" == "budgetset" ]] && break
    [[ "$status" == "rejected" || "$status" == "expired" ]] && { log "  terminal: $status"; return 1; }
  done
  log "  budget_set"

  out=$(ACP_CONFIG_DIR="$VEGETA_CFG" $ACP client fund --job-id "$job_id" --chain-id "$CHAIN" 2>&1)
  if echo "$out" | grep -qiE 'exceeds balance|insufficient|execution reverted'; then
    log "  ❌ saldo insuficiente para fundar #$job_id — VEGETA sem USDC?"; return 1
  fi
  log "  fundado (VEGETA pagou \$2)"

  for i in $(seq 1 60); do
    sleep 10
    status=$(ACP_CONFIG_DIR="$VEGETA_CFG" $ACP job history --job-id "$job_id" --chain-id "$CHAIN" 2>/dev/null | awk 'NR==1{print tolower($2)}')
    [[ "$status" == "submitted" ]] && break
    [[ "$status" == "rejected" || "$status" == "expired" ]] && { log "  terminal: $status"; return 1; }
  done
  log "  deliverable submetido pelo iCLONE"

  ACP_CONFIG_DIR="$VEGETA_CFG" $ACP client complete --job-id "$job_id" --chain-id "$CHAIN" >/dev/null 2>&1
  log "  ✅ #$job_id COMPLETO — iCLONE recebeu pagamento"
  return 0
}

log "=== VEGETA contrata iCLONE 2x (deepCryptoIntelReport \$2) ==="
run_job 1 BTC && DONE=$((DONE+1))
log "  -- pausa 15s --"; sleep 15
run_job 2 ETH && DONE=$((DONE+1))
log "=== Concluido: $DONE/2 jobs ==="
