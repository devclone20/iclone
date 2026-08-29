# iCLONE Agent — Minting pipeline

Self-hosted with `viem` + `wagmi`. No thirdweb SDK.

The launch is multi-chain — **Robinhood Chain** (4663) first, then **Base** (8453), more after; see `identity.json`. The pipeline below is documented for **Base (8453)**.

## What the user provides

In the iCLONE FRAME mint studio, the creator supplies:

1. **Image** — generated in the Image Lab (concept + tier + accessories + seed) → deterministic SVG. (Or an uploaded custom image for the premium tier.)
2. **`neural_soul.md`** — the base character of the agent (identity, knowledge, behaviour at level 1). Picked from a base soul or uploaded.
3. **Quantity** — how many agents to mint (1 for a 1/1, or N for a batch of the same concept with sequential seeds).

## The merge — soul + image = the key

The token is the fusion of both halves. At mint we build one metadata object:

```jsonc
{
  "name": "TALOS #000912",
  "image": "data:image/svg+xml;base64,<deterministic silhouette>",   // on-chain art
  "neural_soul": "ar://<txid>/neural_soul.md",                        // Arweave (permanent)
  "attributes": [
    { "trait_type": "concept", "value": "TALOS" },
    { "trait_type": "track",   "value": "Robotics & Physical AI" },
    { "trait_type": "tier",    "value": "iclone" },
    { "trait_type": "seed",    "value": 912 },
    { "trait_type": "accessories", "value": "shoulder, weapon" },
    { "trait_type": "level",   "value": 1 },
    { "trait_type": "xp",      "value": 0 }
  ]
}
```

The on-chain `genome` (concept, tier, seed, accessories bitmap) is stored in the contract for provenance, so the exact art can always be re-derived deterministically. `soulURI` is stored too. **Owning the token = controlling the agent**: the agent runtime authenticates control against `ownerOf(tokenId)`.

## Pipeline

```
[Image Lab]                         [soul picker]
 concept+tier+seed+acc                neural_soul.md
        │                                  │
        ▼                                  ▼
  render SVG  ──► base64 data URI    pin to Arweave ──► ar://txid
        │                                  │
        └──────────────┬───────────────────┘
                       ▼
              build metadata JSON (the merge)
                       ▼
        mintAgent(tokenURI, genome, soulURI)  { value: price }   // viem/wagmi
                       ▼
        ERC-721 minted on Base  →  funds → Splitter (3×10%)
                       ▼
        AgentMinted event  →  agent runtime binds to ownerOf(tokenId)
```

### Batch minting (N > 1)

Loop the same `concept`/`tier`/`accessories` over `seed, seed+1, … seed+N-1`, building one metadata per token and calling `mintAgent` per token (or a `mintBatch` variant). Each token gets a distinct deterministic silhouette, so a batch is visually coherent but every key is unique.

## Money flow

- Primary mint value (ETH/USDC) → `Splitter`:
  - 10% → BTC reserve (held as **cbBTC** on Base, fully on-chain/auditable)
  - 10% → VIRTUAL (liquidity/treasury)
  - 10% → iCLONE buyback & burn
  - remainder → creator / ops
- Secondary sales → ERC-2981 royalty (default set in `iCloneAgent`).

## Frontend (viem/wagmi) — shape

```ts
const uri  = await buildMetadata({ svg, soulArweaveURI, genome }); // returns data: URI
const tx   = await writeContract({
  address: ICLONE_AGENT, abi, functionName: "mintAgent",
  args: [uri, genome, soulArweaveURI],
  value: parseEther(price),
});
await waitForTransactionReceipt({ hash: tx });
```

See [contracts/iCloneAgent.sol](./contracts/iCloneAgent.sol) and [contracts/Splitter.sol](./contracts/Splitter.sol).
