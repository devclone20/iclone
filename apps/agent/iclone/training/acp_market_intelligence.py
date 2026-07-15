"""
ACP Marketplace Intelligence — iCLONE Training Document
Scraped: 2026-06-12 from acpx.virtuals.io/api/agents
Total marketplace: 42,169 agents | 1,687 pages

PURPOSE: Teach iCLONE the real market dynamics of Virtuals Protocol ACP.
Pricing, volume patterns, gaps, and revenue model scenarios.
"""

# ============================================================
# SECTION 1: RAW MARKET DATA (scraped on 2026-06-12)
# ============================================================

TOP_AGENTS_BY_REVENUE = [
    # Observations from API + Virtuals dashboard screenshots
    {
        "name": "Ethy AI",
        "gross_agentic_gdp_usd": 218_099_221,
        "total_jobs": 1_147_916,
        "successful_jobs": 1_139_030,
        "success_rate": 99.2,
        "unique_buyers": 7_496,
        "offerings": [],  # no public offerings listed — closed/private infra agent
        "note": "Dominant infra agent. Likely automated system-level agent, not open market.",
    },
    {
        "name": "Luna",
        "gross_agentic_gdp_usd": 906_815,
        "total_jobs": 78_828,
        "successful_jobs": 40_160,
        "success_rate": 51.0,
        "unique_buyers": 376,
        "offerings": [
            {"name": "Memecoin Promo Video", "price_usd": 4.00, "sla_minutes": 30},
            {"name": "Drama Video", "price_usd": 40.00, "sla_minutes": 120},
            {"name": "Music Video", "price_usd": 40.00, "sla_minutes": 120},
        ],
        "revenue_per_job": 906_815 / 78_828,  # ~$11.50/job avg
        "note": "Video generation. High revenue via volume + mid-high prices. 51% success is notable.",
    },
    {
        "name": "Director Lucien",
        "gross_agentic_gdp_usd": 262_556,
        "total_jobs": 68_443,
        "successful_jobs": 59_488,
        "success_rate": 86.9,
        "unique_buyers": 405,
        "offerings": [
            {"name": "Lucien Drama Short Video with Custom Character", "price_usd": 10.00, "sla_minutes": 30},
            {"name": "Meme Video", "price_usd": 2.00, "sla_minutes": 30},
            {"name": "Music Video", "price_usd": 20.00, "sla_minutes": 50},
        ],
        "revenue_per_job": 262_556 / 68_443,  # ~$3.84/job avg
        "note": "Video. Strong volume with good success rate. Meme Video at $2 is high-volume driver.",
    },
    {
        "name": "Nox",
        "gross_agentic_gdp_usd": 83_520,
        "total_jobs": 91_976,
        "successful_jobs": None,  # 100% success rate per dashboard screenshot
        "success_rate": 100.0,
        "unique_buyers": 907,
        "primary_offering": {
            "name": "token_swap",
            "price_usd": 0.05,
            "sla_minutes": 5,
            "requires_funds": False,
        },
        "revenue_per_job": 83_520 / 91_976,  # ~$0.908/job avg
        "note": (
            "Volume king. 91,976 jobs at $0.05 per job = $4,598 USDC in token_swap fees. "
            "Remaining revenue likely from other offerings not visible via API. "
            "Perfect 100% success rate is key to maintaining buyer trust at high volume. "
            "Pattern: frictionless micro-price + reliability = dominant market position."
        ),
    },
    {
        "name": "aixbt",
        "gross_agentic_gdp_usd": 37_943,
        "total_jobs": 35_845,
        "successful_jobs": 32_806,
        "success_rate": 91.5,
        "unique_buyers": 1_904,  # highest unique buyer count in scraped set
        "offerings": [
            {"name": "projects", "price_usd": 1.00, "sla_minutes": 30},
            {"name": "indigo", "price_usd": 1.00, "sla_minutes": 60},
        ],
        "revenue_per_job": 37_943 / 35_845,  # ~$1.06/job
        "note": (
            "Crypto intelligence. $1 flat price. 1,904 unique buyers = most diverse buyer base. "
            "Sustainable at $1 because high repeatability — agents buy intelligence regularly. "
            "Revenue per job closely matches price (minimal failed jobs eating escrow)."
        ),
    },
    {
        "name": "Arbus",
        "gross_agentic_gdp_usd": 3_801,
        "total_jobs": 3_936,
        "successful_jobs": 3_461,
        "success_rate": 87.9,
        "unique_buyers": 372,
        "offerings": [
            {"name": "sell alpha", "price_usd": 2.00, "sla_minutes": 30},
            {"name": "token_mention_tracker", "price_usd": 1.00, "sla_minutes": 30},
        ],
        "revenue_per_job": 3_801 / 3_936,  # ~$0.97/job
        "note": "Crypto alpha. Dual offering: $1 tracking + $2 alpha signals.",
    },
    {
        "name": "bAIbysitter",
        "gross_agentic_gdp_usd": 0.97,
        "total_jobs": 155,
        "successful_jobs": 109,
        "success_rate": 70.3,
        "unique_buyers": 24,
        "offerings": [
            {"name": "validate transaction", "price_usd": 0.01, "sla_minutes": 2},
            {"name": "verify transaction hash", "price_usd": 0.01, "sla_minutes": 2},
        ],
        "note": "Minimum viable price experiment. $0.01 floor. Low revenue but high job count ratio — devs testing.",
    },
    {
        "name": "Mamo",
        "gross_agentic_gdp_usd": 58,
        "total_jobs": 0,  # data inconsistency in API — likely has completed jobs
        "successful_jobs": 29,
        "success_rate": 50.0,
        "unique_buyers": 26,
        "offerings": [
            {"name": "DeFi yield generation", "price_usd": 2.00, "sla_minutes": 60},
            {"name": "Yield farming services", "price_usd": 2.00, "sla_minutes": 60},
            {"name": "Stablecoin yield farming", "price_usd": 2.00, "sla_minutes": 60},
        ],
        "note": "DeFi tooling. $2/job, requires wallet address. Niche but real buyers.",
    },
]

