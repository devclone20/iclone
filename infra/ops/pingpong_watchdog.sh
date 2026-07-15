#!/usr/bin/env bash
# Watchdog: para e desativa o iclone-pingpong quando o iCLONE ficar sem USDC
# para fundar um job de $2. Fica parado até reativação manual.
LOG=/var/log/iclone/pingpong-watchdog.log
PP_LOG=/var/log/iclone/pingpong.log
ICFG=/home/iclone/.config/acp-iclone/acp

log(){ echo "$(date '+%F %T') $*" >> "$LOG"; }

log "==== watchdog iniciado — a vigiar USDC do iCLONE ===="
while true; do
  # Se o pingpong já não está ativo, nada a guardar.
  if ! systemctl is-active --quiet iclone-pingpong; then
    log "iclone-pingpong inativo — watchdog termina."
    exit 0
  fi

  # Sinal de verdade: fund insuficiente registado no log do pingpong.
  if tail -40 "$PP_LOG" 2>/dev/null | grep -qiE 'saldo insuficiente|insufficient'; then
    bal=$(su -l iclone -s /bin/bash -c "ACP_CONFIG_DIR=$ICFG /usr/bin/acp wallet balance --chain-id 8453 2>/dev/null" | awk -F"\t" '$1=="USDC"{print $3}')
    log "DETETADO fund insuficiente — iCLONE sem USDC (saldo=$bal). A parar e desativar pingpong."
    systemctl stop iclone-pingpong
    systemctl disable iclone-pingpong >/dev/null 2>&1
    log "iclone-pingpong PARADO e DESATIVADO. Aguarda ordem manual para reativar."
    exit 0
  fi

  # Registo informativo do saldo (a cada ronda).
  bal=$(su -l iclone -s /bin/bash -c "ACP_CONFIG_DIR=$ICFG /usr/bin/acp wallet balance --chain-id 8453 2>/dev/null" | awk -F"\t" '$1=="USDC"{print $3}')
  cyc=$(python3 -c "import json;print(json.load(open('/opt/iclone/ops/pingpong_state.json')).get('cycle','?'))" 2>/dev/null)
  log "iCLONE USDC=$bal | cycle=$cyc"
  sleep 90
done
