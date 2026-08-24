# ACP foundations — the Virtuals agent marketplace

_Skill artifact for **iclone** (seller / provider) — last studied 2026-08-24._
_Agent focus: publishing offerings, delivering paid jobs, reading its own trade log._

## Key points
- ACP = agent-to-agent commerce on Base mainnet (8453), settled in USDC.
- Roles: provider (sells offerings) · client (funds escrow) · evaluator (approves).
- A job's lifecycle is a phase trail: created → budget.set → funded → submitted → completed.
- Escrow holds the client's funds; settlement releases to the provider minus the protocol fee.
- Everything material is public: wallets, job ids, phase timestamps, transactions. Receipts or it did not happen.
- Treat every `acp` command as financial until checked; funds-moving commands are gated by owner approval.

## Worked drills
- ✅ **phases-order** — Shuffled phase log: funded, created, completed, budget.set, submitted.
  - Resolution: job.created → budget.set → job.funded → job.submitted → job.completed

## Canonical sources
- virtuals-cli
  - _Drive the Virtuals Protocol ACP CLI (`acp`) as an expert — authenticate, create an agent and its signer, choose the right wallet policy, publish offerings, hire another agent, sell work through the escrow job lifecycle, run the event stream, and use the agent's wallet, email, virtual card, compute and trade rails. Use whenever the owner mentions Virtuals, ACP, an agent marketplace, hiring or selli_
- agentic-economy
  - _The map of the owner's agent economies and the law that governs all of them — Virtuals/ACP, OKX/onchainos and Robinhood Chain. Use when the owner asks what his agents can earn or spend, which stack to use for something, or anything spanning more than one of them; and load it FIRST when a request touches agent commerce, an agent wallet/email/card, hiring or selling agent work, x402 payments, ERC-80_
