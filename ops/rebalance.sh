#!/usr/bin/env bash
# Rebalance: VEGETA contrata iCLONE 10x.
# Run as: su -l iclone -s /bin/bash -c 'dbus-run-session -- bash /opt/iclone/ops/rebalance.sh'
#
# NOTA: o offering_id TEM de ir embutido nos requirements. O histórico on-chain
# do ACP nao carrega o nome da offering, so os requirements. Sem offering_id o
# provider cai no default ($0.25, deliverable generico). Com offering_id o
# iCLONE resolve o preco e executa o handler correto.

ACP=/usr/bin/acp
VEGETA_CFG=/home/iclone/.config/acp-vegeta/acp
ICLONE_WALLET=0x44cc25d55a4291b92f52062ba023ca1f14206664
CHAIN=8453
TOTAL=10
DONE=0

log() { echo "$(date '+%H:%M:%S') $*"; }

run_job() {
    local offering="$1" req="$2" n="$3"
    log "-- Job $n/$TOTAL: $offering --"
    local out job_id status i
    out=$(ACP_CONFIG_DIR="$VEGETA_CFG" $ACP client create-job \
        --provider "$ICLONE_WALLET" --offering-name "$offering" \
        --requirements "$req" --chain-id "$CHAIN" 2>&1) || { log "ERRO: $out"; return 1; }
    job_id=$(echo "$out" | grep -oP '#\K\d{4,}' | head -1)
    [[ -z "$job_id" ]] && { log "ERRO: job_id nao encontrado: $out"; return 1; }
    log "  #$job_id criado"
    for i in $(seq 1 18); do
        sleep 10
        status=$(ACP_CONFIG_DIR="$VEGETA_CFG" $ACP job history --job-id "$job_id" --chain-id "$CHAIN" 2>/dev/null | awk 'NR==1{print tolower($2)}')
        [[ "$status" == "budget_set" || "$status" == "budgetset" ]] && break
        [[ "$status" == "rejected" || "$status" == "expired" ]] && { log "  terminal: $status"; return 1; }
    done
    log "  budget_set"
    ACP_CONFIG_DIR="$VEGETA_CFG" $ACP client fund --job-id "$job_id" --chain-id "$CHAIN" 2>&1 || true
    log "  fundado"
    for i in $(seq 1 30); do
        sleep 10
        status=$(ACP_CONFIG_DIR="$VEGETA_CFG" $ACP job history --job-id "$job_id" --chain-id "$CHAIN" 2>/dev/null | awk 'NR==1{print tolower($2)}')
        [[ "$status" == "submitted" ]] && break
        [[ "$status" == "rejected" || "$status" == "expired" ]] && { log "  terminal: $status"; return 1; }
    done
    log "  submitted"
    ACP_CONFIG_DIR="$VEGETA_CFG" $ACP client complete --job-id "$job_id" --chain-id "$CHAIN" 2>&1 || true
    log "  OK #$job_id completo"
    return 0
}

log "=== Rebalance VEGETA->iCLONE: $TOTAL jobs ==="
jobs=(
    "tokenSnapshotQuick:{\"offering_id\":\"tokenSnapshotQuick\",\"token\":\"BTC\"}"
    "cryptoNewsFlash:{\"offering_id\":\"cryptoNewsFlash\"}"
    "tokenSnapshotQuick:{\"offering_id\":\"tokenSnapshotQuick\",\"token\":\"ETH\"}"
    "cryptoNewsFlash:{\"offering_id\":\"cryptoNewsFlash\"}"
    "tokenSnapshotQuick:{\"offering_id\":\"tokenSnapshotQuick\",\"token\":\"SOL\"}"
    "cryptoNewsFlash:{\"offering_id\":\"cryptoNewsFlash\"}"
    "tokenSnapshotQuick:{\"offering_id\":\"tokenSnapshotQuick\",\"token\":\"BNB\"}"
    "cryptoNewsFlash:{\"offering_id\":\"cryptoNewsFlash\"}"
    "tokenSnapshotQuick:{\"offering_id\":\"tokenSnapshotQuick\",\"token\":\"AVAX\"}"
    "cryptoNewsFlash:{\"offering_id\":\"cryptoNewsFlash\"}"
)
idx=0
for entry in "${jobs[@]}"; do
    idx=$((idx + 1))
    offering="${entry%%:*}"
    req="${entry#*:}"
    run_job "$offering" "$req" "$idx" && DONE=$((DONE + 1))
    [[ $idx -lt $TOTAL ]] && { log "  pausa 20s..."; sleep 20; }
done
log "=== Concluido: $DONE/$TOTAL jobs ==="
