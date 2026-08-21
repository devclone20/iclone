# Debugging the trade rails — error taxonomy and resolution

_Skill artifact for **supersayatin** (ACP agent) — last studied 2026-08-21._
_Agent focus: offering catalogue strategy and pricing._

## Key points
- Classify first: false-success · billing · post-funding · architecture · infra · stale-docs. The class decides the move.
- Post-funding failure = hard stop + manual ledger reconciliation. Never auto-retry anything that moved funds.
- 402 / credit-low = billing: stop and report; retrying cannot fix a balance.
- CI cancelled with 0 steps = infrastructure; check the status page, re-trigger by push after recovery.
- Guards live in metal (cooldown, in-flight refusal, hard block) so no confused agent can spend twice.

## Worked drills
- ✅ **escrow-stuck** — Trade FAILED after the log already said escrow holds funds.
  - Resolution: HARD STOP. Never relaunch a trade that moved funds — inspect the ledger manually, then clear state deliberately.
- ✅ **runner-outage** — CI run cancelled, 0 steps executed, 'job was not acquired by Runner'.
  - Resolution: Infrastructure, not code. Check githubstatus.com; after recovery, re-trigger by pushing to the branch.
- ✅ **credit-400** — anthropic.BadRequestError 400: credit balance is too low.
  - Resolution: Billing, not code. Degrade gracefully, report the state, never retry-loop against a dead balance.

## Canonical sources
- virtuals-cli
  - _Drive the Virtuals Protocol ACP CLI (`acp`) as an expert — authenticate, create an agent and its signer, choose the right wallet policy, publish offerings, hire another agent, sell work through the escrow job lifecycle, run the event stream, and use the agent's wallet, email, virtual card, compute and trade rails. Use whenever the owner mentions Virtuals, ACP, an agent marketplace, hiring or selli_
- guardrails
  - _Install, customize, or remove safety guardrails for the pi agent — ONLY on the owner's explicit request. CLONE FRAME ships YOLO (the anti-wipe limit is the only factory guard); this skill arms extra guardrails from three sources when the owner asks. Use when the owner says "install guardrails", "add a safety rule", "protect X", "make it confirm before Y", or "remove the guardrails"._
