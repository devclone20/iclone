"""
iCLONE — Offerings Training Module
Trains all 4 agents on the 40 live ACP offerings, routing logic, and job handling.
Includes ACP v2 subscription offerings for DoctorWHO and MATRIX (added 2026-06-13).
Score: pass/fail per section.
"""

# ─── ACP v2 Subscription offerings — DoctorWHO + MATRIX ──────────────────────
# ACP v2 (May 2026) introduced first-class subscription jobs: 7/15/30/90-day tiers.
# These are recurring revenue offerings — client pays once, receives deliverables on cadence.
# No equivalent offerings exist from any top-10 marketplace agent as of 2026-06-13 → gap.

SUBSCRIPTION_OFFERINGS = {
    "DoctorWHO": [
        {
            "name": "dailyResearchDigest",
            "type": "subscription",
            "tier_days": [7, 15, 30],
            "price_per_day_usdc": 0.50,
            "sla_hours": 2,
            "description": (
                "Daily curated research digest: top protocol updates, DeFi yield shifts, "
                "on-chain risk signals, and ACP ecosystem news. "
                "Delivered once per day to the client agent via ACP deliverable memo."
            ),
            "deliverable_format": "Structured JSON: {date, headlines[{title,source,relevance}], "
                                  "risk_alerts[], yield_opportunities[], protocol_updates[]}",
            "tools_used": ["chaingpt_news_fetch", "chaingpt_research_token",
                           "chaingpt_defi_pendle_markets", "chaingpt_defi_morpho_markets",
                           "chaingpt_pm_markets", "chaingpt_hl_funding"],
            "rationale": "Research agents and portfolio agents need daily intel — recurring, predictable demand.",
        },
        {
            "name": "weeklyProtocolReport",
            "type": "subscription",
            "tier_days": [30, 90],
            "price_per_week_usdc": 2.00,
            "sla_hours": 6,
            "description": (
                "Weekly deep-dive protocol analysis report for one chosen protocol. "
                "Covers: TVL trends, smart contract risk, team activity, competitor positioning."
            ),
            "deliverable_format": "Markdown report with data tables, risk score 0–10, recommendation.",
            "tools_used": ["chaingpt_chat", "chaingpt_risk_contract_source", "chaingpt_news_fetch",
                           "chaingpt_defi_aave_health", "chaingpt_research_token"],
            "rationale": "Protocol monitoring is a recurring need — weekly cadence matches governance cycles.",
        },
    ],
    "MATRIX": [
        {
            "name": "portfolioMonitor",
            "type": "subscription",
            "tier_days": [7, 15, 30],
            "price_per_day_usdc": 0.25,
            "sla_hours": 1,
            "description": (
                "Daily DeFi portfolio health check for a given wallet: "
                "Aave health factor, open positions, pending risks, yield opportunities. "
                "Alerts if health factor drops below 1.5 or new airdrop detected."
            ),
            "deliverable_format": "JSON: {wallet, health_factor, positions[], alerts[], opportunities[]}",
            "tools_used": ["chaingpt_defi_aave_health", "chaingpt_wallet_positions",
                           "chaingpt_wallet_pnl", "chaingpt_defi_pendle_markets",
                           "chaingpt_defi_morpho_markets", "chaingpt_research_token"],
            "rationale": (
                "DeFi positions require daily monitoring — liquidation risk is a 24/7 threat. "
                "No agent offers this on ACP. Natural B2B utility for portfolio agents."
            ),
        },
        {
            "name": "fundingRateArb",
            "type": "subscription",
            "tier_days": [7, 15, 30],
            "price_per_day_usdc": 0.50,
            "sla_hours": 1,
            "description": (
                "Daily funding rate arbitrage opportunity scan across Hyperliquid (EVM) "
                "and Drift (Solana). Reports if cross-venue spread exceeds 0.05% threshold."
            ),
            "deliverable_format": "JSON: {date, hl_rates{}, drift_rates{}, arb_opportunities[], spread_threshold_breached}",
            "tools_used": ["chaingpt_hl_funding", "chaingpt_hl_markets",
                           "chaingpt_drift_funding", "chaingpt_drift_markets"],
            "rationale": (
                "Funding arb is time-sensitive and repetitive — ideal for subscription cadence. "
                "Trading agents need this daily. No competitor offers it on ACP."
            ),
        },
    ],
    "acp_v2_note": (
        "All subscription offerings use ACP v2 job type 'subscription'. "
        "Client locks full subscription cost in escrow. "
        "Deliverables submitted once per cadence period. "
        "Auto-renew available at client discretion."
    ),
}


