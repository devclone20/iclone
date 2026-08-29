#!/usr/bin/env bash
# iclone (iCLONE iNFT monorepo) — boot the agent with this project's resources TRUSTED.
# Hermes injects AGENTS.md straight from the repo — always, with no trust step — and
# AGENTS.md carries the soul distillation, so the soul loads on a bare clone. Trust is
# only about skills: `hermes skills trust` is what makes this repo's .hermes/skills
# discoverable, and that is the one thing this script grants (persisted).
# The root SOUL.md is NOT read from a repo (Hermes reads its identity slot from
# $HERMES_HOME/SOUL.md only), which is exactly why the soul travels in AGENTS.md.
# Extra args pass through to `hermes chat`.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v hermes >/dev/null 2>&1; then
  echo "✗ 'hermes' not found. Run: bash scripts/setup.sh"
  echo "  (or install directly: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash)"
  exit 1
fi

if ! grep -qF 'founder-mind and official agent of the CLONE platform' AGENTS.md 2>/dev/null; then
  echo "⚠ AGENTS.md does not carry the iCLONE soul — booting without it."
  echo "  AGENTS.md is the file Hermes injects from this repo; the soul lives in it."
fi

hermes skills trust "$PWD" >/dev/null 2>&1 || echo "⚠ 'hermes skills trust' failed — this repo's skills will not load."
exec hermes chat "$@"
