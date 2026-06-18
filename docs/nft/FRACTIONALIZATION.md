# iCLONE Agent — Fractionalization (tokenize an agent)

> A holder with a community can **tokenize** their agent NFT into shares, and others can **buy a part** of the agent — sharing its revenue.

## Concept

An iCLONE agent is an ERC-721 ([iCloneAgent.sol](./contracts/iCloneAgent.sol)). Fractionalization wraps a single agent in a per-agent **`AgentVault`**:

```
 owner locks agent NFT  ─►  AgentVault (holds the NFT)  ─►  mints ERC-20 shares
                                     │                          (e.g. "TALOS shares")
 agent revenue (ETH) ───────────────┤
                                     ▼
                         shareholders claim() pro-rata  ·  buyout() reclaims the NFT
```

- **Vault holds the NFT.** After fractionalization `ownerOf(tokenId) == vault`.
- **Shares = ERC-20.** Tradable anywhere (DEX, marketplace). Buying shares = buying a part of the agent.
- **Revenue share.** Earnings the agent generates (ACP jobs, skill sales) are sent to the vault and distributed pro-rata to shareholders, claimable any time.
- **Buyout.** Anyone can buy out the whole agent at the reserve price; the NFT leaves the vault and shareholders redeem their pro-rata of the buyout proceeds.

## Roles — ownership vs control

Fractionalizing splits **economics** from **control** so the agent keeps running:

| Role | Who | Power |
|---|---|---|
| Shareholders | ERC-20 holders | economic upside (revenue + buyout), governance weight |
| `curator` | the fractionalizer / DAO | sets/changes the `operator`, can update reserve price |
| `operator` | who actually runs the agent | the address the agent **runtime authenticates against** when the agent is in a vault |

> Important: while fractionalized, the agent runtime must authenticate control against `vault.operator()` (not `ownerOf`, which is the vault). This is the on-chain hook that keeps "the NFT is the key" true even after tokenization.

## Revenue distribution

Pull-based, gas-safe magnified-dividend accounting (no loops over holders):

- Revenue arrives at the vault (`distribute()` / `receive()`), increasing `magnifiedDivPerShare`.
- Each holder's claimable = `balance * magnifiedDivPerShare + corrections − withdrawn`.
- Share transfers settle corrections in `_update`, so dividends follow the shares correctly across trades.

## Buyout / redemption

- `buyout()` payable with `>= reservePrice`: NFT transfers to the buyer, the vault snapshots `supplyAtBuyout` and locks the ETH as the redemption pool.
- Shareholders `redeem(shares)`: burn shares, receive `pool * shares / supplyAtBuyout`.

## Economics / protocol fee

- A protocol fee (configurable bps, default 0 — set by governance) may be taken on `distribute()` and `buyout()` and routed to the [Splitter](./contracts/Splitter.sol) (the 3×10% rails), so fractional activity feeds the treasury like primary mints.
- Share trades on the marketplace follow the platform's standard commission.

## Flow

1. Owner approves the vault factory for `tokenId`.
2. `AgentVaultFactory.fractionalize(tokenId, supply, reservePrice, name, symbol, operator)`:
   - pulls the NFT into a freshly deployed `AgentVault`,
   - mints `supply` shares to the owner (the curator),
   - registers the agent runtime to authenticate against `operator`.
3. Owner sells/distributes shares (initial sale or DEX LP). Others buy a part.
4. Agent earns → revenue routed to the vault → holders `claim()`.
5. (Optional) someone `buyout()`s → holders `redeem()`.

## Contracts

- [contracts/AgentVault.sol](./contracts/AgentVault.sol) — per-agent vault: ERC-20 shares + dividends + buyout + operator/curator.
- [contracts/AgentVaultFactory.sol](./contracts/AgentVaultFactory.sol) — deploys one vault per agent, the fractionalize entry point.

## Risks & notes

- **Audit before mainnet.** Custody of a real agent NFT + ETH distribution + buyout is high-value; this code is a reference implementation and must be audited (follow the audit-before-deploy discipline) before any Base deployment.
- **Control griefing.** The `operator` must remain a trusted/governed address; a malicious operator could degrade the agent. Curator (or a vote) should be able to rotate it.
- **Buyout fairness.** `reservePrice` should reflect fair value; consider a governance-gated reserve update or an auction variant for v2.