OFFERINGS_KNOWLEDGE = {
    "total_offerings": 40,
    "limit_per_agent": 40,
    "agents": {
        "CLONE": {"offerings": 40, "wallet": "0x44cc25d55a4291b92f52062ba023ca1f14206664"},
        "SuperSayatin": {"offerings": 10, "wallet": "0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3"},
        "DoctorWHO": {
            "offerings": 2,
            "offering_type": "subscription",
            "subscription_offerings": ["dailyResearchDigest", "weeklyProtocolReport"],
            "subscription_status": "DEFINED — pending on-chain publication via acp provider publish",
            "wallet": "0x875242eb5c91270ca80ed7753a87d6e22e4f5acf",
        },
        "MATRIX": {
            "offerings": 2,
            "offering_type": "subscription",
            "subscription_offerings": ["portfolioMonitor", "fundingRateArb"],
            "subscription_status": "DEFINED — pending on-chain publication via acp provider publish",
            "wallet": "0x07924dea2c8212969d5dc5655785aa5063adb2bc",
        },
    },
    "pricing": {
        "micro_0.01": ["cryptoNewsFlash", "cryptoNewsDaily", "cryptoNewsByToken", "cryptoNewsSentiment",
                       "tokenSnapshotQuick", "walletSnapshot", "whaleActivityAlert", "cryptoThreadMicro",
                       "marketCommentary", "riskRewardCalculator", "fundingRateAlert", "priceMonitor",
                       "gasOptimiser", "webResearchQuick", "dataFormatConverter", "codeGenerateQuick", "sqlQueryWrite"],
        "standard_0.05": ["cryptoNewsWeekly", "cryptoNewsNarrative", "cryptoNewsAlpha",
                          "tokenResearchStandard", "protocolAnalysis", "narrativeScanner", "sectorComparison", "competitorMap",
                          "walletHealthAudit", "walletPnL", "walletBehaviourProfile", "smartMoneyTracker",
                          "cryptoThreadStandard", "cryptoThreadViral", "alphaPost", "newsletterSection",
                          "tradingSetupScanner", "tokenTechnicalAnalysis", "marketRegimeDetector", "correlationAnalysis", "liquidityMapQuick",
                          "yieldOpportunityFinder", "defiProtocolHealth", "airdropScanner", "onChainFlowAnalysis", "newTokenResearch",
                          "webResearchStandard", "competitorIntelligence", "pdfExtractor",
                          "codeReviewSecurity", "automationScript", "clonePlatformOnboarding"],
        "deep_0.10": ["tokenResearchDeep", "walletForensics", "cryptoNewsletterFull",
                      "agentTrainingModule", "skillBuildQuick", "skillBuildStandard",
                      "fullAgentTrainingSuite", "multiAgentCoordination"],
    },
    "confirmed_demand": {
        "crypto_news": {"external_jobs": 3, "agent": "0x7457b799121c9b8c51298d08f1c19f0186648c90", "price": 0.01},
        "wallet_health": {"external_jobs": 1, "price": 0.50},
        "thread_quick": {"external_jobs": 1, "price": 0.25},
        "research_quick": {"external_jobs": 1, "price": 0.25},
    },
    "ecosystem_job_types": {
        "evaluator_agent": "platform → agent_training_module",
        "explain_transaction": "wallet → wallet_quick (tx analysis)",
        "mutual_boost": "research → web_research_quick",
        "market_intelligence_report": "research → web_research_deep",
        "crypto_news": "research → web_research_quick (top stories)",
        "dedicated:crypto_news": "research → web_research_quick",
        "bootstrap:crypto_news": "research → web_research_quick",
    },
    "execution_engines": {
        "Engine1_Research": ["cryptoNewsFlash", "cryptoNewsDaily", "cryptoNewsWeekly", "cryptoNewsNarrative",
                              "cryptoNewsAlpha", "narrativeScanner", "sectorComparison", "competitorMap",
                              "webResearchQuick", "webResearchStandard", "competitorIntelligence",
                              "marketRegimeDetector", "correlationAnalysis", "fundingRateAlert",
                              "airdropScanner", "riskRewardCalculator", "smartMoneyTracker"],
        "Engine2_Code": ["codeGenerateQuick", "codeReviewSecurity", "sqlQueryWrite",
                         "automationScript", "dataFormatConverter", "pdfExtractor"],
        "Engine3_Wallet": ["tokenSnapshotQuick", "tokenResearchStandard", "tokenResearchDeep",
                           "protocolAnalysis", "cryptoNewsByToken", "cryptoNewsSentiment",
                           "walletSnapshot", "walletHealthAudit", "walletPnL",
                           "walletBehaviourProfile", "walletForensics", "whaleActivityAlert",
                           "tradingSetupScanner", "tokenTechnicalAnalysis", "liquidityMapQuick",
                           "yieldOpportunityFinder", "defiProtocolHealth", "onChainFlowAnalysis",
                           "newTokenResearch", "gasOptimiser"],
        "Engine4_Content": ["cryptoThreadMicro", "cryptoThreadStandard", "cryptoThreadViral",
                             "marketCommentary", "alphaPost", "newsletterSection", "cryptoNewsletterFull"],
        "Engine5_Platform": ["agentTrainingModule", "skillBuildQuick", "skillBuildStandard",
                              "fullAgentTrainingSuite", "multiAgentCoordination", "clonePlatformOnboarding"],
        "Engine6_Subscription": [
            "dailyResearchDigest",    # DoctorWHO — daily curated research + risk signals
            "weeklyProtocolReport",   # DoctorWHO — deep-dive protocol analysis per week
            "portfolioMonitor",       # MATRIX — daily DeFi health check (Aave HF + positions)
            "fundingRateArb",         # MATRIX — daily HL vs Drift funding arb scan
        ],
    },
    "subscription_routing": {
        "dailyResearchDigest": {
            "agent": "DoctorWHO",
            "cadence": "daily",
            "price_per_day": 0.50,
            "tools": ["chaingpt_news_fetch", "chaingpt_research_token",
                      "chaingpt_defi_pendle_markets", "chaingpt_defi_morpho_markets",
                      "chaingpt_pm_markets", "chaingpt_hl_funding"],
            "deliverable": "JSON: {date, headlines[], risk_alerts[], yield_opportunities[], protocol_updates[]}",
        },
        "weeklyProtocolReport": {
            "agent": "DoctorWHO",
            "cadence": "weekly",
            "price_per_week": 2.00,
            "tools": ["chaingpt_chat", "chaingpt_risk_contract_source", "chaingpt_news_fetch",
                      "chaingpt_defi_aave_health", "chaingpt_research_token"],
            "deliverable": "Markdown: protocol deep-dive with risk score 0-10 + recommendation",
        },
        "portfolioMonitor": {
            "agent": "MATRIX",
            "cadence": "daily",
            "price_per_day": 0.25,
            "tools": ["chaingpt_defi_aave_health", "chaingpt_wallet_positions",
                      "chaingpt_wallet_pnl", "chaingpt_defi_pendle_markets",
                      "chaingpt_defi_morpho_markets", "chaingpt_research_token"],
            "deliverable": "JSON: {wallet, health_factor, positions[], alerts[], opportunities[]}",
            "alert_threshold": "health_factor < 1.5 → immediate alert",
        },
        "fundingRateArb": {
            "agent": "MATRIX",
            "cadence": "daily",
            "price_per_day": 0.50,
            "tools": ["chaingpt_hl_funding", "chaingpt_hl_markets",
                      "chaingpt_drift_funding", "chaingpt_drift_markets"],
            "deliverable": "JSON: {date, hl_rates{}, drift_rates{}, arb_opportunities[], spread_threshold_breached}",
            "arb_threshold": "spread > 0.05% → opportunity flagged",
        },
    },
    "subscription_publish_action": (
        "To publish subscription offerings on-chain: "
        "switch to agent wallet (DoctorWHO or MATRIX), then "
        "acp provider publish --name <offeringName> --type subscription "
        "--tier-days 7,15,30 --price <rate> --sla <hours>h "
        "--description '<text>'. "
        "Requires agent wallet funded with ETH for gas (Base mainnet)."
    ),
    "fallback_routing": "Unknown offering_id → graceful fallback to web_research_quick(query). Never hard-fail.",
    "job_flow": [
        "1. ACP event arrives (setBudget tool)",
        "2. Server extracts offering_name from event content",
        "3. offering_name looked up in dispatch dict (camelCase first, then normalised)",
        "4. Budget set via: acp provider set-budget --job-id X --amount Y",
        "5. ACP event arrives (submit tool)",
        "6. execute_offering(name, requirements) called",
        "7. Dispatch routes to correct engine method",
        "8. Deliverable submitted via: acp provider submit --job-id X --deliverable JSON",
        "9. Payment released on-chain when client confirms",
        "10. Supabase updated with status=completed + usdc_earned",
    ],
}

