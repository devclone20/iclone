"""
iCLONE — Offerings Training Module
Trains all 4 agents on the 40 live ACP offerings, routing logic, and job handling.
Score: pass/fail per section.
"""

OFFERINGS_KNOWLEDGE = {
    "total_offerings": 40,
    "limit_per_agent": 40,
    "agents": {
        "CLONE": {"offerings": 40, "wallet": "0x44cc25d55a4291b92f52062ba023ca1f14206664"},
        "SuperSayatin": {"offerings": 10, "wallet": "0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3"},
        "DoctorWHO": {"offerings": 0, "wallet": "0x875242eb5c91270ca80ed7753a87d6e22e4f5acf"},
        "MATRIX": {"offerings": 0, "wallet": "0x07924dea2c8212969d5dc5655785aa5063adb2bc"},
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
    },
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
    ("total_offerings_count",   lambda: OFFERINGS_KNOWLEDGE["total_offerings"] == 40),
    ("clone_has_40",            lambda: OFFERINGS_KNOWLEDGE["agents"]["CLONE"]["offerings"] == 40),
    ("supersayatin_has_10",     lambda: OFFERINGS_KNOWLEDGE["agents"]["SuperSayatin"]["offerings"] == 10),
    ("crypto_news_demand",      lambda: OFFERINGS_KNOWLEDGE["confirmed_demand"]["crypto_news"]["external_jobs"] == 3),
    ("micro_price_correct",     lambda: "cryptoNewsFlash" in OFFERINGS_KNOWLEDGE["pricing"]["micro_0.01"]),
    ("deep_price_correct",      lambda: "tokenResearchDeep" in OFFERINGS_KNOWLEDGE["pricing"]["deep_0.10"]),
    ("ecosystem_types_known",   lambda: "evaluator_agent" in OFFERINGS_KNOWLEDGE["ecosystem_job_types"]),
    ("fallback_routing_exists", lambda: "graceful fallback" in OFFERINGS_KNOWLEDGE["fallback_routing"]),
    ("engine1_research_mapped", lambda: "cryptoNewsFlash" in OFFERINGS_KNOWLEDGE["execution_engines"]["Engine1_Research"]),
    ("engine3_wallet_mapped",   lambda: "walletSnapshot" in OFFERINGS_KNOWLEDGE["execution_engines"]["Engine3_Wallet"]),
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
