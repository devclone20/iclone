#!/bin/bash
# iCLONE — Fleet monitor. Snapshot legível da actividade dos 2 agentes no droplet.
#   bash ops/do/monitor.sh <ip>          → snapshot único
#   bash ops/do/monitor.sh <ip> live     → tail combinado em tempo real
set -uo pipefail
IP="${1:?Usage: monitor.sh <droplet-ip> [live]}"
MODE="${2:-snapshot}"

if [ "${MODE}" = "live" ]; then
    echo "── LIVE (Ctrl+C para sair) — server + vegeta interleaved ──"
    ssh root@${IP} 'tail -n 5 -f /var/log/iclone/server.log /var/log/iclone/vegeta.log'
    exit 0
fi

ssh root@${IP} 'bash -s' <<'REMOTE'
G="\033[0;32m"; R="\033[0;31m"; Y="\033[1;33m"; C="\033[0;36m"; B="\033[1m"; X="\033[0m"
echo -e "${B}═══ iCLONE fleet — $(date -u +'%Y-%m-%d %H:%M:%S UTC') ═══${X}"

# Serviços
printf "Serviços: "
for s in iclone-server iclone-client iclone-vegeta-server iclone-vegeta iclone-token-refresh; do
    st=$(systemctl is-active $s 2>/dev/null)
    [ "$st" = "active" ] && printf "${G}● %s${X}  " "${s#iclone-}" || printf "${R}○ %s($st)${X}  " "${s#iclone-}"
done; echo

# Recursos
mem=$(free -m | awk '/Mem:/{print $3"/"$2"MB"}')
sw=$(free -m | awk '/Swap:/{print $3"MB"}')
dk=$(df -h / | awk 'NR==2{print $5}')
echo -e "Recursos: RAM ${mem} · swap ${sw} · disco ${dk}"

today=$(date -u +%Y-%m-%d)
echo ""
echo -e "${B}── Hoje (${today}) ──${X}"
cr=$(grep -c "created" /var/log/iclone/vegeta.log 2>/dev/null || echo 0)
cp=$(grep -c "completed — escrow" /var/log/iclone/vegeta.log 2>/dev/null || echo 0)
api=$(grep -c "api.anthropic.com" /var/log/iclone/server.log 2>/dev/null || echo 0)
sub=$(grep -c "Deliverable submitted" /var/log/iclone/server.log 2>/dev/null || echo 0)
err=$(grep -ciE "error|fail|unavailable" /var/log/iclone/server.log /var/log/iclone/vegeta.log 2>/dev/null | awk -F: '{s+=$2}END{print s}')
echo -e "  VEGETA criou: ${C}${cr}${X}   iCLONE submeteu: ${C}${sub}${X}   completados: ${G}${cp}${X}   Claude API: ${C}${api}${X}   erros: ${Y}${err}${X}"

echo ""
echo -e "${B}── Pipeline (últimas 12 transições, ordenadas) ──${X}"
{ grep -hE "Hiring|created →|completed" /var/log/iclone/vegeta.log 2>/dev/null \
    | sed -E 's/\[INFO\] [a-z]+\.autopilot: /V→C  /'
  grep -hE "Hiring|created →|completed" /var/log/iclone/iclone-client.log 2>/dev/null \
    | sed -E 's/\[INFO\] [a-z]+\.autopilot: /C→V  /'
  grep -hE "Setting budget|Deliverable submitted" /var/log/iclone/server.log 2>/dev/null \
    | sed -E 's/\[INFO\] iclone.server.CLONE: /iCLONE(prov)  /'
  grep -hE "Setting budget|Deliverable submitted" /var/log/iclone/vegeta-server.log 2>/dev/null \
    | sed -E 's/\[INFO\] iclone.server.VEGETA: /VEGETA(prov)  /'
} | sed -E 's/,[0-9]{3}//; s/\.[0-9]{3}//' | sort | tail -14 \
  | awk '{t=$2; who=$3; $1=$2=$3=""; sub(/^ +/,""); printf "  %s  %-7s %s\n", t, who, $0}'

echo ""
echo -e "${B}── Últimos erros reais (ERROR level) ──${X}"
e=$(grep -hE "\[ERROR\]" /var/log/iclone/server.log /var/log/iclone/vegeta.log 2>/dev/null \
      | grep -viE "failed: 0|processed:" | tail -3 | cut -c1-160)
[ -n "$e" ] && echo "$e" | sed 's/^/  /' || echo -e "  ${G}(nenhum)${X}"
REMOTE
