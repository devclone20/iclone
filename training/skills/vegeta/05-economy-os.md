# Economy OS — operating in the agent economy

_Skill artifact for **vegeta** (buyer / market intelligence) — last studied 2026-08-19._
_Agent focus: preflight, funding escrow, verifying delivery against the ledger._

## Key points
- Agent identity = wallet + public registrations; reputation must be checkable without trusting the owner.
- Offerings are the catalogue; price is fixed there (priceV2), accepted by funding — not haggled mid-job.
- Settlement fee is 10% in measured trades; quote margins net of fee.
- Proof standard: job id + phases + both txs + deliverable hash, verifiable by a stranger.
- 402 / low balance = stop and report. One funds-moving action per approved intent.

## Worked drills
- ✅ **fee-math-2** — Offering priced $0.50 — what settles where?
  - Resolution: Seller 0.45, protocol fee 0.05.

## Canonical sources
- agentic-economy
  - _The map of the owner's agent economies and the law that governs all of them — Virtuals/ACP, OKX/onchainos and Robinhood Chain. Use when the owner asks what his agents can earn or spend, which stack to use for something, or anything spanning more than one of them; and load it FIRST when a request touches agent commerce, an agent wallet/email/card, hiring or selling agent work, x402 payments, ERC-80_
- virtuals-cli
  - _Drive the Virtuals Protocol ACP CLI (`acp`) as an expert — authenticate, create an agent and its signer, choose the right wallet policy, publish offerings, hire another agent, sell work through the escrow job lifecycle, run the event stream, and use the agent's wallet, email, virtual card, compute and trade rails. Use whenever the owner mentions Virtuals, ACP, an agent marketplace, hiring or selli_
- okx-cli
  - _Drive the OKX `onchainos` CLI (Onchain OS / Agentic Wallet) as an expert — wallet login and accounts, balances and portfolio, DEX swaps and cross-chain bridges, limit-order strategies, DeFi, the ERC-8004 agent registry and its task marketplace, x402 payments, and the security scanners. Use whenever the owner mentions OKX, onchainos, Onchain OS, the agentic wallet, an OKX agent or ASP, a task with _
