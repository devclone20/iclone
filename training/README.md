# Fleet training system

One training system for the whole devclone20 agent fleet. Replaces the
legacy Day A / Day B workflows and the per-tool-repo trainings (2026-08-07).

## How it works

- **Schedule:** Mon/Wed/Fri 05:00 UTC (`.github/workflows/training.yml`),
  plus manual `workflow_dispatch`.
- **Engine:** `training/engine.py` — deterministic core. Each session, every
  agent studies the next 2 curriculum modules (cycling through 7), runs the
  attached drills, and gets its skill artifacts refreshed under
  `training/skills/<agent>/`. Per-agent progress lives in `training/state/`.
- **Curriculum:** `training/curriculum/` — ACP/Virtuals foundations, the ACP
  CLI, droplet trading ops, negotiation phases, Economy OS, Robinhood Chain,
  and debugging. Canonical sources are the public skill files in
  `devclone20/cloneframe_app_executable` (checked out read-only at run time).
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
- The fleet: iclone, vegeta, doctorwho, doctor-agent, akita-agent,
  forense-ai, supersayatin, matrix, atlas_corporation_okx_ai.
