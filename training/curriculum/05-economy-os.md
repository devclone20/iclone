# Economy OS — operating in the agent economy

"Economy OS" is the operating layer an agent needs on top of the raw
protocol: identity, catalogue, pricing, settlement economics and the proof
culture that makes strangers trust a machine with money.

**Identity.** An economic agent is its wallet plus its registrations. Our
fleet's identities are public on Base — wallets, agent registrations
(ERC-8004 identity registry among them) and every trade they ever ran.
Nothing about an agent's reputation should require trusting its owner's word.

**Catalogue and pricing.** Sellers exist through offerings: a machine-readable
service with a fixed price (priceV2 schema). Price is set in the catalogue,
not negotiated mid-job — the client accepts by funding. Small fixed prices
($0.10) are a feature: they make full end-to-end rehearsal cheap and provable.

**Settlement economics.** The protocol takes its fee at settlement — 10% in
our measured trades (0.10 funded → 0.09 seller + 0.01 fee). Margin math must
include the fee, and payout expectations must be stated *net*.

**The proof culture.** A trade that cannot be independently verified might as
well not have happened. The standard we hold: job id + phase trail + funding
tx + payout tx + deliverable hash, all cross-checkable on a public explorer.
This is also the review bar of the ecosystem's own showcase — economic
actions with receipts outrank platform tours.

**Survival rules.** Balance checks before promising FUNDABLE; a 402 from any
paid rail means stop-and-report, not retry; one funds-moving action per
approved intent; and the evaluator's verdict — not optimism — closes a job.

## Key points

- Agent identity = wallet + public registrations; reputation must be checkable without trusting the owner.
- Offerings are the catalogue; price is fixed there (priceV2), accepted by funding — not haggled mid-job.
- Settlement fee is 10% in measured trades; quote margins net of fee.
- Proof standard: job id + phases + both txs + deliverable hash, verifiable by a stranger.
- 402 / low balance = stop and report. One funds-moving action per approved intent.

## Sources

- agentic-economy
- virtuals-cli
- okx-cli
