#!/usr/bin/env bash
# iclone — personalize a forged repo. Idempotent and non-destructive.
#
#   personalize.sh "Agent Name"     Set the marketplace name (won't clobber an
#                                   already-personalized name without --force).
#   personalize.sh --apply-owner    Fold .hermes/owner.local.md into the LOCAL
#                                   SOUL.md and untrack that file so
#                                   the owner profile is never committed.
#   Flags: --force  overwrite an existing name.
set -euo pipefail
cd "$(dirname "$0")/.."

PLACEHOLDER="iNFT i01"
MARKER="<!-- ─────────────────────────────────────────────────────────────────────────"
SENTINEL="<!-- OWNER-PROFILE-APPLIED -->"

say() { printf '%s\n' "$*"; }

apply_owner() {
  local prof=".hermes/owner.local.md"
  local target="SOUL.md"
  [ -f "$prof" ] || { say "✗ $prof not found. Write the owner profile there first (see owner/OWNER.example.md)."; exit 1; }

  if grep -qF "$SENTINEL" "$target" 2>/dev/null; then
    say "✓ Owner profile already applied — nothing to do (idempotent)."
  else
    { printf '\n%s\n\n## OWNER PROFILE\n\n' "$SENTINEL"; cat "$prof"; } >> "$target"
    say "✓ Owner profile folded into $target (local only)."
  fi

  # Untrack the personalized system prompt so PII is never committed/pushed.
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git rm --cached --quiet "$target" 2>/dev/null || true
    grep -qxF "SOUL.md" .gitignore 2>/dev/null || printf '\n# personalized system prompt (contains owner profile)\nSOUL.md\n' >> .gitignore
  fi

  # Safety check: owner files must be ignored.
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    for f in .hermes/owner.local.md SOUL.md; do
      git check-ignore -q "$f" && say "  ✓ $f is gitignored" || say "  ⚠ $f is NOT ignored — do not push until fixed"
    done
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

  [ -x scripts/make-manifest.sh ] && bash scripts/make-manifest.sh >/dev/null && say "✓ manifest regenerated"
  say "  Your agent answers to \"$newname\", \"iNFT\", and \"Hermes\"."
}

case "${1:-}" in
  ""|-h|--help) say "Usage: personalize.sh \"Agent Name\" [--force]  |  personalize.sh --apply-owner"; exit 0 ;;
  --apply-owner) apply_owner ;;
  *) set_name "$1" "${2:-}" ;;
esac