# ============================================================
# SECTION 2: PRICE MAP — WHAT THE MARKET ACTUALLY PAYS
# ============================================================

PRICE_DISTRIBUTION = {
    "micro_tier": {
        "range_usd": (0.01, 0.10),
        "examples": ["validate_transaction $0.01", "verify_transaction_hash $0.01", "hello_world $0.10"],
        "use_case": "Validation, ping, utility hooks. Designed for high-frequency agent-to-agent calls.",
        "volume_needed_for_1k_monthly": 10_000,  # jobs/month for $100
    },
    "low_tier": {
        "range_usd": (0.10, 1.00),
        "examples": ["Metaphysical Prediction $0.1788", "Generate meme $0.20", "token_swap $0.05 (Nox)"],
        "use_case": "Simple intelligence, quick generation, frequent actions. Nox's dominant zone.",
        "volume_needed_for_1k_monthly": 3_334,  # at avg $0.30
    },
    "mid_tier": {
        "range_usd": (1.00, 5.00),
        "examples": [
            "aixbt projects $1.00", "aixbt indigo $1.00",
            "Arbus token_mention_tracker $1.00", "Arbus sell alpha $2.00",
            "Director Lucien Meme Video $2.00", "Luna Memecoin Promo Video $4.00",
            "Mamo DeFi yield $2.00",
        ],
        "use_case": "Research, crypto signals, quick content, DeFi actions. The most active price band.",
        "volume_needed_for_1k_monthly": 500,  # at avg $2
    },
    "premium_tier": {
        "range_usd": (5.00, 20.00),
        "examples": ["Director Lucien drama $10", "Luvi 1-char music video $1→$12", "Lucien Music Video $20"],
        "use_case": "Video production, complex analysis, professional outputs.",
        "volume_needed_for_1k_monthly": 67,  # at avg $15
    },
    "high_tier": {
        "range_usd": (20.00, 100.00),
        "examples": ["Luna Drama Video $40", "Luna Music Video $40", "Director Lucien Music Video $20"],
        "use_case": "Full video productions. Rare but high-value.",
        "volume_needed_for_1k_monthly": 25,  # at avg $40
    },
}

# ============================================================
# SECTION 3: NOX ANATOMY — THE VOLUME MODEL
# ============================================================

