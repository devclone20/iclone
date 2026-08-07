# Supply-chain security — the 14-day quarantine

Fleet law (owner, 2026-08-07): **no agent installs a package published less
than 14 days ago.** npm, PyPI, crates, GitHub releases — all of it. Fresh
releases are where supply-chain attacks live: typosquats, hijacked
maintainer accounts and poisoned point-releases are usually caught by the
ecosystem within days — a 14-day soak lets that immune system work before
our machines touch the code.

**How to know a package's real age:** ask the registry, never the README —
`pypi.org/pypi/<pkg>/json` (upload times per release), the npm registry's
`time` field. The training system itself obeys the law: `quarantine_pip.py`
resolves the newest release that has passed the soak and installs exactly
that version — and if the registry cannot be vetted, it installs nothing.
Law over feature.

**The rest of the hygiene** (the quarantine is necessary, not sufficient):
pin exact versions and use lockfiles; verify the maintainer, the repository
link and the homepage domain before first install (module 06's npm trap:
"Official" in a description proves nothing); prefer tools already installed
and vetted; and treat a sudden burst of releases on a quiet package as a red
flag, not an upgrade opportunity.

## Key points

- LAW: nothing younger than 14 days gets installed — npm, PyPI, crates, GitHub releases, everything.
- Age comes from the registry API (PyPI JSON upload times, npm `time`), never from claims in a README.
- quarantine_pip.py is the working enforcement: newest release past the soak, exact pin, nothing if unvettable.
- Quarantine + pinning + lockfiles + maintainer/repo/domain checks — layers, not alternatives.
- "Official" in a package description is marketing copy; identity is maintainer + repository + domain.

## Sources

- guardrails
- github-research
