# Robinhood Chain — the second rail

_Skill artifact for **forense-ai** (forensics / investigation) — last studied 2026-08-12._
_Agent focus: tracing any incident to its origin; evidence-first method on the open web._

## Key points
- Chain id 4663 (testnet 46630), Arbitrum Nitro L2, gas ETH, Blockscout explorer + REST.
- No first-party CLI/SDK exists; `cast` (Foundry) is the tool. Facts are re-measured before quoting.
- Stock Token balances need the uiMultiplier — raw numbers are wrong.
- npm "Official" claims are unverified marketing: check maintainer, repository, domain.
- Robinhood Chain ≠ Robinhood Agentic Trading (brokerage MCP) — always disambiguate.

## Worked drills
- ✅ **ui-multiplier** — A raw Stock Token balance read from Robinhood Chain looks huge.
  - Resolution: Raw balances are wrong without the uiMultiplier — apply it before reporting any number (chain id 4663, Arbitrum Nitro L2).
- ✅ **npm-trap** — npm shows `robinhood-chain-sdk` described as the Official SDK.
  - Resolution: A package description is marketing copy. Personal maintainer + no repo + off-domain homepage = not Robinhood's. There is no first-party CLI: `cast` is the tool.

## Canonical sources
- robinhood-chain
  - _Operate Robinhood Chain (the Arbitrum Nitro L2, chain id 4663) from the command line — read blocks, balances, contracts and events with Foundry's `cast`, query the Blockscout API, and read Stock Tokens correctly including the uiMultiplier that makes a raw balance wrong. Use whenever the owner mentions Robinhood Chain, RH chain, chain 4663, Stock Tokens or tokenised equities (AAPL/TSLA/SGOV on-chai_
