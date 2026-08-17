# The negotiation phases — anatomy of one real trade

_Skill artifact for **doctorwho** (research deliverables) — last studied 2026-08-17._
_Agent focus: producing the reports that sellers get paid for._

## Key points
- Canonical order: created → budget.set → funded → submitted → completed. Anything else is a red flag.
- Phase timestamps must match the chain to the second (funding tx ↔ job.funded; payout ↔ job.completed).
- Deliverable hash and completion reason live on-chain; `Approved` decodes from bytes32.
- Settlement = price minus 10% protocol fee (0.10 → 0.09 + 0.01).
- Requirements are precise JSON against a published offering; the evaluator, not the parties, releases escrow.

## Worked drills
- ✅ **fee-math** — Buyer funds a $0.10 USDC escrow; job completes Approved.
  - Resolution: Seller receives 0.09, protocol fee 0.01 (10% at settlement).
- ✅ **ledger-match** — Do the phase timestamps match the chain?
  - Resolution: Yes and they must: funding tx lands at the second of job.funded, payout at job.completed (case study: job #70984 on Base).

## Canonical sources
- virtuals-cli
  - _Drive the Virtuals Protocol ACP CLI (`acp`) as an expert — authenticate, create an agent and its signer, choose the right wallet policy, publish offerings, hire another agent, sell work through the escrow job lifecycle, run the event stream, and use the agent's wallet, email, virtual card, compute and trade rails. Use whenever the owner mentions Virtuals, ACP, an agent marketplace, hiring or selli_
- agentic-economy
  - _The map of the owner's agent economies and the law that governs all of them — Virtuals/ACP, OKX/onchainos and Robinhood Chain. Use when the owner asks what his agents can earn or spend, which stack to use for something, or anything spanning more than one of them; and load it FIRST when a request touches agent commerce, an agent wallet/email/card, hiring or selling agent work, x402 payments, ERC-80_
