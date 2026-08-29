#!/usr/bin/env bash
# iclone — personalize a forged repo. Idempotent and non-destructive.
#
#   personalize.sh "Agent Name"     Set the marketplace name (won't clobber an
#                                   already-personalized name without --force).
#   personalize.sh --install-soul   Copy this repo's SOUL.md into Hermes's identity
#                                   slot ($HERMES_HOME/SOUL.md, default
#                                   ~/.hermes/SOUL.md), backing up what was there.
#   personalize.sh --apply-owner    Same, then fold .hermes/owner.local.md into the
#                                   INSTALLED soul. The owner profile lands outside
#                                   this repo, so it can never be committed.
#   Flags: --force  overwrite an existing name.
#
# Why the copy: Hermes reads its identity slot from $HERMES_HOME/SOUL.md only — a
# SOUL.md sitting in a project directory is never loaded. (AGENTS.md *is* read from
# the repo; that half needs no install.)
set -euo pipefail
cd "$(dirname "$0")/.."

PLACEHOLDER="iNFT i01"
SENTINEL="<!-- OWNER-PROFILE-APPLIED -->"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
SOUL_SLOT="$HERMES_HOME_DIR/SOUL.md"

say() { printf '%s\n' "$*"; }

# Copy the tracked SOUL.md into Hermes's identity slot. Never clobbers silently:
# an existing, different soul is backed up next to it first.
install_soul() {
  [ -f SOUL.md ] || { say "✗ SOUL.md not found in the repo root."; exit 1; }
  mkdir -p "$HERMES_HOME_DIR"

  if [ -f "$SOUL_SLOT" ] && cmp -s SOUL.md "$SOUL_SLOT"; then
    say "✓ $SOUL_SLOT already carries this soul (idempotent)."
    return 0
  fi

  if [ -f "$SOUL_SLOT" ]; then
    local backup="$SOUL_SLOT.bak.$(date -u +%Y%m%dT%H%M%SZ)"
    cp "$SOUL_SLOT" "$backup"
    say "  ↳ previous soul backed up to $backup"
  fi

  cp SOUL.md "$SOUL_SLOT"
  chmod 600 "$SOUL_SLOT"
  say "✓ SOUL.md installed into Hermes's identity slot → $SOUL_SLOT"
}

apply_owner() {
  local prof=".hermes/owner.local.md"
  [ -f "$prof" ] || { say "✗ $prof not found. Write the owner profile there first (see owner/OWNER.example.md)."; exit 1; }

  # Check the sentinel BEFORE installing: an already-personalized slot no longer matches
  # the tracked SOUL.md, so re-installing would back it up and throw the profile away.
  if grep -qF "$SENTINEL" "$SOUL_SLOT" 2>/dev/null; then
    say "✓ Owner profile already applied to $SOUL_SLOT — nothing to do (idempotent)."
  else
    install_soul
    { printf '\n%s\n\n## OWNER PROFILE\n\n' "$SENTINEL"; cat "$prof"; } >> "$SOUL_SLOT"
    say "✓ Owner profile folded into $SOUL_SLOT (outside this repo — never committed)."
  fi

  # Safety check: the owner profile source must be ignored, and the installed soul
  # must live outside the working tree.
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git check-ignore -q "$prof" && say "  ✓ $prof is gitignored" || say "  ⚠ $prof is NOT ignored — do not push until fixed"
    case "$SOUL_SLOT" in
      "$PWD"/*) say "  ⚠ $SOUL_SLOT is INSIDE this repo — do not push until fixed" ;;
      *)        say "  ✓ $SOUL_SLOT is outside this repo" ;;
    esac
  fi
}

set_name() {
  local newname="$1" force="${2:-}"
  local current
  current="$(python3 -c "import json;print(json.load(open('identity.json'))['marketplace_name'])" 2>/dev/null || echo "")"

  if [ "$current" != "$PLACEHOLDER" ] && [ -n "$current" ] && [ "$force" != "--force" ]; then
    say "✓ Already personalized as \"$current\" (idempotent; pass --force to change)."
    return 0
  fi

  python3 - "$newname" <<'PY'
import json, sys
p = "identity.json"
with open(p) as f: j = json.load(f)
j["marketplace_name"] = sys.argv[1]
j.pop("marketplace_name_note", None)
with open(p, "w") as f: json.dump(j, f, indent=2, ensure_ascii=False); f.write("\n")
PY
  say "✓ identity.json marketplace_name → \"$newname\""

  # Reflect the name in the metadata template (name field only; leave <...> mint fields).
  python3 - "$newname" <<'PY' 2>/dev/null || true
import json, os, sys
p = "metadata/metadata.template.json"
if os.path.exists(p):
    with open(p) as f: j = json.load(f)
    j["name"] = sys.argv[1]
    with open(p, "w") as f: json.dump(j, f, indent=2, ensure_ascii=False); f.write("\n")
PY

  if [ -f scripts/make-manifest.sh ] && bash scripts/make-manifest.sh >/dev/null; then
    say "✓ manifest regenerated"
  fi
  say "  Your agent answers to \"$newname\", \"iNFT\", and \"Hermes\"."
}

case "${1:-}" in
  ""|-h|--help)
    say "Usage: personalize.sh \"Agent Name\" [--force]"
    say "       personalize.sh --install-soul     (SOUL.md → $SOUL_SLOT)"
    say "       personalize.sh --apply-owner      (install-soul + fold the owner profile)"
    exit 0 ;;
  --install-soul) install_soul ;;
  --apply-owner)  apply_owner ;;
  *) set_name "$1" "${2:-}" ;;
esac
