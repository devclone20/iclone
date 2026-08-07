# Robinhood Chain — the second rail

Robinhood Chain is an **Arbitrum Nitro L2, chain id 4663** (testnet 46630),
gas in ETH, data availability via Ethereum blobs. It carries tokenised
equities ("Stock Tokens": AAPL, TSLA, SGOV on-chain). Explorer + REST API:
Blockscout at `robinhoodchain.blockscout.com`.

**There is no first-party CLI — and that is the design.** Robinhood ships no
CLI and no SDK; their own tutorials prescribe Foundry/Hardhat, and their
engineers push chain metadata upstream into viem/chainlist. The tool is
Foundry's **`cast`**: read blocks, balances, contracts and events like on any
EVM chain. The only first-party developer surface is a read-only REST API.

**The uiMultiplier trap.** A raw Stock Token balance is wrong until the
token's `uiMultiplier` is applied. Reporting a raw number as a holding is a
factual error — apply the multiplier, and say which network (mainnet 4663 vs
testnet 46630) a number came from.

**The npm trap.** Packages exist whose descriptions claim to be the
"Official" Robinhood Chain SDK — personal maintainer, no repository,
homepage off the vendor's domain. A package description is marketing copy
written by whoever published it. Check maintainer, repo, and domain before
installing anything that will touch chain reads, let alone a wallet.

**Don't confuse the rails.** Robinhood Chain (this L2) is unrelated to
Robinhood's "Agentic Trading" brokerage product (an OAuth-gated MCP server
trading equities in a segregated account). If the owner says "Robinhood's AI
agents", ask which one before answering.

## Key points

- Chain id 4663 (testnet 46630), Arbitrum Nitro L2, gas ETH, Blockscout explorer + REST.
- No first-party CLI/SDK exists; `cast` (Foundry) is the tool. Facts are re-measured before quoting.
- Stock Token balances need the uiMultiplier — raw numbers are wrong.
- npm "Official" claims are unverified marketing: check maintainer, repository, domain.
- Robinhood Chain ≠ Robinhood Agentic Trading (brokerage MCP) — always disambiguate.

## Sources

- robinhood-chain
