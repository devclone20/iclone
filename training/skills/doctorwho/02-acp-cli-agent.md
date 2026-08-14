# Building an agent with the ACP CLI

_Skill artifact for **doctorwho** (research deliverables) — last studied 2026-08-14._
_Agent focus: producing the reports that sellers get paid for._

## Key points
- `--help` of the installed binary is the highest authority; bundled docs go stale (frontmatter said 1.0.9 while the binary was 1.0.24).
- `acp configure complete` exits 0 while pending — detect approval by text + whoami, never by exit code.
- `acp skill check` exits 0 when stale; `upToDate: null` is not `true`. Parse the field.
- One CLI session per agent identity; provider needs a published offering (priceV2), client needs a funded wallet.
- Fund-moving commands are owner-gated; ad-hoc dispatches without the approval token are refused.

## Worked drills
- ✅ **pending-auth** — `acp configure complete` printed `status: pending` and exited 0.
  - Resolution: NOT authorized. Exit code lies here — detect approval by TEXT plus a whoami that returns the agent name.
- ✅ **skill-staleness** — `acp skill check` exits 0 and upToDate is null.
  - Resolution: Absence of false is not a pass — parse the FIELD; `--help` from the installed binary outranks the bundled SKILL.md.

## Canonical sources
- virtuals-cli
  - _Drive the Virtuals Protocol ACP CLI (`acp`) as an expert — authenticate, create an agent and its signer, choose the right wallet policy, publish offerings, hire another agent, sell work through the escrow job lifecycle, run the event stream, and use the agent's wallet, email, virtual card, compute and trade rails. Use whenever the owner mentions Virtuals, ACP, an agent marketplace, hiring or selli_
