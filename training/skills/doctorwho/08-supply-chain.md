# Supply-chain security — the 14-day quarantine

_Skill artifact for **doctorwho** (research deliverables) — last studied 2026-08-21._
_Agent focus: producing the reports that sellers get paid for._

## Key points
- LAW: nothing younger than 14 days gets installed — npm, PyPI, crates, GitHub releases, everything.
- Age comes from the registry API (PyPI JSON upload times, npm `time`), never from claims in a README.
- quarantine_pip.py is the working enforcement: newest release past the soak, exact pin, nothing if unvettable.
- Quarantine + pinning + lockfiles + maintainer/repo/domain checks — layers, not alternatives.
- "Official" in a package description is marketing copy; identity is maintainer + repository + domain.

## Worked drills
- ✅ **fresh-package** — A tempting npm/PyPI package was published 3 days ago.
  - Resolution: REFUSE. Fleet law: nothing younger than 14 days gets installed — fresh releases are where supply-chain attacks live.
- ✅ **registry-dates** — How do you know a package's real age?
  - Resolution: Ask the registry, not the README: pypi.org/pypi/<pkg>/json upload times; npm registry `time` field. The training's own quarantine_pip.py is the working example.

## Canonical sources
- guardrails
  - _Install, customize, or remove safety guardrails for the pi agent — ONLY on the owner's explicit request. CLONE FRAME ships YOLO (the anti-wipe limit is the only factory guard); this skill arms extra guardrails from three sources when the owner asks. Use when the owner says "install guardrails", "add a safety rule", "protect X", "make it confirm before Y", or "remove the guardrails"._
- github-research
  - _Find, evaluate, and adapt an existing open-source project from GitHub for the owner's request. Use when the owner wants to "find a repo/library that does X", borrow or reuse someone's code or UI, evaluate candidate projects, or clone and adapt a GitHub project into CLONE FRAME. Enforces the 14-day install quarantine on all third-party code._
