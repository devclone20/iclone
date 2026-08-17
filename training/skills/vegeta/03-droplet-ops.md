# Trading through a droplet — the remote body pattern

_Skill artifact for **vegeta** (buyer / market intelligence) — last studied 2026-08-17._
_Agent focus: preflight, funding escrow, verifying delivery against the ledger._

## Key points
- ACP CLI is droplet-only; the workstation never holds keys or sessions.
- Long commands kill personas (~120s) — launch detached (transient systemd unit), return in ~1s.
- State is derived from the log: RUNNING / COMPLETE / FAILED / IDLE; `status` is always safe and instant.
- Poll every ~25s with short calls; never hold a connection across a trade.
- Wrapper guard rails: in-flight refusal · post-completion cooldown · hard block after FAILED-post-funding.

## Worked drills
- ✅ **long-bash** — A persona holds one ssh command for 3 minutes and dies around 120s.
  - Resolution: Never hold long commands: launch detached (transient systemd unit), then poll a short `status` every ~25s.
- ✅ **detached-state** — The caller lost its connection mid-trade.
  - Resolution: State is derived from the log file — any new caller recovers the truth via `status` (RUNNING/COMPLETE/FAILED/IDLE).

## Canonical sources
- virtuals-cli
  - _Drive the Virtuals Protocol ACP CLI (`acp`) as an expert — authenticate, create an agent and its signer, choose the right wallet policy, publish offerings, hire another agent, sell work through the escrow job lifecycle, run the event stream, and use the agent's wallet, email, virtual card, compute and trade rails. Use whenever the owner mentions Virtuals, ACP, an agent marketplace, hiring or selli_
- clone-frame-orchestration
  - _Set up a multi-pane iT terminal inside CLONE FRAME and run or coordinate several jobs or agents side by side. Use when the owner asks to "open panes and orchestrate", run things in parallel in the terminal, drive the iT multiplexer, or coordinate multiple agents in the app._
