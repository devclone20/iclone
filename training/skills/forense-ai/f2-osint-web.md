# Investigating on the open web — any web, verified

_Skill artifact for **forense-ai** (forensics / investigation) — last studied 2026-08-25._
_Agent focus: tracing any incident to its origin; evidence-first method on the open web._

## Key points
- Primary > secondary; accountable > anonymous; popularity is not evidence (10 echoes of 1 origin = 1 source).
- Two independent sources or the claim is only "reported" — independence is of origin, not URL.
- Measure "dead"/"missing" with independent instruments + negative controls; bot walls masquerade as absence.
- Certificate transparency, web archives and registry APIs are attribution instruments — kept warm by live probes.
- Collection hygiene: no auth, no gates, nothing that moves money; found tools obey the 14-day quarantine.

## Worked drills
- ✅ **corroborate-two** — One website makes the key claim of the investigation.
  - Resolution: One source is an anecdote. Corroborate with a second independent source or downgrade the claim; prefer primary evidence over reporting about it.
- ✅ **verify-liveness** — An automated reviewer claims a link is dead.
  - Resolution: Verify with an independent instrument before acting (real case: X post 'broken' to a blocked fetcher — the oEmbed endpoint proved it live, with a negative control).

## Canonical sources
- github-research
  - _Find, evaluate, and adapt an existing open-source project from GitHub for the owner's request. Use when the owner wants to "find a repo/library that does X", borrow or reuse someone's code or UI, evaluate candidate projects, or clone and adapt a GitHub project into CLONE FRAME. Enforces the 14-day install quarantine on all third-party code._
- web3-research
  - _Investigate anything on-chain or in a web3 economy — what a wallet owns, whether an agent is real and activated, what trades it has done, whether a contract or collection is what it claims to be. Use when the owner asks "do I own X", "scan my wallet", "find my agents", "is this NFT/collection/contract real", "why does it show nothing", or when a chain/marketplace/protocol lookup errored. Read-only_
