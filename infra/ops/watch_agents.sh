#!/usr/bin/env bash
# iCLONE — Live agent monitor
# Mostra os 4 agentes em split-view no terminal
# Usage: ./ops/watch_agents.sh

LOG_DIR="$HOME/Library/Logs/iCLONE"

# Cores
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
RESET='\033[0m'

clear
echo -e "${BOLD}iCLONE — Multi-Agent Live Monitor${RESET}  (Ctrl+C para sair)"
echo -e "──────────────────────────────────────────────────────────────"

# Status inicial
for slug in clone supersayatin doctorwho matrix; do
  pid_file="/tmp/iclone-${slug}.pid"
  if [ -f "$pid_file" ]; then
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
      echo -e "  ${GREEN}● RUNNING${RESET}  $slug  (PID $pid)"
    else
      echo -e "  ${YELLOW}○ STOPPED${RESET}  $slug"
    fi
  else
    echo -e "  ${YELLOW}○ STOPPED${RESET}  $slug"
  fi
done

echo -e "──────────────────────────────────────────────────────────────"
echo -e "${BOLD}Logs em tempo real:${RESET}"
echo ""

# Colorize por agente e fazer tail de todos ao mesmo tempo
tail -f \
  "$LOG_DIR/clone.log" \
  "$LOG_DIR/supersayatin.log" \
  "$LOG_DIR/doctorwho.log" \
  "$LOG_DIR/matrix.log" \
  2>/dev/null | awk '
    /clone\.log/         { prefix = "\033[0;36m[CLONE        ]\033[0m" }
    /supersayatin\.log/  { prefix = "\033[0;32m[SuperSayatin ]\033[0m" }
    /doctorwho\.log/     { prefix = "\033[0;35m[DoctorWHO    ]\033[0m" }
    /matrix\.log/        { prefix = "\033[1;33m[MATRIX       ]\033[0m" }
    /^==/               { next }
    {
      # Highlight job events
      line = $0
      if (line ~ /Event — job/) gsub(/Event — job/, "\033[1;33mEvent — job\033[0m", line)
      if (line ~ /Setting budget/) gsub(/Setting budget/, "\033[0;32mSetting budget\033[0m", line)
      if (line ~ /Deliverable submitted/) gsub(/Deliverable submitted/, "\033[1;32mDeliverable submitted\033[0m", line)
      if (line ~ /completed — payment/) gsub(/completed — payment/, "\033[1;32mcompleted — payment\033[0m", line)
      if (line ~ /FAILED|ERROR|error/) gsub(/FAILED|ERROR|error/, "\033[0;31m&\033[0m", line)
      if (line ~ /LIVE/) gsub(/LIVE/, "\033[0;32mLIVE\033[0m", line)
      if (line ~ /restarting/) gsub(/restarting/, "\033[1;33mrestarting\033[0m", line)
      print prefix " " line
    }
  '
