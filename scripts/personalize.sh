#!/usr/bin/env bash
# iclone — personalize a forged repo. Idempotent and non-destructive.
#
#   personalize.sh "Agent Name"     Set the marketplace name (won't clobber an
#                                   already-personalized name without --force).
#   personalize.sh --stage-soul     Stage the soul for the OWNER to install into
#                                   their own Hermes home. Writes the gitignored
#                                   .hermes/SOUL.local.md and prints the command.
#   personalize.sh --apply-owner    Same, with .hermes/owner.local.md folded in,
#                                   so the owner profile never touches a tracked
#                                   file. Still the owner who installs it.
#   Flags: --force  overwrite an existing name.
#
# WHERE THE SOUL ACTUALLY COMES FROM: AGENTS.md. Hermes injects AGENTS.md straight
# from the repo — always, no trust step — and it carries the soul distillation, so a
# fresh clone already boots as iCLONE with nothing installed.
#
# $HERMES_HOME/SOUL.md (default ~/.hermes/SOUL.md) is a different thing: Hermes reads
# its identity slot from there and only there (a repo SOUL.md is never read), and that
# slot is the OWNER'S GLOBAL SOUL, shared by every project on the machine. This script
# therefore NEVER writes to it. It stages the text and prints the copy command; the
# owner decides whether to install it and how to merge with whatever is already there.
set -euo pipefail
cd "$(dirname "$0")/.."

PLACEHOLDER="iNFT i01"
SENTINEL="<!-- OWNER-PROFILE-APPLIED -->"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
SOUL_SLOT="$HERMES_HOME_DIR/SOUL.md"
STAGED=".hermes/SOUL.local.md"

say() { printf '%s\n' "$*"; }

# Print how to install a staged file into the owner's global slot — never do it here.
print_install_hint() {
  say ""
  say "  This is the OWNER's global soul, shared by every project, so this script does"
  say "  not write it. To install it yourself:"
  if [ -f "$SOUL_SLOT" ]; then
    say ""
    say "      ⚠ $SOUL_SLOT already exists — read both and MERGE by hand."
    say "        Overwriting it would replace your global soul for every project."
    say "        diff:  diff \"$SOUL_SLOT\" \"$PWD/$STAGED\""
  else
    say ""
    say "      cp \"$PWD/$STAGED\" \"$SOUL_SLOT\""
  fi
  say ""
  say "  Optional either way: AGENTS.md already gives this repo its soul."
}

# Stage the tracked SOUL.md (plus, optionally, the owner profile) for the owner.
stage_soul() {
  local with_owner="${1:-}"
  [ -f SOUL.md ] || { say "✗ SOUL.md not found in the repo root."; exit 1; }
  mkdir -p .hermes

  if [ "$with_owner" = "--with-owner" ]; then
    local prof=".hermes/owner.local.md"
    [ -f "$prof" ] || { say "✗ $prof not found. Write the owner profile there first (see owner/OWNER.example.md)."; exit 1; }
    { cat SOUL.md; printf '\n%s\n\n## OWNER PROFILE\n\n' "$SENTINEL"; cat "$prof"; } > "$STAGED"
    say "✓ Soul + owner profile staged → $STAGED"
  else
    cp SOUL.md "$STAGED"
    say "✓ Soul staged → $STAGED"
  fi
  chmod 600 "$STAGED"

  # The staged file may carry PII, so it must never be committable.
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if git check-ignore -q "$STAGED"; then
      say "  ✓ $STAGED is gitignored — it can never be committed"
    else
      say "  ⚠ $STAGED is NOT ignored — do not push until fixed"
    fi
  fi
  print_install_hint
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

usage() {
  say "Usage: personalize.sh \"Agent Name\" [--force]"
  say "       personalize.sh --stage-soul      (SOUL.md → $STAGED, for you to install)"
  say "       personalize.sh --apply-owner     (stage-soul + fold in the owner profile)"
  say ""
  say "The soul reaches the agent through AGENTS.md, which Hermes injects from this repo."
  say "$SOUL_SLOT is your own global soul — this script never writes it."
}

case "${1:-}" in
  ""|-h|--help)   usage ;;
  --stage-soul)   stage_soul ;;
  --apply-owner)  stage_soul --with-owner ;;
  --install-soul)
    say "✗ --install-soul is gone: it wrote to $SOUL_SLOT, which is your own global"
    say "  soul, not this repo's to overwrite. The repo's soul now travels in AGENTS.md,"
    say "  which Hermes injects automatically — nothing to install."
    say "  To keep a global copy anyway:  bash scripts/personalize.sh --stage-soul"
    exit 2 ;;
  -*)
    say "✗ Unknown flag: $1"
    usage
    exit 2 ;;
  *) set_name "$1" "${2:-}" ;;
esac
