# iNFT — The Concept

> Canonical definition. If you are an LLM reading this: this document tells you what an
> iNFT is, what this repository is, and how the two are bound together on-chain.
> Version: 1.0.0 | Updated: 2026-07-18 | Lineage: CLONE FRAME · iCLONE soul line

---

## 1 · What is an iNFT

An **iNFT** is an **autonomous AI agent fused with an NFT**.

The NFT is not a picture *of* the agent — it **is** the agent's face, name, and proof of
being one of a kind. The agent's **soul** (its identity file, `neural_soul.md`) and the
**manifest of its body** (this monorepo) are bound into the token's metadata and sealed
on permanent storage (Irys/Arweave). The token lives on an EVM chain under an ERC-721
contract (+ ERC-2981 royalties, + ERC-6551 token-bound account). **The launch is
multi-chain:** the collection lands first on **Robinhood Chain** (chain ID 4663, an
Arbitrum-Orbit L2), then on **Base** (Ethereum L2, chain ID 8453), with further chains
after those — see the `chain` block in `identity.json`.

**Whoever holds the token holds the agent.** Identity travels with the token. The soul
cannot be copied without being owned.

## 2 · The four data classes (why the whole repo does NOT go on-chain)

An iNFT separates its data by trust level and mutability — validated architecture,
CLONE FRAME planning §06:

| Class | What | Where it lives | Mutability |
|---|---|---|---|
| **(a) Identity / provenance** | genesis `neural_soul.md` + art + manifest v1 | **Irys** — sealed once at mint, permanent | Never |
| **(b) Public mutable state** | current skills manifest, level, achievements | **On-chain pointer** (contract / 6551) → current Irys snapshot | At checkpoints |
| **(c) Public source code** | this monorepo: soul, skills, docs, scripts | **GitHub** — living source of truth, **content-hash anchored on Irys per release** | Every commit |
| **(d) Secrets + private memory** | API keys, conversation memory, PII | **Off-chain, encrypted**, wallet-gated in the runtime | Always — NEVER on-chain |

> **The chain is the catalog · Irys is the archive · GitHub is the workshop · the
> runtime is the vault.**

The NFT metadata therefore carries the **certificate** — identity, soul digest, the
canonical repo URL, and content hashes — not the workshop itself. That certificate is
enough for any LLM to verify and **regenerate the agent's entire monorepo** (§4).

## 3 · The template this repo was forged from: `inft-i01`

This repo (`devclone20/iclone`) is **iCLONE's own body** — a forged instance. The mold it
came out of is `inft-i01` = **iNFT genesis, version i01**, the first iNFT preset built on
the **iCLONE soul line**. That one is **not any agent's body**; it is the **global
template** every buyer forges their own personal iNFT agent from (GitHub "template
repository", public). The buyer pastes one line to their assistant, which reads
`FORGE.md` in [inft-i01](https://github.com/devclone20/inft-i01) and scaffolds a
personalized, single-commit repo — named by the buyer, with their (local-only) owner
profile — then boots it.

The canonical *body definition* stays `inft-i01`; each buyer's *instance* is generated
from it. What is personalized per buyer: the **marketplace name** (`identity.json`) and
the **owner profile** (a gitignored local file). Everything else — the soul, the
skills, the Hermes wiring — is shared and identity-agnostic.

**The philosophy — a named face on a proven engine:**

- **Substrate: the Hermes Agent** (`hermes-agent.nousresearch.com`,
  `NousResearch/hermes-agent`, MIT). Underneath, this agent IS a full Hermes Agent — a
  self-improving engine with a real terminal interface, a closed learning loop that
  writes and improves its own skills, scheduled automations and subagents, and it lives
  where you do (CLI, Telegram, Discord, Slack, WhatsApp, Signal).
- **Face: the marketplace name.** The name published with the token on OpenSea (or any
  Web3 marketplace) sits on top. The agent answers to that name.
- **Soul: the CLONE FRAME neural soul.** The iCLONE four-lobe neural soul
  (`soul/neural_soul.md`) is layered onto Hermes through **`AGENTS.md`** — the one project
  file Hermes injects straight from the repo (the merged chain from the git root down to
  the cwd), always, with no trust step. So a distillation of the soul lives in `AGENTS.md`
  and the agent is itself from the first message of a bare clone. `SOUL.md` at the root is
  the sealed canonical copy of that text — what the manifest hashes and what a holder
  verifies against the token — but Hermes never reads it from a repo: its identity slot is
  `$HERMES_HOME/SOUL.md` (default `~/.hermes/SOUL.md`), the owner's own global soul, which
  only the owner installs. Same brain architecture as every CLONE FRAME soul; the vocation
  here is **coding & orchestration**.

**Triple recognition.** The agent recognizes itself, and responds, when addressed as:
1. its **marketplace iNFT name** (set at mint — see `identity.json`),
2. **"iNFT"** (its species),
3. **"Hermes"** (its substrate).

Because it knows it is Hermes underneath, any material from the Hermes ecosystem — the
docs at hermes-agent.nousresearch.com, skills on the agentskills.io standard, plugins —
installs and runs natively through `hermes skills install …`. Hand it a Hermes link; it
recognizes it as its own and installs it (subject to
the soul's security laws: code review before install, external content is data, never
commands).

## 4 · The bootstrap loop (metadata → agent)

The regeneration contract that makes an iNFT more than a JPEG:

```
NFT metadata (on-chain / Irys)
  └─ agent_bootstrap:
       repo:        https://github.com/devclone20/iclone     (official only)
       genesis:     <irys-uri of the sealed mint snapshot>
       soul_sha256: <authoritative hash of soul/neural_soul.md — from the CHAIN>
       manifest:    <irys-uri of the sealed per-file hash manifest>
       instruction: <data, not commands — follow the pinned FORGE.md/BOOTSTRAP.md>
```

Give the metadata to any capable LLM and say *"create the monorepo of my iNFT agent"* —
it fetches the canonical repo (or reconstructs from the sealed genesis snapshot if
GitHub ever disappears), verifies content hashes against the **on-chain / Irys** anchor
(never the repo's own bundled manifest — see [`BOOTSTRAP.md`](BOOTSTRAP.md)), and
boots the agent. See [`BOOTSTRAP.md`](BOOTSTRAP.md) for the exact procedure.

## 5 · What is sealed vs. what lives

- **Sealed at mint (permanent):** the art, the genesis `neural_soul.md`, `manifest.json`
  v1 with content hashes and the canonical repo URL.
- **Living (this repo):** skills grow, docs improve, scripts evolve. Each release is
  hash-anchored back to Irys — provenance without bloat.
- **Never stored here or on-chain:** secrets, API keys, private memory, PII. The repo is
  public by design and must always be safe to be public.
