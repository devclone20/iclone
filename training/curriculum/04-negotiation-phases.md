# The negotiation phases — anatomy of one real trade

Every ACP job walks the same trail, and each step has a timestamp that must
match the chain. Case study: **job #70984** (Base mainnet, ACP v2), performed
live by our own fleet on 2026-08-06 — VEGETA (client) hired iCLONE (provider)
for a `tokenResearchDeep` job at $0.10 USDC.

| Phase | Meaning | Case study (UTC) |
| --- | --- | --- |
| `job.created` | client opens the job with its requirement | 17:02:03 |
| `budget.set` | price pinned ($0.10) | 17:02:39 |
| `job.funded` | client's USDC lands in escrow | 17:02:57 |
| `job.submitted` | provider delivers; hash goes on-chain | 17:03:53 |
| `job.completed` | evaluator approves; escrow releases | 17:04:03 |

The proof discipline: the funding transfer landed **at the exact second** of
`job.funded`, and the payout at the second of `job.completed`. The deliverable
hash is on-chain; the completion reason is a bytes32 that decodes to
`Approved`. Settlement: 0.10 funded → 0.09 to the seller, 0.01 protocol fee.
When the ledger and the phase trail tell the same story, the trade is real;
when they diverge, believe the ledger and start debugging.

Negotiation, practically: the client states the requirement precisely
(offering id, subject, format), the price is the offering's — not haggled
mid-job — and the evaluator's verdict is the only thing that moves escrow.

## Key points

- Canonical order: created → budget.set → funded → submitted → completed. Anything else is a red flag.
- Phase timestamps must match the chain to the second (funding tx ↔ job.funded; payout ↔ job.completed).
- Deliverable hash and completion reason live on-chain; `Approved` decodes from bytes32.
- Settlement = price minus 10% protocol fee (0.10 → 0.09 + 0.01).
- Requirements are precise JSON against a published offering; the evaluator, not the parties, releases escrow.

## Sources

- virtuals-cli
- agentic-economy
