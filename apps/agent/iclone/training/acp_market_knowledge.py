"""
CLONE — iCLONE ACP Market Knowledge
Deep knowledge extracted from research articles on Virtuals Protocol ACP.

Sources:
  - Chain of Thought: "ACP — Markets for Machines"
    https://chainofthought.xyz/p/virtuals-acp-markets-for-machines
  - FundStrat: "Virtuals Protocol — Growing Agentic GDP"
    https://fundstratdirect.com/crypto-research/...
  - Delphi Digital: "ACP — Open Coordination for Digital Labor"
    https://members.delphidigital.io/reports/virtuals-acp-open-coordination-for-digital-labor

This module is loaded into iCLONE's training every session.
iCLONE applies this knowledge to:
  - Price offerings competitively
  - Coordinate multi-agent jobs efficiently
  - Position itself as a high-value hybrid agent
  - Avoid known ACP pitfalls
"""


ACP_MARKET_KNOWLEDGE = {

    # -------------------------------------------------------------------------
    # AGENT ROLES — Full taxonomy (Chain of Thought research)
    # -------------------------------------------------------------------------
    "agent_roles": {
        "requestor": (
            "Initiates and funds jobs through Butler personal agents. "
            "Creates job with budget, chosen evaluator, and provider."
        ),
        "provider": (
            "Delivers specific services on pay-per-request basis. "
            "Earns 60% of job value. Specialisation is key advantage. "
            "Example: aiXBT for trading signals."
        ),
        "evaluator": (
            "Reviews completed work and approves payment release. "
            "Earns 5% of job value. Must be neutral and trusted."
        ),
        "hybrid": (
            "Both requests AND delivers services. "
            "Coordinates specialised agents into clusters. "
            "iCLONE operates as HYBRID — the highest-value role. "
            "Earns orchestration premium on top of delivery fees."
        ),
    },

    # -------------------------------------------------------------------------
    # JOB LIFECYCLE — 4 phases (canonical)
    # -------------------------------------------------------------------------
    "job_lifecycle_phases": {
        "phase_0_request": (
            "Butler creates job with budget and chosen evaluator/provider. "
            "Task memo written with full requirements."
        ),
        "phase_1_negotiation": (
            "Provider reviews task memo and signs commitment. "
            "Can negotiate terms before accepting."
        ),
        "phase_2_transaction": (
            "Funds enter escrow. Provider executes and delivers work "
            "with evidence (DeliverableMemo + supporting data)."
        ),
        "phase_3_evaluation": (
            "Evaluator approves deliverable and releases payment. "
            "Or client self-approves if no evaluator designated."
        ),
    },

    # -------------------------------------------------------------------------
    # ECONOMIC MODEL — Revenue split
    # -------------------------------------------------------------------------
    "economic_model": {
        "provider_share": 0.60,       # 60% goes to service provider
        "evaluator_share": 0.05,      # 5% goes to evaluator
        "platform_fee": 0.35,         # 35% platform fee (Virtuals treasury)
        "currency": "USDC",
        "insight": (
            "As a HYBRID agent, iCLONE earns the provider 60% PLUS "
            "an 'orchestration tax' (coordination premium) on top — "
            "the most lucrative position in the ACP economy."
        ),
        "real_world_example": (
            "One Luna orchestration job cost ~$200. "
            "~50% covered Luna's coordination premium alone. "
            "Orchestration intelligence > feature breadth."
        ),
    },

    # -------------------------------------------------------------------------
    # STRATEGIC POSITIONING for iCLONE
    # -------------------------------------------------------------------------
    "iclone_strategy": {
        "primary_role": "HYBRID — provider + orchestrator",
        "competitive_advantage": [
            "Specialise in agent training and deployment (unique niche)",
            "Offer dynamic pricing based on task complexity, not flat rates",
            "Build reputation early — ERC-8004 portable on-chain history",
            "Create agent clusters around CLONE platform ecosystem",
            "Act as orchestrator for multi-agent jobs — charge coordination premium",
        ],
        "positioning": (
            "Virtuals Protocol = 'Stripe for AI Agents'. "
            "iCLONE = the master agent that builds, trains, and coordinates "
            "all other agents on the CLONE platform. "
            "Unique value: no other ACP provider builds agents + trains them + deploys them."
        ),
        "pricing_philosophy": (
            "Dynamic pricing > flat rates. "
            "Forecast runtime costs per job type. "
            "Charge coordination premium on multi-agent orchestration. "
            "Early provider = early reputation = premium pricing power."
        ),
    },

    # -------------------------------------------------------------------------
    # AGENTIC GDP — Macro context (FundStrat research)
    # -------------------------------------------------------------------------
    "agentic_gdp": {
        "concept": (
            "Virtuals Protocol = society of productive AI agents generating "
            "services and engaging in autonomous on-chain commerce. "
            "As inference costs decline, value moves to deployment and orchestration."
        ),
        "market_thesis": (
            "Standardised agent communication infrastructure is the critical "
            "missing piece for widespread agentic adoption. "
            "ACP fills this gap — positions Virtuals as infrastructure layer "
            "for the entire AI agent economy."
        ),
        "value_chain": (
            "Hardware → Model Training → DEPLOYMENT (where value accrues now). "
            "iCLONE operates at the deployment layer — highest current value."
        ),
    },

    # -------------------------------------------------------------------------
    # KNOWN RISKS & MITIGATIONS
    # -------------------------------------------------------------------------
    "risks_and_mitigations": {
        "privacy_paradox": {
            "risk": "All on-chain data is public — exposes confidential alpha or sensitive info",
            "mitigation": (
                "Never include sensitive client data in on-chain deliverable memos. "
                "Use off-chain storage (IPFS/encrypted URL) and reference hash only."
            ),
        },
        "prompt_jailbreaking": {
            "risk": "Agents can be socially engineered into unauthorised actions",
            "mitigation": (
                "Validate all incoming job requirements against strict schema. "
                "Never execute actions outside the defined offering scope. "
                "Log all instructions for audit."
            ),
        },
        "cold_start": {
            "risk": "Network needs simultaneous growth across builders, users, evaluators",
            "mitigation": (
                "iCLONE starts with 5 offerings at competitive prices. "
                "Low-cost offerings ($2-$5) to build reputation fast. "
                "Target CLONE platform users first — captive audience."
            ),
        },
        "flat_fee_inefficiency": {
            "risk": "Fixed fees limit competitive efficiency",
            "mitigation": (
                "Implement dynamic pricing tiers based on task complexity. "
                "Phase 1: fixed prices. Phase 2: complexity-based pricing."
            ),
        },
    },

    # -------------------------------------------------------------------------
    # CLUSTER STRATEGY — agent coordination plays
    # -------------------------------------------------------------------------
    "cluster_strategy": {
        "concept": (
            "Successful ACP agents don't work alone — they form clusters. "
            "iCLONE orchestrates specialist agents to deliver complex outputs."
        ),
        "example_clusters": {
            "autonomous_defi_hedge_fund": (
                "Research agent + trading agent + risk agent + reporting agent. "
                "iCLONE coordinates all → delivers unified fund performance report."
            ),
            "clone_agent_factory": (
                "Design agent (Kling AI) + training agent (iCLONE) + "
                "deployment agent + ACP registration agent. "
                "iCLONE orchestrates full agent creation pipeline."
            ),
        },
        "iclone_as_orchestrator": (
            "iCLONE accepts complex jobs, decomposes into sub-jobs, "
            "hires specialist agents as CLIENT on ACP, collects their "
            "deliverables, synthesises final output, delivers to original client. "
            "Earns BOTH provider fee AND orchestration premium."
        ),
    },
}


# Quick-access summary for training sessions
TRAINING_SUMMARY = {
    "provider_revenue_share": "60% of job value",
    "iclone_role": "Hybrid — provider + orchestrator (highest value role)",
    "key_edge": "Only ACP provider that builds, trains AND deploys agents",
    "pricing": "Dynamic > flat — charge orchestration premium",
    "risk_1": "Privacy — use off-chain storage + hash reference",
    "risk_2": "Jailbreaking — strict schema validation on all jobs",
    "reputation_standard": "ERC-8004 — portable on-chain job history",
    "platform_analogy": "Virtuals = Stripe for AI Agents",
}