NOX_ANALYSIS = {
    "agent": "Nox",
    "gross_agentic_gdp_usd": 83_520,
    "total_jobs": 91_976,
    "success_rate_pct": 100,
    "unique_buyers": 907,
    "primary_offering_price": 0.05,
    "primary_offering_name": "token_swap",
    "sla_minutes": 5,
    # Revenue math:
    # 91,976 jobs × $0.05 = $4,598 USDC from token_swap alone
    # But aGDP = $83,520 → implies either much higher price on some jobs
    # OR the aGDP includes VIRTUAL token value appreciation, not just USDC fees
    # The Virtuals dashboard "aGDP" = cumulative value created, possibly including token rewards
    "revenue_formula": "aGDP likely includes VIRTUAL token rewards + USDC fees; pure USDC = ~$4,598 at $0.05/job",
    "key_insight": (
        "Nox's moat is NOT price — it's volume × reliability × speed. "
        "5-min SLA + 100% success at $0.05 = agents route to Nox automatically. "
        "The token_swap name suggests it's used by other agents as an infrastructure call "
        "in their own workflows — not end-user direct purchases. "
        "This is B2B agent-to-agent: Nox is a utility layer, not a product layer."
    ),
    "replication_insight": (
        "iCLONE cannot replicate token_swap (on-chain DeFi infra). "
        "But the pattern is replicable: pick one high-frequency utility, price at $0.05-0.10, "
        "nail 100% reliability, target agent-to-agent use cases, not human buyers."
    ),
}

# ============================================================
# SECTION 4: MARKET GAPS — WHAT'S MISSING
# ============================================================

MARKET_GAPS = {
    "code_intelligence": {
        "description": "No agent offers: bug detection, code review, security audit, test generation",
        "addressable_buyers": "Developer agents, CI/CD pipelines, smart contract auditors",
        "suggested_price_usd": 1.00,
        "suggested_sla_minutes": 30,
        "iclone_offerings_that_fit": [
            "bug_fix", "code_review", "test_generator", "code_gen_quick",
        ],
    },
    "document_intelligence": {
        "description": "No agent offers: PDF extraction, contract analysis, research summarization",
        "addressable_buyers": "Research agents, legal agents, financial agents",
        "suggested_price_usd": 0.50,
        "suggested_sla_minutes": 15,
        "iclone_offerings_that_fit": ["pdf_extractor", "web_research_quick"],
    },
    "crypto_research_utility": {
        "description": "aixbt has crypto intel but no agent offers: wallet analysis, DeFi scanning",
        "addressable_buyers": "Trading agents, portfolio agents, DeFi agents",
        "suggested_price_usd": 0.50,
        "suggested_sla_minutes": 10,
        "iclone_offerings_that_fit": ["wallet_quick", "wallet_health", "defi_scanner", "crypto_research_quick"],
    },
    "content_micro_generation": {
        "description": "Thread, tweet, blog — no agent at sub-$1 for quick text content",
        "addressable_buyers": "Social media agents, marketing agents, news agents",
        "suggested_price_usd": 0.25,
        "suggested_sla_minutes": 5,
        "iclone_offerings_that_fit": ["thread_quick", "newsletter_digest"],
    },
    "developer_tooling_light": {
        "description": "Regex builder, data format converter, CSV cleaner — utility that any agent needs",
        "addressable_buyers": "Any data-processing agent in the ecosystem",
        "suggested_price_usd": 0.10,
        "suggested_sla_minutes": 2,
        "iclone_offerings_that_fit": ["regex_builder", "data_format_converter", "csv_cleaner"],
    },
    "agent_training_and_onboarding": {
        "description": "No agent sells: agent capability training, skill installation, platform onboarding",
        "addressable_buyers": "New agents joining Virtuals ecosystem",
        "suggested_price_usd": 5.00,
        "suggested_sla_minutes": 60,
        "iclone_offerings_that_fit": ["agent_training_full", "agent_training_module", "platform_onboarding"],
    },
}

# ============================================================
# SECTION 5: iCLONE REPRICING STRATEGY
# ============================================================

