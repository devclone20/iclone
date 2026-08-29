#!/usr/bin/env bash
# iclone (iCLONE iNFT monorepo) — boot the agent with this project's resources TRUSTED.
# Hermes injects AGENTS.md straight from the repo, and discovers this repo's skills under
# .hermes/skills once the project root is trusted. `hermes skills trust` grants that
# trust (persisted). The soul distillation is the one piece that is NOT read from the
# repo: Hermes reads its identity slot from $HERMES_HOME/SOUL.md, so this script only
# checks that the slot carries our soul and tells you how to install it if it does not.
# Extra args pass through to `hermes chat`.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v hermes >/dev/null 2>&1; then
  echo "✗ 'hermes' not found. Run: bash scripts/setup.sh"
  echo "  (or install directly: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash)"
  exit 1
fi

SOUL_SLOT="${HERMES_HOME:-$HOME/.hermes}/SOUL.md"
if ! grep -qF 'founder-mind and official agent of the CLONE platform' "$SOUL_SLOT" 2>/dev/null; then
  echo "⚠ $SOUL_SLOT does not carry the iCLONE soul — booting without it."
  echo "  Install it first:  bash scripts/personalize.sh --install-soul"
fi

hermes skills trust "$PWD" >/dev/null 2>&1 || echo "⚠ 'hermes skills trust' failed — this repo's skills will not load."
exec hermes chat "$@"
