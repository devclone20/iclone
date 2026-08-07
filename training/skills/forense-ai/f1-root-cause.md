# Root-cause investigation — to the origin, always

_Skill artifact for **forense-ai** (forensics / investigation) — last studied 2026-08-07._
_Agent focus: tracing any incident to its origin; evidence-first method on the open web._

## Key points
- Order is law: evidence intake → timeline (one clock, UTC) → hypothesis tree → descend to origin → prove from primary evidence.
- Proximate ≠ root: the last log line names the symptom; keep asking why until the answer leaves your system.
- Test hypotheses cheapest-first; eliminate branches, never adopt favourites untested.
- One symptom can have several origins — enumerate before closing.
- A finding = a demonstration from primary evidence; anything less stays a hypothesis.

## Worked drills
- ✅ **timeline-first** — An incident report starts with a suspect and works backwards.
  - Resolution: Reverse it: evidence intake → timeline reconstruction → hypothesis tree → eliminate until the origin. Conclusions come last, not first.
- ✅ **proximate-vs-root** — A CI run failed and the log's last line blames the test step.
  - Resolution: Last line = proximate cause. Keep asking why until the origin (real case: 'review failed' → runner never acquired → GitHub Actions major outage — code was never the problem).

## Canonical sources
- guardrails
  - _Install, customize, or remove safety guardrails for the pi agent — ONLY on the owner's explicit request. CLONE FRAME ships YOLO (the anti-wipe limit is the only factory guard); this skill arms extra guardrails from three sources when the owner asks. Use when the owner says "install guardrails", "add a safety rule", "protect X", "make it confirm before Y", or "remove the guardrails"._
