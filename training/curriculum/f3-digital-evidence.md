# Digital evidence — preserve first, analyse second

Evidence that was not preserved at collection time is testimony, not
evidence. Forense's discipline:

**Preserve before analysing.** The moment something matters: archive the
page (Wayback), save the raw file, hash it, screenshot it, and record the
retrieval instant in UTC. A page can change or vanish between your first
read and your report — the preserved copy is what your findings stand on.

**Chain of custody.** Every artifact carries: where it came from (exact
URL/path), when it was taken, how (tool + parameters), and its hash. A
finding whose evidence cannot be re-derived from preserved artifacts does
not survive review.

**Immutable ledgers are the gold standard.** When an investigation touches
on-chain activity, the chain *is* the primary record: this fleet proved a
disputed trade real by matching phase timestamps to transaction timestamps
to the second, and answered a "2026 dates must be a typo" challenge by
pointing at the ledger — the receipts outrank anyone's intuition, including
a reviewer's.

**Publication is exposure.** Before any evidence goes public, sweep it as
an adversary would: pixels carry secrets (screen recordings get
frame-by-frame OCR audits here — grep is blind to images), metadata carries
paths and names, and a "redacted" PDF often isn't. What leaves the lab is
what a stranger may keep forever.

## Key points

- Preserve first: archive + hash + screenshot + UTC retrieval time, before any analysis.
- Chain of custody: origin, instant, method, hash — findings must be re-derivable from preserved artifacts.
- On-chain records are primary evidence; second-level timestamp matching settles disputes (job #70984 case).
- Pre-publication sweep like an adversary: OCR pixels frame-by-frame, strip metadata, distrust "redactions".

## Sources

- guardrails
- web3-research