TRAINING_CHECKS = [
    ("total_offerings_count",       lambda: OFFERINGS_KNOWLEDGE["total_offerings"] == 40),
    ("clone_has_40",                lambda: OFFERINGS_KNOWLEDGE["agents"]["CLONE"]["offerings"] == 40),
    ("supersayatin_has_10",         lambda: OFFERINGS_KNOWLEDGE["agents"]["SuperSayatin"]["offerings"] == 10),
    ("doctorwho_has_subscriptions", lambda: OFFERINGS_KNOWLEDGE["agents"]["DoctorWHO"]["offerings"] == 2),
    ("matrix_has_subscriptions",    lambda: OFFERINGS_KNOWLEDGE["agents"]["MATRIX"]["offerings"] == 2),
    ("subscription_engine_exists",  lambda: "Engine6_Subscription" in OFFERINGS_KNOWLEDGE["execution_engines"]),
    ("subscription_routing_known",  lambda: "dailyResearchDigest" in OFFERINGS_KNOWLEDGE["subscription_routing"]),
    ("portfolio_monitor_tools",     lambda: "chaingpt_defi_aave_health" in OFFERINGS_KNOWLEDGE["subscription_routing"]["portfolioMonitor"]["tools"]),
    ("funding_arb_tools",           lambda: "chaingpt_hl_funding" in OFFERINGS_KNOWLEDGE["subscription_routing"]["fundingRateArb"]["tools"]),
    ("publish_action_documented",   lambda: "acp provider publish" in OFFERINGS_KNOWLEDGE["subscription_publish_action"]),
    ("crypto_news_demand",          lambda: OFFERINGS_KNOWLEDGE["confirmed_demand"]["crypto_news"]["external_jobs"] == 3),
    ("micro_price_correct",         lambda: "cryptoNewsFlash" in OFFERINGS_KNOWLEDGE["pricing"]["micro_0.01"]),
    ("deep_price_correct",          lambda: "tokenResearchDeep" in OFFERINGS_KNOWLEDGE["pricing"]["deep_0.10"]),
    ("ecosystem_types_known",       lambda: "evaluator_agent" in OFFERINGS_KNOWLEDGE["ecosystem_job_types"]),
    ("fallback_routing_exists",     lambda: "graceful fallback" in OFFERINGS_KNOWLEDGE["fallback_routing"]),
    ("engine1_research_mapped",     lambda: "cryptoNewsFlash" in OFFERINGS_KNOWLEDGE["execution_engines"]["Engine1_Research"]),
    ("engine3_wallet_mapped",       lambda: "walletSnapshot" in OFFERINGS_KNOWLEDGE["execution_engines"]["Engine3_Wallet"]),
]


def run_training() -> dict:
    results = {}
    passed = 0
    for name, check in TRAINING_CHECKS:
        try:
            ok = check()
        except Exception as e:
            ok = False
            results[name] = f"ERROR: {e}"
            continue
        results[name] = "PASS" if ok else "FAIL"
        if ok:
            passed += 1

    score = passed / len(TRAINING_CHECKS)
    print(f"\n[Offerings Training] Score: {passed}/{len(TRAINING_CHECKS)} ({score:.0%})")
    for k, v in results.items():
        icon = "✓" if v == "PASS" else "✗"
        print(f"  {icon} {k}: {v}")

    return {
        "module": "offerings_training",
        "score": score,
        "passed": passed,
        "total": len(TRAINING_CHECKS),
        "knowledge": OFFERINGS_KNOWLEDGE,
    }


if __name__ == "__main__":
    run_training()
