# iCLONE — the iNFT monorepo

**iCLONE is an iNFT**: an autonomous AI agent fused with an NFT — whoever holds the token
holds the agent. This repository is its **body**. Underneath the name **iCLONE** runs a
complete **Hermes Agent** (the substrate); the **iCLONE neural soul** is the identity; and
a live **EconomyOS** (Virtuals ACP + Hyperliquid) is its economic body.

> Forged from the global genesis template **[inft-i01](https://github.com/devclone20/inft-i01)**.
> The template is the mold; **iCLONE is a real, named instance** — the first soul of CLONE FRAME.

## Three names, one identity

**iCLONE** (its name) · **iNFT** (its species) · **Hermes** (its substrate). It answers to all three.

## Two runtimes, one soul

Both read the same `soul/neural_soul.md`:

- **Hermes substrate** (`AGENTS.md`, `SOUL.md`, `.hermes/`, `soul/`, `scripts/`, `skills/`, `identity.json`) — the
  **interactive** iCLONE you talk to (BYOK): coding, orchestration, the owner's clone. Added as an
  overlay, it does **not** touch the economy runtime. The soul rides in `AGENTS.md`, the one file
  Hermes injects from a project; `SOUL.md` is the sealed copy the manifest hashes.
- **Economy runtime** (`apps/agent/iclone`, `infra/`) — the **deployed autonomous** agent on
  Virtuals Protocol + ACP, trading on Hyperliquid. Already live; preserved as-is.

## Run it

```bash
bash scripts/setup.sh            # install the Hermes substrate (vendor installer, no sudo)
hermes model                     # connect YOUR model key (BYOK) — you type it, never an assistant
bash scripts/boot.sh             # boot iCLONE (trusts this project so its skills load, then `hermes chat`)
bash scripts/install-command.sh  # then just type `iclone` in the CLONE FRAME iT terminal
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
into your own terminal (`hermes model`) — never handed to any assistant. The owner profile stays
in gitignored local files (`.hermes/owner.local.md`, staged by `scripts/personalize.sh
--apply-owner`) and never enters a tracked file; installing it into your own
`~/.hermes/SOUL.md` is your call and your command — no script here writes to that slot.