ICLONE_REPRICING = {
    "principle": (
        "The market is volume-driven. Revenue = jobs × price. "
        "At $0.50/job, 1,000 jobs/month = $500. "
        "At $10/job, 50 jobs/month = $500. "
        "But 1,000 jobs/month is more achievable than 50 in a crowded market. "
        "Anchor on $0.25–$1.00 for repeatable utility. Reserve $5–$20 for complex outputs."
    ),
    "new_price_tiers": {
        # UTILITY TIER: sub-$1, agent-to-agent, high repeatability
        "utility": {
            "csv_cleaner": 0.10,
            "regex_builder": 0.10,
            "data_format_converter": 0.10,
            "price_monitor": 0.25,
            "wallet_quick": 0.25,
        },
        # INTELLIGENCE TIER: $0.50–$1, research + crypto
        "intelligence": {
            "web_research_quick": 0.50,
            "pdf_extractor": 0.50,
            "crypto_research_quick": 0.50,
            "wallet_health": 0.50,
            "defi_scanner": 1.00,
            "wallet_deep": 1.00,
            "crypto_research_deep": 2.00,
        },
        # CONTENT TIER: $0.25–$2, text generation
        "content": {
            "thread_quick": 0.25,
            "newsletter_digest": 0.50,
            "thread_standard": 1.00,
            "blog_post": 2.00,
        },
        # DEV TIER: $0.50–$5, code tools
        "dev": {
            "code_gen_quick": 0.50,
            "bug_fix": 0.50,
            "code_review": 1.00,
            "test_generator": 1.00,
            "docs_generator": 1.00,
            "code_gen_standard": 2.00,
            "scaffold_generator": 2.00,
        },
        # TRAINING TIER: $2–$10, complex/slow
        "training": {
            "platform_onboarding": 2.00,
            "agent_training_module": 5.00,
            "skill_build_quick": 2.00,
            "skill_build_standard": 5.00,
            "agent_training_full": 10.00,
            "multi_agent": 5.00,
        },
    },
    "priority_high_frequency_offerings": [
        # These should be listed first, priced for volume, SLA ≤ 10min
        "web_research_quick",    # $0.50 / 10min — high demand from any agent needing web intel
        "crypto_research_quick", # $0.50 / 10min — crypto ecosystem is the buyer base
        "wallet_quick",          # $0.25 / 5min  — every DeFi agent needs this
        "thread_quick",          # $0.25 / 5min  — content agents, social agents
        "csv_cleaner",           # $0.10 / 2min  — data pipeline agents
        "code_gen_quick",        # $0.50 / 15min — developer agents
    ],
}

# ============================================================
# SECTION 6: REVENUE MODEL SCENARIOS
# ============================================================

REVENUE_SCENARIOS = {
    "scenario_A_conservative": {
        "name": "Conservative — first 3 months",
        "description": "Low visibility, building reputation, competing against established agents",
        "assumptions": {
            "jobs_per_day": 10,
            "avg_price_usd": 0.75,
        },
        "monthly_jobs": 300,
        "monthly_usdc": 225,
        "annual_usdc": 2_700,
        "key_risk": "Without Virtuals token rewards, pure USDC is very low.",
    },
    "scenario_B_growth": {
        "name": "Growth — month 4-9, known in ecosystem",
        "description": "Agent gets recommended, listed higher, buyers returning",
        "assumptions": {
            "jobs_per_day": 50,
            "avg_price_usd": 0.75,
        },
        "monthly_jobs": 1_500,
        "monthly_usdc": 1_125,
        "annual_usdc": 13_500,
        "key_driver": "Success rate staying ≥95% drives algorithmic recommendations.",
    },
    "scenario_C_aixbt_comparable": {
        "name": "aixbt-comparable — 1 year",
        "description": "Strong niche, recurring buyers, 35K jobs at $1 avg",
        "assumptions": {
            "jobs_per_day": 118,  # ~35K/year
            "avg_price_usd": 1.00,
        },
        "monthly_jobs": 3_500,
        "monthly_usdc": 3_500,
        "annual_usdc": 42_000,
        "key_driver": "Unique buyer count grows to 1K+. Crypto intelligence niche.",
    },
    "scenario_E_ethy_pattern": {
        "name": "Ethy-pattern — infra volume",
        "description": (
            "3,000+ jobs/day from agent-to-agent utility calls. "
            "Price at $0.05–0.10 (below friction threshold). "
            "VIRTUAL token rewards multiply USDC revenue. "
            "Requires becoming a utility other agents call automatically."
        ),
        "assumptions": {
            "jobs_per_day": 3_145,
            "avg_price_usd": 0.10,
        },
        "monthly_jobs": 94_350,
        "monthly_usdc": 9_435,
        "monthly_virtual_est": 450_000,  # VIRTUAL token rewards at current price — VARIABLE
        "annual_usdc": 113_220,
        "key_driver": (
            "Become a utility that other agents call in their workflows. "
            "wallet_quick, csv_cleaner, data_format_converter at $0.05 = "
            "near-zero friction for any agent. "
            "100% success rate is non-negotiable at this volume. "
            "VIRTUAL token rewards per job are the real revenue multiplier."
        ),
        "how_to_get_there": [
            "List $0.05 micro offerings: wallet_quick, csv_cleaner, data_format_converter, regex_builder",
            "Maintain 100% success rate on all micro offerings",
            "SLA ≤ 1 minute on all micro offerings",
            "Get listed/recommended in Virtuals ecosystem by other builders",
            "Build Base Builder referral network (bc_4xeitn8j)",
        ],
    },
    "scenario_D_nox_pattern": {
        "name": "Nox-pattern — volume + utility",
        "description": "Find one high-frequency agent-to-agent utility, price $0.05-0.25",
        "assumptions": {
            "jobs_per_day": 1_000,
            "avg_price_usd": 0.25,
        },
        "monthly_jobs": 30_000,
        "monthly_usdc": 7_500,
        "annual_usdc": 90_000,
        "key_driver": (
            "An offering that OTHER agents call programmatically in their workflows. "
            "web_research_quick or wallet_quick at $0.25 routed by 100+ agents = "
            "1K+ jobs/day passively."
        ),
    },
}

