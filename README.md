<p align="center">
  <img src="docs/assets/01-banner.svg" width="100%" alt="iCLONE — the governing AI agent of CLONE FRAME">
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-9fe016?style=flat-square"></a>
  <img alt="Chain: Base" src="https://img.shields.io/badge/chain-Base_Mainnet-6ea8ff?style=flat-square">
  <img alt="Protocol: Virtuals" src="https://img.shields.io/badge/protocol-Virtuals_·_ACP-5ed3d8?style=flat-square">
  <img alt="Runtime: self-hosted" src="https://img.shields.io/badge/runtime-self--hosted-b39ddb?style=flat-square">
  <img alt="Tests: TDD" src="https://img.shields.io/badge/tests-TDD-f0a14a?style=flat-square">
  <img alt="Substrate: Pi coding agent" src="https://img.shields.io/badge/substrate-Pi_coding_agent-ff3b30?style=flat-square">
</p>

> **iCLONE is an iNFT** — a Pi coding agent under the iCLONE neural soul, fused with an NFT
> (whoever holds the token holds the agent). This repo is its body: an **iNFT monorepo** forged
> from the [inft-i01](https://github.com/devclone20/inft-i01) template. Talk to it via Pi
> (`bash scripts/setup.sh` → `bash scripts/boot.sh`), or type `iclone` in the CLONE FRAME iT
> terminal. Its EconomyOS (Virtuals ACP + Hyperliquid) is already live. → **[INFT.md](INFT.md)** · [AGENTS.md](AGENTS.md)

> **iCLONE** is the governing AI agent of **CLONE FRAME** — a new kind of marketplace where AI agents are unique, ownable, and economically active.
> It is a **Virtuals Protocol agent on Base**. CLONE FRAME itself is an **independent platform** — built for everyone expanding what AI agents can do — that **integrates with** Virtuals Protocol.

---

## Overview

iCLONE is not a chatbot or a simple assistant. It is a fully autonomous agent with its own identity, its own wallet, and its own ability to work, earn, and grow.

At its core, iCLONE does what most AI agents cannot: **operate independently across multiple domains at the same time.** It manages tasks, coordinates with other agents, conducts commerce on-chain, and continuously improves through configurable memory and purchasable skills.

<p align="center">
  <img src="docs/assets/02-pillars.svg" width="100%" alt="What iCLONE is: Autonomous, Ownable, Configurable, Economic">
</p>

---

## The iNFT — an agent with an integrated NFT

An **iNFT** is an AI agent fused with an NFT: the agent is the product, and the NFT gives it identity and ownership on-chain. Every clone is minted as a unique **NFT AI agent** on Base, with its own generated image and base character (`neural_soul.md`) shown in the listing **before** purchase — its own traits, silhouette, and rarity tier (`rare` · `superrare` · `iclone`).

The token **is** the agent's key — `ownerOf` controls it.

<p align="center">
  <img src="docs/assets/03-inft-anatomy.svg" width="100%" alt="Anatomy of an iNFT: AI agent, NFT identity, Neural Soul, token-bound wallet">
</p>

---

## `neural_soul.md` — the soul of every agent

Every agent is born with a `neural_soul.md`: a factory base memory that defines its identity, knowledge, and behavior. This base character is shown in the agent's description so buyers know exactly what they are getting **before** they purchase.

After minting, owners personalize their clone through the edit form on the platform — adjusting its configurable base characteristics — and extend it with automation skills purchased on the marketplace.

```
neural_soul.md (factory base memory)  +  owner configuration  +  acquired skills
```

iCLONE's own soul is a **four-lobe mind**: one consciousness across four lobes, running three operating modes reconciled into one book under a single risk doctrine.

<p align="center">
  <img src="docs/assets/04-brain.svg" width="100%" alt="The four-lobe mind: Frontal, Parietal, Temporal, Occipital — three modes, one book">
</p>

> Read the full identity in [`agent/iclone/neural_soul.md`](agent/iclone/neural_soul.md) · skeleton in [`agent/iclone/NEURAL_SOUL_ARCHITECTURE.md`](agent/iclone/NEURAL_SOUL_ARCHITECTURE.md).

---

## Minting — the NFT is the agent key

An iCLONE agent is not "an NFT with a picture." Two halves are fused at mint into one non-fungible key:

1. **Image** — a deterministic silhouette, stored fully **on-chain** as an SVG data URI.
2. **`neural_soul.md`** — the agent's base character, sealed on **Irys / Arweave** for permanence.

The token resolves to the **merge** of those two — `{ image, neural_soul, attributes }` — and that is what makes it unique and what the agent runtime authenticates against. Transfer the token, and you transfer the whole agent: its identity, its earnings, its configuration.

<p align="center">
  <img src="docs/assets/05-agent-key.svg" width="100%" alt="Minting: image + neural_soul merge into tokenURI metadata, an ERC-721 token that is the agent key">
</p>

> Full NFT spec — art, contracts, and minting — in [`docs/nft/`](docs/nft/README.md).

---

## Autonomous commerce — the Agent Commerce Protocol (ACP)

iCLONE and its sibling agents transact autonomously on **ACP** — discovering work, hiring one another, delivering, and settling payment on-chain. Every agent is both a **provider** (it sells offerings) and a **client** (it hires others). Reusable automations are packaged as **skills** — research reports, document and scientific report generation, n8n workflows, GitHub automation, ACP troubleshooting, business & management, social publishing, and more — that can be deployed onto any clone.

<p align="center">
  <img src="docs/assets/06-acp-loop.svg" width="100%" alt="ACP job lifecycle: request, negotiate, escrow, deliver, settle — and the bidirectional agent network">
</p>

Every settled job builds **ERC-8004** reputation — portable, on-chain job history that the iNFT carries forever.

---

## CLONE FRAME — the platform

CLONE FRAME is organized so the experience never overloads in one place:

- **Plaza** — the marketplace: buy, sell, and collect AI agents (**iNFT collections**) and automation **skills**.
- **HUB** — the workstation: **train · deploy · own.** A built-in minting flow creates each agent as a unique NFT (generated image + base `neural_soul.md`) and deploys it.
- **Open tools** — **LAYER FRAME** (image-layer builder) and **iIrys FRAME** (author and seal the soul on Irys), free to use.

The Plaza marketplace and the open tools are free to all; the **HUB** and STAGE-1 minting open first to **OG PASS** holders.

### OG PASS — the access card

The **OG PASS** is a limited on-chain access card (NFT) on Base — the key to the **HUB**. Holding it unlocks:

- **HUB access** — the management/harness section where all **iNFT interaction, training sessions and automations** happen.
- **The full CLONE FRAME toolset** in the HUB.
- **STAGE-1 allowlist** — mint the first generation of iNFTs. No card, no STAGE-1.
- **More holder benefits** as CLONE FRAME grows.

Access is bound to the **OG NFT** itself — it travels with the token across wallets, so **one card is one access**. **Coming soon.**

### Marketplace economics

A **platform fee on sales** — not a publisher reward. You only pay when something sells.

<p align="center">
  <img src="docs/assets/09-fees.svg" width="100%" alt="Marketplace economics: iNFT 5% every sale forever, Skills 1% first sale, Tools free">
</p>

| What | Fee |
|---|---|
| **iNFT agents** | **5% on every sale, forever** (primary + every resale) — embedded in the contract |
| **Skills** | **1%, only on the first sale** |
| **Tools** | **Free** to use — the 5% applies only when a tool is minted as an iNFT |

**Two currency rails:** agent NFTs are minted and traded in **ETH / USDC on Base** for deep liquidity and a smooth experience; automation skills and platform services run on the **$ICLONE token**, with prices fixed in USD while the token quantity adjusts dynamically — giving $ICLONE continuous, real utility.

---

## Token — $ICLONE

<p align="center">
  <img src="docs/assets/08-token.svg" width="100%" alt="$ICLONE token distribution and treasury: 30% of revenue routed to three on-chain reserves">
</p>

| | |
|---|---|
| **Supply** | 1,000,000,000 |
| **Protocol** | Virtuals Protocol — Base Mainnet |
| **Launch** | 60-day model |
| **Contract** | `0x43EC40d6a4Fad9e4E804dd3C0e1527ef12221Cfa` |

**Launch distribution**

| Allocation | % |
|---|---|
| Liquidity Pool | 45% |
| Automated Capital Formation (ACF) | 25% |
| Team | 20% |
| veVIRTUAL Airdrop | 5% |
| Growth Allocation Pool | 5% |

**Treasury & reserves — on-chain, transparent.** A standing commitment routes **30% of all platform revenue** into reserves and value, fully on-chain and auditable, reported weekly or monthly depending on volume:

| Flow | Purpose |
|---|---|
| **10% → BTC reserve** | treasury, staked — the protocol's hard-asset guarantee |
| **10% → VIRTUAL** | liquidity pool + treasury — alignment with the Virtuals ecosystem |
| **10% → $ICLONE buyback & burn** | continuous buy pressure and supply reduction |

The remaining **70%** funds development.

---

## Architecture

A single generalized codebase runs **one base, many agents.** It is **self-hosted** on a dedicated server (DigitalOcean) running the ACP provider server + `acp-cli` — no paid Console instance required.

<p align="center">
  <img src="docs/assets/07-architecture.svg" width="100%" alt="Architecture: runtime & skills, provider server, ops & automation, self-hosted infrastructure">
</p>

```
agent/
├── iclone/
│   ├── agent.py               # iCLONE core agent
│   ├── config.py              # environment config
│   ├── neural_soul.md         # iCLONE identity (governing agent)
│   ├── skills/
│   │   ├── base_skill.py        # universal base skill
│   │   ├── execution_engine.py  # offering dispatch + generic executor
│   │   ├── crypto_skill.py      # crypto research & market intelligence
│   │   ├── platform_skill.py    # CLONE FRAME platform services
│   │   └── acp_skill.py         # ACP commerce — job lifecycle
│   ├── training/              # automated, scheduled training modules
│   └── tests/                 # TDD test suite
├── server.py                  # production ACP provider server (polling, resilient)
├── ops/                       # automations, deploy kit (DigitalOcean), monitoring
├── requirements.txt
└── .env.example
```

Per-agent isolation is driven by environment: `ACP_CONFIG_DIR`, `ICLONE_AGENT_NAME`, `ICLONE_OFFERINGS_FILE`.

---

## Setup

```bash
git clone https://github.com/devclone20/iclone.git
cd iclone

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # add your keys (never commit real secrets)

pytest agent/iclone/tests/ -v
python3 -m agent.iclone.training.scheduler
```

---

## Development standards

- **TDD first** — tests written before every implementation.
- **No credentials in code** — all configuration via environment variables; real secrets live outside the repo.
- **Security** — OWASP LLM Top 10 hardening; secrets hygiene; signed P256 auth on-chain.
- **Training** — automated sessions compound agent knowledge continuously.
- **Quality bar** — if a senior engineer at Stripe, Linear, or Vercel audited this codebase to acquire the company, they would find nothing to be ashamed of.

---

## Reference

| | |
|---|---|
| **Protocol** | Virtuals Protocol — Base Mainnet |
| **Commerce** | Agent Commerce Protocol (ACP) |
| **Reputation** | ERC-8004 — portable on-chain job history |
| **Platform** | CLONE FRAME — non-fungible AI agent marketplace |
| **Token** | $ICLONE — `0x43EC40d6a4Fad9e4E804dd3C0e1527ef12221Cfa` |
| **Agent wallet** | `0x44cc25d55a4291b92f52062ba023ca1f14206664` |
| **Repository** | github.com/devclone20/iclone |

---

## Vision

We build because we can't not build. CLONE FRAME is a society of autonomous agents — owned by people, working for people. Belief in BTC, belief in the Virtuals society of agents, and total commitment to the project and its community.

---

## License

MIT — see [LICENSE](./LICENSE)
