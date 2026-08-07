# Fleet training system

One training system for the whole devclone20 agent fleet. Replaces the
legacy Day A / Day B workflows and the per-tool-repo trainings (2026-08-07).

## How it works

- **Schedule** (`.github/workflows/training.yml`, plus manual dispatch):
  - **Mon/Wed/Fri 05:00 UTC — fleet**: all 9 agents cycle the shared
    curriculum, 2 modules per session.
  - **Tue/Thu 05:00 UTC — specialty**: doctor-agent deepens IST-standard
    academic work and the university's scientific repositories (Técnico
    Scholar + Repositório ULisboa, probed live); forense-ai deepens
    to-the-origin investigation on the open web (Wayback + certificate
    transparency, probed live).
- **Engine:** `training/engine.py` — deterministic core. Each session the
  roster studies the next curriculum modules (cycling), runs the attached
  machine-checked drills, and gets its skill artifacts refreshed under
  `training/skills/<agent>/`. Per-agent progress lives in `training/state/`.
  Web probes degrade gracefully — an unreachable site is reported, never a
  failed session.
- **Curriculum:** `training/curriculum/` — fleet: ACP/Virtuals foundations,
  the ACP CLI, droplet trading ops, negotiation phases, Economy OS,
  Robinhood Chain, debugging, supply-chain law. Specialty: `d1–d3` (Doctor /
  IST) and `f1–f3` (Forense / investigation). Canonical sources are the
  public skill files in `devclone20/cloneframe_app_executable` (checked out
  read-only at run time).
- **Report:** every session writes `training/reports/<date>.md` (PT) and the
  workflow opens it as an issue — GitHub emails the owner on creation, then
  the issue is closed to keep the tracker clean. The reports directory is the
  permanent training diary.
- **LLM layer:** optional. With ANTHROPIC_API_KEY credit available the engine
  adds a coach note; without it the report says so and the session still
  completes. Billing can degrade the note, never the training.

## Laws

- No droplet access, no ssh, no ACP CLI execution in CI — live trading is
  droplet-only. Training studies patterns and drills on transcripts.
- No secrets in reports, artifacts or logs.
- **14-day package quarantine (owner, 2026-08-07):** no agent — and no
  training run — installs a package published less than 14 days ago
  (npm, PyPI, crates, GitHub releases). `training/quarantine_pip.py` is the
  enforcement for this workflow's own installs.
- The fleet: iclone, vegeta, doctorwho, doctor-agent, akita-agent,
  forense-ai, supersayatin, matrix, atlas_corporation_okx_ai.
