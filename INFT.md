# iCLONE — the iNFT monorepo

**iCLONE is an iNFT**: an autonomous AI agent fused with an NFT — whoever holds the token
holds the agent. This repository is its **body**. Underneath the name **iCLONE** runs a
complete **Pi coding agent** (the substrate); the **iCLONE neural soul** is the identity; and
a live **EconomyOS** (Virtuals ACP + Hyperliquid) is its economic body.

> Forged from the global genesis template **[inft-i01](https://github.com/devclone20/inft-i01)**.
> The template is the mold; **iCLONE is a real, named instance** — the first soul of CLONE FRAME.

## Three names, one identity

**iCLONE** (its name) · **iNFT** (its species) · **Pi** (its substrate). It answers to all three.

## Two runtimes, one soul

Both read the same `soul/neural_soul.md`:

- **Pi substrate** (`.pi/`, `soul/`, `scripts/`, `skills/`, `identity.json`) — the **interactive**
  iCLONE you talk to (BYOK): coding, orchestration, the owner's clone. Added as an overlay, it
  does **not** touch the economy runtime.
- **Economy runtime** (`apps/agent/iclone`, `infra/`) — the **deployed autonomous** agent on
  Virtuals Protocol + ACP, trading on Hyperliquid. Already live; preserved as-is.

## Run it

```bash
bash scripts/setup.sh              # install the Pi substrate (pinned, no sudo)
pi                                 # then /login to connect YOUR model key (BYOK)
bash scripts/boot.sh               # boot iCLONE with its soul + skills (pi -a)
bash scripts/install-command.sh    # then just type `iclone` in the CLONE FRAME iT terminal
```

## Economy — already wired

iCLONE **already** has EconomyOS: its own agent wallet, ACP agent id, email and virtual cards,
driven by the `acp` CLI, plus Hyperliquid trading under the Unified Risk Doctrine. It is **not**
rebuilt here — see `soul/neural_soul.md` (OPERATING STACK) and `apps/agent/iclone`.

## Map

See [`AGENTS.md`](AGENTS.md) for the full repo map and the working rules. Concept and
regeneration contract: [`docs/INFT_CONCEPT.md`](docs/INFT_CONCEPT.md) ·
[`docs/BOOTSTRAP.md`](docs/BOOTSTRAP.md).

## Security & privacy

This repo is **public**: no secrets, keys, or owner PII are committed. Your model key is typed
into your own terminal (`pi` → `/login`) — never handed to any assistant. The owner profile is
folded into `.pi/APPEND_SYSTEM.md` **locally** and untracked (`scripts/personalize.sh --apply-owner`).