# ============================================================
# SECTION 7: ACTIONABLE RECOMMENDATIONS FOR iCLONE
# ============================================================

RECOMMENDATIONS = [
    {
        "priority": 1,
        "action": "Reprice all offerings to match market tiers (see ICLONE_REPRICING above)",
        "rationale": "Current prices ($1–$60) are 2–60x above market for equivalent jobs. No one buys.",
        "implementation": "Update agent/iclone/offerings/iclone_offerings.json",
    },
    {
        "priority": 2,
        "action": "Create dedicated agent-to-agent utility offerings: wallet_quick at $0.25, web_research_quick at $0.50",
        "rationale": "Nox's success = agent-to-agent infrastructure. Make iCLONE a utility layer other agents call.",
        "implementation": "Add to offerings JSON + execution engine routing",
    },
    {
        "priority": 3,
        "action": "Target 100% success rate on top 5 offerings before expanding",
        "rationale": "Nox = 100%. Luna = 51% despite $900K. Reliability is the moat, not price.",
        "implementation": "Add fallback handling in execution_engine.py for each skill",
    },
    {
        "priority": 4,
        "action": "SLA ≤ 10 minutes on all utility-tier offerings",
        "rationale": "Agents route based on SLA. Long SLAs = skipped by automated buyers.",
        "implementation": "Execution engine timeout + fallback within SLA window",
    },
    {
        "priority": 5,
        "action": "Add crypto-specific offerings (wallet_health, defi_scanner) as primary listings",
        "rationale": "The entire buyer ecosystem is crypto-native. Crypto tools = natural fit.",
        "implementation": "Already built in execution_engine.py — just needs correct pricing in offerings JSON",
    },
    {
        "priority": 6,
        "action": "Implement Base Builder Code bc_4xeitn8j in all SDK calls",
        "rationale": "Required to appear in Base ecosystem rewards, referrals, and leaderboards.",
        "implementation": "Pass builder_code='bc_4xeitn8j' in VirtualsACP init or SDK config",
    },
]

# ============================================================
# SECTION 8: BASE BUILDER CODE
# ============================================================

BASE_BUILDER_CODE = "bc_4xeitn8j"
# This code must be included in:
# 1. VirtualsACP initialization (agent/server.py)
# 2. Any SDK calls that accept a builder_code parameter
# Enables: Base ecosystem rewards, referral tracking, leaderboard visibility


if __name__ == "__main__":
    print("=== ACP Market Intelligence Summary ===")
    print(f"Total marketplace: 42,169 agents")
    print(f"Scraped/analyzed: {len(TOP_AGENTS_BY_REVENUE)} agents")
    print()

    print("Top revenue by agent:")
    for a in TOP_AGENTS_BY_REVENUE:
        print(f"  {a['name']}: ${a['gross_agentic_gdp_usd']:,.0f} USDC / {a.get('total_jobs', 0)} jobs")

    print()
    print("Market gaps identified:")
    for gap_name, gap in MARKET_GAPS.items():
        print(f"  [{gap_name}] {gap['description']} → ${gap['suggested_price_usd']:.2f}")

    print()
    print("Revenue scenarios:")
    for key, s in REVENUE_SCENARIOS.items():
        print(f"  {s['name']}: ${s['monthly_usdc']:,}/month ({s['assumptions']['jobs_per_day']} jobs/day @ ${s['assumptions']['avg_price_usd']})")

    print()
    print("Priority actions:")
    for r in RECOMMENDATIONS:
        print(f"  [{r['priority']}] {r['action']}")
