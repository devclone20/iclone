#!/bin/bash
# iCLONE — Training cron runner
# Chamado pelo crontab 2× por dia (08:07 e 20:13 Lisboa)
# Executa scheduler + gera relatório mínimo

set -euo pipefail

ICLONE_DIR="/Users/alexaist1107397/Desktop/AI/iclone"
VENV="$ICLONE_DIR/venv312/bin/python3"
LOG_DIR="$ICLONE_DIR/training_reports"
DATE=$(date +%Y%m%d)
SESSION=$([ $(date +%H) -lt 14 ] && echo "morning" || echo "evening")
LOG="$LOG_DIR/${DATE}_${SESSION}.log"

mkdir -p "$LOG_DIR"

echo "=== iCLONE Training — $DATE $SESSION ===" >> "$LOG"
echo "Started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$LOG"

cd "$ICLONE_DIR"
"$VENV" -m agent.iclone.training.scheduler >> "$LOG" 2>&1

echo "Finished: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$LOG"
echo "=======================================" >> "$LOG"
