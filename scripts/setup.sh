#!/usr/bin/env bash
# iclone (iCLONE iNFT monorepo) — Hermes substrate setup. Verifies this repo's wiring and
# never calls sudo itself. Safe to re-run (installs are idempotent). This only wires the
# INTERACTIVE Hermes substrate; it does NOT touch the Python economy runtime in
# apps/agent/iclone (that has its own venv + start.sh).
#
# SUPPLY CHAIN — read before running. Hermes is not an npm package, so there is no pinned
# version to install: this script fetches the vendor's install script from
# $HERMES_INSTALL_URL and pipes it to bash. That is the vendor's documented install path,
# and it means you are trusting whatever that URL serves at the time you run it — this
# script cannot pin it or vouch for what it does (including whether it asks for sudo).
# Read it first if you want the guarantee:  curl -fsSL <url> | less
# opensrc, which IS an npm package, stays pinned and installed with --ignore-scripts.
# Every command that touches your machine is printed before it runs.
set -euo pipefail
cd "$(dirname "$0")/.."

HERMES_INSTALL_URL="${HERMES_INSTALL_URL:-https://hermes-agent.nousresearch.com/install.sh}"
OPENSRC_VERSION="${OPENSRC_VERSION:-0.7.3}"
OPENSRC_PKG="opensrc@${OPENSRC_VERSION}"

say() { printf '%s\n' "$*"; }

say "── iclone · Hermes substrate setup ────────────────────────────"

# ── Preflight ────────────────────────────────────────────────────
command -v git  >/dev/null 2>&1 || { say "✗ git is required."; exit 1; }
command -v curl >/dev/null 2>&1 || { say "✗ curl is required to fetch the Hermes installer."; exit 1; }
say "  ✓ git and curl present"

# ── Install the substrate: Hermes Agent (no sudo) ────────────────
if command -v hermes >/dev/null 2>&1; then
  say "  ✓ hermes already installed ($(hermes --version 2>/dev/null || echo present))"
  INSTALL_MODE=present
else
  say "→ Installing the Hermes Agent (Nous Research, MIT)…"
  say "  \$ curl -fsSL $HERMES_INSTALL_URL | bash"
  curl -fsSL "$HERMES_INSTALL_URL" | bash
  INSTALL_MODE=installed
  command -v hermes >/dev/null 2>&1 || {
    say "  ⚠ 'hermes' is not on PATH yet — open a new shell, or add the installer's"
    say "    bin directory to PATH, then re-run this script."
  }
fi

# opensrc is an independent helper (read real dependency source before vendoring).
if command -v npm >/dev/null 2>&1; then
  say "  \$ npm install -g --ignore-scripts $OPENSRC_PKG"
  if npm install -g --ignore-scripts "$OPENSRC_PKG" >/dev/null 2>&1; then
    say "  ✓ opensrc installed"
  else
    say "  ! opensrc skipped (optional helper; needs a writable npm prefix)"
  fi
fi

# ── Verify wiring ────────────────────────────────────────────────
say "→ Verifying repo wiring…"
for f in SOUL.md soul/neural_soul.md identity.json skills/cmux/SKILL.md AGENTS.md; do
  [ -f "$f" ] && say "  ✓ $f" || { say "  ✗ MISSING: $f"; exit 1; }
done
[ -e ".hermes/skills" ] && say "  ✓ .hermes/skills → ../skills (project skills, loaded once trusted)"
command -v hermes  >/dev/null 2>&1 && say "  ✓ hermes $(hermes --version 2>/dev/null || echo installed) ($INSTALL_MODE)"
command -v opensrc >/dev/null 2>&1 && say "  ✓ opensrc installed"

# AGENTS.md is the only file Hermes injects from a project, so it is where the soul
# has to live. (A repo SOUL.md is never read: Hermes reads its identity slot from
# $HERMES_HOME/SOUL.md alone, and that slot belongs to the owner, not to this repo.)
if grep -qF 'founder-mind and official agent of the CLONE platform' AGENTS.md 2>/dev/null; then
  say "  ✓ AGENTS.md carries the iCLONE soul (injected from this repo, no trust needed)"
else
  say "  ✗ AGENTS.md does NOT carry the iCLONE soul — the agent would boot as stock Hermes"
  exit 1
fi

NAME="$(python3 -c "import json;print(json.load(open('identity.json'))['marketplace_name'])" 2>/dev/null || echo 'iCLONE')"
say ""
say "── Substrate ready. Next:"
say "   1) Connect a model: hermes model    (you type the key, never the assistant)"
say "   2) Boot:            bash scripts/boot.sh   (trusts this project, then 'hermes chat')"
say "   3) Terminal:        bash scripts/install-command.sh   (then type '$NAME' in the CLONE FRAME iT terminal)"
say "   The soul needs no install step — it travels in AGENTS.md, which Hermes injects"
say "   from this repo. (Want it in every project too? bash scripts/personalize.sh --stage-soul)"
say "   Current name: \"$NAME\" — it also answers to \"iNFT\" and \"Hermes\"."
