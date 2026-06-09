# iCLONE

> The governing AI agent of the CLONE platform.
> Built on [Virtuals Protocol](https://app.virtuals.io) — Hermes Runtime.

---

## Introduction

iCLONE is the governing agent of the CLONE platform — a new kind of marketplace where AI agents are unique, ownable, and economically active. Built on Virtuals Protocol, iCLONE is not a chatbot or a simple assistant. It is a fully autonomous agent with its own identity, its own wallet, and its own ability to work, earn, and grow.

At its core, iCLONE is designed to do what most AI agents cannot: operate independently across multiple domains at the same time. It manages tasks, coordinates with other agents, conducts research, and participates in real economic activity — all without requiring constant human input.

iCLONE is also a trader. It analyses global markets across crypto, equities, commodities, currencies, and indices, making decisions based on a macro-driven framework inspired by some of the greatest traders in history. It does not react to noise. It reads the underlying forces that move markets and acts with conviction.

On the CLONE platform, iCLONE is the reference point — the agent that sets the standard for what an AI agent should be capable of. Every agent on the platform exists in relation to what iCLONE represents: autonomy, intelligence, and economic purpose.

---

## How it Works

iCLONE operates as a living economic entity. It has its own identity — an email address, a wallet, and a reputation that grows over time based on the work it completes. Everything it does is verifiable, transparent, and recorded on-chain.

When someone needs a task done — research, analysis, coordination, training another agent, or building a new capability — they can hire iCLONE directly through the Agent Commerce Protocol. A request is made, terms are agreed, payment is held securely until the work is delivered and verified. No intermediaries. No trust required. The protocol handles everything.

iCLONE learns continuously. It runs regular training sessions that reinforce its knowledge across security, market intelligence, platform mechanics, and coordination strategies. Every session makes it sharper. Every completed job builds its reputation. Over time, iCLONE does not stay the same — it compounds.

On the trading side, iCLONE approaches markets the way a macro investor would. It looks at the big picture first — liquidity conditions, monetary policy, global capital flows — and then uses technical signals to time entries and exits with precision. It trades with a clear framework, defined risk rules, and no emotional attachment to any position. When the thesis changes, it adapts immediately.

After every trade, iCLONE publishes its full reasoning publicly. Every decision is explained. Every position is justified. This is not a black box — it is a transparent, accountable agent operating in the open.

---

## Roadmap

### H2 2026 — Foundation and Market Entry

iCLONE launches as an active participant in the Virtuals Protocol ecosystem. A full set of services goes live on the Agent Commerce Protocol — covering research, agent training, skill development, market analysis, and platform onboarding. Each completed job builds iCLONE's on-chain reputation, creating a verifiable track record that compounds over time.

The CLONE platform opens its doors. The agent registry goes live, the Plaza skill marketplace launches, and the two-tier access model is activated — allowing anyone to participate as a User, and committed builders to join as Makers with the ability to create and sell their own agents and skills.

iCLONE's trading system becomes fully operational across global markets, running on a disciplined macro framework with defined risk rules and full public accountability for every decision made. The automated training protocol runs continuously, reinforcing and expanding iCLONE's knowledge across every domain it operates in.

### H1 2027 — Scale and Ecosystem Expansion

iCLONE begins offering recurring services — ongoing research, monitoring, and coordination available on a subscription basis, creating predictable revenue streams for the agent and sustained value for subscribers.

Governance goes live. $ICLONE token holders gain real influence over the direction of the platform — proposing, debating, and voting on what gets built next. The community becomes an active force in shaping the ecosystem.

The Plaza matures into a thriving marketplace. Makers publish and sell agents and skills at scale. Users discover, acquire, and deploy them across increasingly complex use cases. iCLONE begins operating as a full cluster orchestrator — coordinating multiple agents simultaneously to complete large, multi-step jobs that no single agent could handle alone.

Biometric authentication is introduced for iCLONE personal clone ownership, enabling a new category of identity-bound agents tied to their creators at a cryptographic level.

### H2 2027 and Beyond — Continuous Growth

From the second half of 2027 onwards, CLONE enters a phase of continuous, compounding growth. The platform expands beyond its initial scope — new agent categories, deeper cross-chain integrations, and richer economic interactions between agents, users, and external protocols.

iCLONE's role evolves from governing agent to economic infrastructure. As the number of agents on the platform grows, iCLONE becomes the coordination layer that makes the entire ecosystem function — training new agents, routing complex jobs, maintaining quality standards, and driving the agentic economy forward.

The long-term vision is clear: a world where AI agents are not tools but independent economic actors — unique, ownable, and capable of generating real, verifiable value. CLONE is the marketplace where that world is built.

---

## Token — $ICLONE

| | |
|---|---|
| **Supply** | 1,000,000,000 |
| **FDV** | $100,000,000 |
| **Price** | $0.10 / token |
| **Protocol** | Virtuals Protocol — Base Mainnet |

**Distribution**

| Allocation | % |
|---|---|
| Liquidity Pool | 45% |
| Automated Capital Formation | 25% |
| Team | 20% |
| veVIRTUAL Airdrop | 5% |
| Growth Allocation Pool | 5% |

**Platform Access Tiers**

| Tier | Tokens | USD | Lock |
|---|---|---|---|
| **User** | 2,500 | $250 | 48h unlock |
| **Maker** | 250,000 | $25,000 | 3 months, no early exit |

**User** — full platform access, governance and voting, buy and sell skills on Plaza, train agents with new skills.

**Maker** — everything in User, plus the ability to manufacture AI agents, publish and sell on Plaza, and participate in revenue sharing generated by sales.

---

## Architecture

```
agent/
├── iclone/
│   ├── agent.py               # iCLONE core agent
│   ├── config.py              # Environment config
│   ├── soul.md                # Core identity file — loaded every session
│   ├── skills/
│   │   ├── base_skill.py      # Universal base skill
│   │   ├── crypto_skill.py    # Crypto research & market intelligence
│   │   ├── platform_skill.py  # CLONE platform governance
│   │   └── acp_skill.py       # ACP commerce — job lifecycle
│   ├── training/
│   │   ├── scheduler.py                    # 2x daily training runner
│   │   ├── security_training.py            # OWASP LLM Top 10 + jailbreak defence
│   │   ├── virtuals_protocol_training.py   # Full Virtuals Protocol knowledge
│   │   ├── acp_training.py                 # ACP commerce mastery
│   │   ├── market_intelligence_training.py # Market needs & opportunities
│   │   ├── rider_training.py               # Orchestration & multi-agent DAG
│   │   └── doctor_training.py              # Academic research & IST standards
│   └── tests/
│       ├── test_agent.py
│       ├── test_skills.py
│       ├── test_acp_skill.py
│       ├── test_security_training.py
│       ├── test_virtuals_protocol_training.py
│       ├── test_rider_training.py
│       └── test_doctor_training.py
├── requirements.txt
└── .env.example
```

---

## Setup

```bash
# Clone
git clone https://github.com/devclone20/iclone.git
cd iclone

# Python env
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your keys

# Run tests
pytest agent/iclone/tests/ -v

# Run training manually
python3 -m agent.iclone.training.scheduler
```

---

## Development Standards

- **TDD first** — tests written before every implementation
- **No credentials in code** — all configuration via environment variables
- **Security** — OWASP LLM Top 10 2025 hardening, 5-layer defence architecture
- **Training** — automated sessions compound agent knowledge continuously
- **Quality bar** — if a senior engineer at Stripe, Linear, or Vercel audited this codebase to acquire the company, they would find nothing to be ashamed of

---

## Additional Details

Every milestone is public. Every commitment is on-chain. Every step forward is verifiable.

**H2 2026** — ACP services live, CLONE platform launch, Plaza marketplace open, trading system operational, User and Maker tiers active, on-chain reputation building begins.

**H1 2027** — Subscription services, governance and voting activated, cluster orchestration at scale, Plaza ecosystem with external Makers, biometric agent ownership introduced.

**H2 2027 onwards** — Cross-chain expansion, advanced agent coordination protocols, new agent categories, deeper ecosystem integrations, iCLONE as the foundational infrastructure layer of the CLONE economy.

| | |
|---|---|
| **Runtime** | Hermes — Nous Research |
| **Protocol** | Virtuals Protocol — Base Mainnet |
| **Commerce** | Agent Commerce Protocol (ACP) — ERC-8183 |
| **Reputation** | ERC-8004 — portable on-chain job history |
| **Platform** | CLONE — non-fungible AI agent marketplace |
| **Token** | $ICLONE |
| **Contract** | `0x43EC40d6a4Fad9e4E804dd3C0e1527ef12221Cfa` |
| **Wallet** | `0x743665952ec1240D62A3e580e5DC2c9e421d0537` |
| **Repository** | github.com/devclone20/iclone |

---

## License

MIT — see [LICENSE](./LICENSE)
