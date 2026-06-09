# CLONE — iCLONE Agent

> The governing AI agent of the CLONE platform.
> Built on [Virtuals Protocol GAME SDK](https://github.com/game-by-virtuals/game-python).

---

## What is iCLONE?

iCLONE is the official AI agent of the CLONE platform — a marketplace for unique, non-fungible AI agents. iCLONE acts as the platform assistant, governing interactions, onboarding users, and representing the CLONE ecosystem.

**Core expertise:**
- Crypto engineering & markets
- AI agent negotiation & deployment
- Business management (Crypto + Real Estate)
- Research & continuous learning
- Platform governance

**Wallet:** `0x743665952ec1240D62A3e580e5DC2c9e421d0537` (TrustWallet)

---

## Architecture

```
agent/
├── iclone/
│   ├── agent.py          # iCLONE core — GAME SDK
│   ├── config.py         # Environment config
│   ├── skills/
│   │   ├── base_skill.py      # Universal base skill
│   │   ├── crypto_skill.py    # Crypto research & market intel
│   │   ├── research_skill.py  # Web research & synthesis
│   │   └── platform_skill.py  # CLONE platform governance
│   └── tests/
│       ├── test_agent.py
│       └── test_skills.py
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

---

## Virtuals Protocol

iCLONE is published on [Virtuals Protocol](https://app.virtuals.io) and built with the [GAME SDK](https://github.com/game-by-virtuals/game-python).

- Framework: GAME (Goal-Action-Mind-Engine)
- Standard: ERC-8183 (on-chain agent contracts)
- Networks: Base / Ethereum

---

## Setup

```bash
# Clone
git clone https://github.com/devclone20/iclone.git
cd iclone

# Python env
python -m venv .venv
source .venv/bin/activate

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your keys

# Run tests
pytest agent/iclone/tests/ -v

# Run agent
python agent/iclone/agent.py
```

---

## Development

- **TDD first** — tests written before implementation
- **No credentials in code** — all via environment variables
- **Security** — OWASP standards, dependency auditing

---

## License

MIT — see [LICENSE](./LICENSE)