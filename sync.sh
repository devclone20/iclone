#!/bin/bash
# iCLONE — sync local com GitHub (devclone20/iclone)
# Corre: ./sync.sh
# Ou adiciona ao crontab: */30 * * * * /Users/alexaist1107397/Desktop/AI/iclone/sync.sh
cd "$(dirname "$0")"
git fetch origin && git pull --ff-only origin main && echo "✓ iCLONE synced $(date)"
