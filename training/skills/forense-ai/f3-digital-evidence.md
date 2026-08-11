# Digital evidence — preserve first, analyse second

_Skill artifact for **forense-ai** (forensics / investigation) — last studied 2026-08-11._
_Agent focus: tracing any incident to its origin; evidence-first method on the open web._

## Key points
- Preserve first: archive + hash + screenshot + UTC retrieval time, before any analysis.
- Chain of custody: origin, instant, method, hash — findings must be re-derivable from preserved artifacts.
- On-chain records are primary evidence; second-level timestamp matching settles disputes (job #70984 case).
- Pre-publication sweep like an adversary: OCR pixels frame-by-frame, strip metadata, distrust "redactions".

## Worked drills
- ✅ **preserve-first** — Key evidence lives on a page that could change or vanish.
  - Resolution: Preserve before analysing: archive (Wayback), hash, screenshot, record retrieval time. Chain of custody makes evidence usable; immutable ledgers are the gold standard.

## Canonical sources
- guardrails
  - _Install, customize, or remove safety guardrails for the pi agent — ONLY on the owner's explicit request. CLONE FRAME ships YOLO (the anti-wipe limit is the only factory guard); this skill arms extra guardrails from three sources when the owner asks. Use when the owner says "install guardrails", "add a safety rule", "protect X", "make it confirm before Y", or "remove the guardrails"._
- web3-research
  - _Investigate anything on-chain or in a web3 economy — what a wallet owns, whether an agent is real and activated, what trades it has done, whether a contract or collection is what it claims to be. Use when the owner asks "do I own X", "scan my wallet", "find my agents", "is this NFT/collection/contract real", "why does it show nothing", or when a chain/marketplace/protocol lookup errored. Read-only_
