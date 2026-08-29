# iCLONE Agent NFT

> The NFT **is** the agent. Whoever holds the token owns the AI agent and governs everything inside it.

This folder documents how an iCLONE agent becomes a unique, non-fungible on-chain asset, and how the art + soul are fused into a single token.

> **The launch is multi-chain.** The collection lands first on **Robinhood Chain** (chain ID 4663, an Arbitrum-Orbit L2 — [docs.robinhood.com/chain](https://docs.robinhood.com/chain/connecting)), then on **Base** (Ethereum L2, chain ID 8453), with further chains after those. The contracts, art pipeline and mint flow below are written against **Base**; `identity.json` carries the authoritative chain block.

## The core idea — NFT = agent key

An iCLONE agent is not "an NFT with a picture". The token is the **control key** of a living agent:

- `ownerOf(tokenId)` is the sole controller of that agent. Transfer the token → transfer the agent (its identity, its earnings, its config).
- Two halves are fused at mint into one non-fungible key:
  1. **Image** — a deterministic silhouette (generated in the Image Lab / Silhouette engine), stored fully **on-chain** as an SVG data URI. See [ART.md](./ART.md).
  2. **`neural_soul.md`** — the agent's base character (identity, knowledge, behaviour), pinned to **Arweave** for permanence.
- The metadata that the token resolves to is the **merge** of those two: `{ image, neural_soul, attributes }`. That merged object is what makes the token unique and what the agent runtime authenticates against.

```
 image (on-chain SVG)  ─┐
                        ├─►  tokenURI metadata  ─►  ERC-721 token  ═  agent key
 neural_soul.md (AR)   ─┘        (the merge)            (Base)        (ownerOf = controller)
```

## Index

- [ART.md](./ART.md) — silhouette engine, rarity tiers, 10 base concepts, accessories.
- [MINTING.md](./MINTING.md) — the mint pipeline, the Image Lab integration, the soul↔image merge, batch minting.
- [FRACTIONALIZATION.md](./FRACTIONALIZATION.md) — tokenize an agent into shares; others buy a part and share revenue.
- [contracts/iCloneAgent.sol](./contracts/iCloneAgent.sol) — the ERC-721 + genome + royalties.
- [contracts/Splitter.sol](./contracts/Splitter.sol) — the 3×10% treasury split.
- [contracts/AgentVault.sol](./contracts/AgentVault.sol) — per-agent fractional vault (ERC-20 shares + revenue share + buyout).
- [contracts/AgentVaultFactory.sol](./contracts/AgentVaultFactory.sol) — fractionalize entry point.

## Decisions (Base / ETH)

| Layer | Decision | Why |
|---|---|---|
| Standard | ERC-721 (1/1), OpenZeppelin `ERC721URIStorage` + ERC-2981 + `Ownable` + `ReentrancyGuard` | Audit-grade, no vendor lock-in; gas on Base is already cheap |
| Minting | `viem` + `wagmi`, self-hosted, no thirdweb SDK | Typed, already in the stack |
| Art | Deterministic SVG silhouettes, 100% on-chain | Permanent, cheap, on-brand, no IPFS dependency for art |
| Soul | `neural_soul.md` on Arweave, CID in metadata | Permanence of the agent's base character |
| Currency | Agents in ETH/USDC on Base | Liquidity (skills stay on iCLONE token) |
