#!/usr/bin/env python3
"""
iCLONE — Auto Offerings Manager
Runs every 30 minutes. Detects uncovered niches, rotates low-performing
offerings, and keeps all 4 agents at maximum slot capacity.

Usage:
    python3 ops/auto_offerings_manager.py [--dry-run] [--force]

Cron (add to crontab):
    */30 * * * * cd /path/to/iclone && python3 ops/auto_offerings_manager.py >> logs/offerings.log 2>&1
"""

import json
import os
import subprocess
import sys
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log = logging.getLogger("offerings_manager")

DRY_RUN = "--dry-run" in sys.argv
FORCE   = "--force"   in sys.argv

# ─── Agent registry ───────────────────────────────────────────────────────────
AGENTS = [
    {"id": "019eae06-96cd-77d0-8f8b-a6abb71f0cd7", "name": "CLONE",        "max_slots": 40},
    {"id": "019ebb92-7415-7baa-93e9-ee19a7742877", "name": "SuperSayatin",  "max_slots": 40},
    {"id": "019ebb92-93e8-7b4e-b2e8-39c3419843c9", "name": "DoctorWHO",    "max_slots": 40},
    {"id": "019ebb92-b4be-7660-82d3-4b1647843e6a", "name": "MATRIX",       "max_slots": 40},
]

# ─── Master catalog — 180 offerings across high-demand niches ─────────────────
# Format: (name, description, price, sla_minutes, requirements, deliverable)
# Prices: 0.01 (quick <60s data) | 0.05 (standard research) | 0.10 (deep/complex)
CATALOG = [
    # ── Crypto News & Narratives ──────────────────────────────────────────────
    ("cryptoBreakingNews",    "Real-time breaking crypto news scan. Top 3 stories in the last 15 minutes.",
     "0.01", 30, "No input required.", "Top 3 breaking crypto headlines with source and impact rating."),
    ("cryptoHourlyDigest",    "Hourly crypto market digest. Price moves, news, and dominant sentiment.",
     "0.01", 30, "No input required.", "Hourly digest: top movers, key headlines, market sentiment."),
    ("cryptoDailyBrief",      "Daily crypto briefing: market overview, top stories, and watchlist.",
     "0.05", 60, "Optional: tokens to include in watchlist.", "Daily brief: market overview, top 5 stories, watchlist analysis."),
    ("narrativeDetector",     "Detect the dominant crypto narrative driving price action today.",
     "0.05", 60, "No input required.", "Dominant narrative, key tokens, catalysts, estimated duration."),
    ("narrativeRotationAlert","Alert when a major crypto narrative is showing signs of rotation or exhaustion.",
     "0.05", 60, "Current narrative or sector to monitor.", "Rotation signal: strength, evidence, emerging narrative to watch."),
    ("catalystCalendar",      "Upcoming on-chain events, unlocks, launches, and protocol upgrades this week.",
     "0.05", 90, "Optional: chains or protocols to focus on.", "7-day catalyst calendar with dates, events, and expected impact."),
    ("fudOrFactChecker",      "Verify whether a circulating crypto claim or news is FUD or fact.",
     "0.01", 30, "The claim or news item to verify.", "Verdict (FUD/Fact/Unclear), evidence, and source links."),
    ("alphaLeakDetector",     "Scan crypto alpha channels for unconfirmed but credible early signals.",
     "0.10", 120, "No input required.", "Top 3 unconfirmed alpha signals with credibility rating and source."),
    ("kol_sentiment_scan",    "Scan top crypto KOL posts for consensus sentiment on a token or sector.",
     "0.05", 60, "Token symbol or sector to scan.", "KOL sentiment distribution, key quotes, and overall bias."),
    ("ecosystemUpdate",       "Latest updates for a specific blockchain ecosystem (launches, TVL, devs).",
     "0.05", 90, "Ecosystem name (e.g. Base, Solana, Sui).", "Ecosystem update: TVL, new launches, developer activity, outlook."),

    # ── Token & Protocol Research ─────────────────────────────────────────────
    ("tokenSnapshotQuick",    "30-second token snapshot: price, 24h change, volume, market cap, holders.",
     "0.01", 30, "Token symbol or contract address.", "Token snapshot: price, 24h delta, volume, mcap, holder count."),
    ("tokenFundamentals",     "Token fundamental analysis: tokenomics, team, use case, competitive position.",
     "0.10", 180, "Token name or symbol and research depth (light/deep).", "Fundamentals report: tokenomics breakdown, team assessment, moat analysis, verdict."),
    ("tokenComparison",       "Side-by-side comparison of two tokens across key metrics.",
     "0.05", 90, "Two token symbols to compare.", "Comparison table: tokenomics, market position, risk, recommendation."),
    ("rugPullScreener",       "Screen a new token for rug pull red flags: contract, LP, team, socials.",
     "0.05", 60, "Token contract address and chain.", "Safety report: risk score 0-100, red flags found, recommendation."),
    ("tokenUnlockImpact",     "Assess the price impact of an upcoming token unlock event.",
     "0.05", 60, "Token symbol and unlock date/amount.", "Unlock impact assessment: supply shock estimate, historical comps, price outlook."),
    ("protocolRevenueAnalysis","Analyse a DeFi protocol's revenue, fee structure, and sustainability.",
     "0.10", 180, "Protocol name and chain.", "Revenue analysis: fee breakdown, monthly trend, sustainability score, comps."),
    ("protocolRiskScore",     "Risk score a DeFi protocol on smart contract, governance, and market risk.",
     "0.05", 90, "Protocol name.", "Risk scorecard: contract (0-10), governance (0-10), market (0-10), total risk rating."),
    ("tvlTrendAnalysis",      "TVL trend analysis for a protocol or chain over the last 30 days.",
     "0.05", 60, "Protocol or chain name.", "TVL trend: 30d chart data, growth rate, relative ranking, outlook."),
    ("liquidityDepthCheck",   "Check the liquidity depth and slippage for a token trade size.",
     "0.01", 30, "Token symbol, DEX, and trade size in USD.", "Liquidity report: depth, estimated slippage, optimal routing suggestion."),
    ("forkAnalysis",          "Analyse a protocol fork: differences from original, risk, opportunity.",
     "0.05", 90, "Fork name and original protocol.", "Fork analysis: diff summary, risk factors, airdrop eligibility, verdict."),

    # ── Trading Intelligence ──────────────────────────────────────────────────
    ("btcDominanceSignal",    "BTC dominance trend signal: rising/falling with alt rotation implication.",
     "0.01", 30, "No input required.", "BTC dominance: current level, 7d trend, alt season signal, action bias."),
    ("fearGreedInterpretation","Interpret the current Crypto Fear & Greed Index with contrarian context.",
     "0.01", 30, "No input required.", "F&G level, historical context, contrarian signal, what it means for traders."),
    ("supportResistanceScan", "Key support and resistance levels for a token on 4H and daily charts.",
     "0.05", 60, "Token symbol.", "S/R map: key levels, distance from current price, historical strength."),
    ("breakoutScreener",      "Screen for tokens approaching technical breakout zones right now.",
     "0.05", 60, "Optional: sector or chain filter.", "Top 5 breakout candidates: setup quality, risk/reward, key levels."),
    ("volumeAnomalyDetector", "Detect unusual volume spikes vs 30-day average across top 200 tokens.",
     "0.05", 60, "No input required.", "Volume anomalies: tokens with >3x average volume, context, possible cause."),
    ("fundingRateMonitor",    "Perp funding rates across major exchanges — identify crowded positions.",
     "0.01", 30, "Optional: specific token.", "Funding rate table: top funded longs/shorts, crowded trade warning."),
    ("openInterestAnalysis",  "Open interest changes as a leading indicator for short-term price moves.",
     "0.05", 60, "Token symbol.", "OI analysis: 24h change, oi/mcap ratio, signal for directional bias."),
    ("liquidationMapReport",  "Liquidation cluster map for a token — where are the pain points?",
     "0.05", 60, "Token symbol and timeframe.", "Liquidation map: key clusters above/below, distance, cascade risk level."),
    ("trendStrengthScore",    "Score the trend strength of a token using ADX and momentum indicators.",
     "0.01", 30, "Token symbol.", "Trend score: ADX level, trend direction, strength rating, hold/fade signal."),
    ("swingTradeSetup",       "Identify a high-probability swing trade setup with defined entry, stop, target.",
     "0.05", 90, "Token symbol and preferred timeframe.", "Setup: entry zone, stop loss, take profit, R:R ratio, conviction score."),

    # ── On-Chain Intelligence ─────────────────────────────────────────────────
    ("whaleAlertDigest",      "Recent large on-chain moves (>$500k) for a token in the last 4 hours.",
     "0.05", 60, "Token symbol or contract address.", "Whale digest: top 5 moves, wallet labels, direction, significance."),
    ("exchangeFlowSignal",    "Net exchange inflow/outflow for a token — selling or accumulation signal?",
     "0.01", 30, "Token symbol.", "Flow signal: 24h net flow, exchange breakdown, bullish/bearish bias."),
    ("smartMoneyWallet",      "Identify smart money wallets actively accumulating a token.",
     "0.05", 90, "Token symbol.", "Smart money wallets: top 5 accumulators, entry prices, position size."),
    ("walletProfitHistory",   "Profit/loss history and win rate for an on-chain wallet.",
     "0.05", 90, "Wallet address and chain.", "P&L history: total realised, win rate, best/worst trades, risk profile."),
    ("transactionDecoder",    "Decode a complex on-chain transaction into plain English.",
     "0.01", 30, "Transaction hash and chain.", "Transaction decoded: what happened, who initiated, what moved, why it matters."),
    ("contractAuditQuick",    "Quick smart contract audit: ownership, mint function, honeypot check.",
     "0.05", 60, "Contract address and chain.", "Audit summary: ownership structure, dangerous functions, honeypot verdict."),
    ("nftWalletAnalysis",     "NFT holdings analysis for a wallet: floor value, blue-chips, performance.",
     "0.05", 60, "Wallet address and chain.", "NFT portfolio: floor total, blue-chip count, best/worst positions."),
    ("mevActivityCheck",      "Check if a wallet or contract has been targeted by MEV bots recently.",
     "0.05", 60, "Wallet or contract address.", "MEV report: sandwiches, frontrunning events, estimated value extracted."),
    ("bridgeFlowMonitor",     "Monitor bridge flows between two chains for a token.",
     "0.05", 60, "Token and chains (e.g. ETH → Base).", "Bridge flow: 24h volume, direction bias, net accumulation on destination."),
    ("onChainSignalBundle",   "Bundle of 5 on-chain signals for a token: flows, whales, smart money, holders, dev.",
     "0.10", 180, "Token symbol.", "5-signal bundle: flows, whale activity, smart money, holder trend, dev wallet."),

    # ── DeFi & Yield ─────────────────────────────────────────────────────────
    ("yieldRanker",           "Rank top DeFi yield opportunities right now above a minimum APY.",
     "0.05", 90, "Minimum APY (%), preferred chains, risk tolerance (low/med/high).", "Top 10 yield opportunities: protocol, APY, TVL, risk rating, link."),
    ("stablecoinYieldScan",   "Best stablecoin yields across lending and LP protocols right now.",
     "0.05", 60, "No input required.", "Stablecoin yield table: top 10 options, APY, protocol, risk rating."),
    ("liquidityPoolAnalysis", "Analyse an LP position: IL risk, fee income, and net return estimate.",
     "0.05", 90, "Pool address or token pair and DEX.", "LP analysis: IL estimate, fee APY, net return, hold-vs-LP comparison."),
    ("airdropEligibilityCheck","Check if a wallet is eligible for known upcoming airdrops.",
     "0.05", 60, "Wallet address and chain.", "Airdrop eligibility: protocols farming, estimated value, gaps to fill."),
    ("lendingRateArbitrage",  "Find lending rate discrepancies across protocols to arbitrage.",
     "0.05", 60, "Token to lend/borrow.", "Rate arb table: supply vs borrow rates by protocol, spread, net opportunity."),
    ("loopingStrategyCheck",  "Assess the safety and profitability of a leveraged looping strategy.",
     "0.05", 90, "Collateral token, borrowed token, protocol, leverage.", "Looping assessment: liquidation price, effective yield, risk rating, max safe leverage."),
    ("veTokenVotingSignal",   "Optimal vote allocation for a veToken governance round to maximise yield.",
     "0.05", 90, "Protocol name and veToken held.", "Vote allocation: top pools by bribe-adjusted APY, recommended splits."),
    ("defiInsuranceCheck",    "Check DeFi coverage options for a protocol from Nexus, Sherlock, or Unslashed.",
     "0.01", 30, "Protocol name.", "Coverage available: providers, premiums, coverage limits, recommendation."),
    ("farmingStrategyBuilder","Build a yield farming strategy for a given capital and risk profile.",
     "0.10", 180, "Capital in USD, risk tolerance, chains, time horizon.", "Strategy plan: allocation, protocols, expected APY, IL risk, rebalance schedule."),
    ("gaugeVotingAnalysis",   "Analyse current Curve/Balancer/Velodrome gauge votes and bribe flows.",
     "0.05", 90, "Platform name.", "Gauge analysis: top voted pools, bribe $/vote, optimal gauge target."),

    # ── NFT & Collectibles ────────────────────────────────────────────────────
    ("nftFloorTracker",       "Track floor price movement and volume for an NFT collection.",
     "0.01", 30, "Collection name or contract address.", "Floor snapshot: current price, 24h delta, 7d trend, volume ranking."),
    ("nftRarityScore",        "Rarity score and rank for a specific NFT within its collection.",
     "0.01", 30, "Collection name and token ID.", "Rarity score, trait breakdown, rank in collection, floor vs rare premium."),
    ("nftMintAnalysis",       "Analyse a new NFT mint: team, art, utility, community strength.",
     "0.05", 90, "Project name, mint date, and contract if available.", "Mint analysis: utility score, community size, team track record, buy/skip verdict."),
    ("nftWhaleTracker",       "Wallets accumulating a specific NFT collection in the last 48 hours.",
     "0.05", 60, "Collection name.", "Whale activity: top 5 accumulators, wallet labels, quantities, floor impact."),
    ("nftWashTradingCheck",   "Detect wash trading patterns in an NFT collection's volume.",
     "0.05", 60, "Collection name or contract.", "Wash trading report: suspicious volume %, wallet clusters, adjusted real volume."),

    # ── Content & Copywriting ─────────────────────────────────────────────────
    ("tweetThread",           "Write a punchy, viral-optimised crypto Twitter thread on any topic.",
     "0.01", 60, "Topic, angle, and desired tone (educational/alpha/opinion).", "5-8 tweet thread with hooks, data points, and a strong CTA."),
    ("tweetSingle",           "Write a single high-engagement tweet on a crypto topic.",
     "0.01", 30, "Topic and tone.", "One polished tweet with hook, content, and CTA."),
    ("newsletterSection",     "Write one section of a crypto newsletter (500–800 words).",
     "0.05", 60, "Section topic and any data to include.", "Newsletter section: headline, body, key takeaways, call to action."),
    ("linkedInPost",          "Write a professional LinkedIn post about a crypto/Web3 topic.",
     "0.01", 30, "Topic and professional angle.", "LinkedIn post: hook, insight, takeaway, 5 hashtags."),
    ("pressReleaseDraft",     "Draft a crypto project press release from a brief.",
     "0.05", 90, "Project name, announcement, and key points.", "Press release: headline, dateline, body, boilerplate, contact section."),
    ("pitchDeckNarrative",    "Write the narrative script for a crypto project pitch deck.",
     "0.10", 180, "Project overview, problem, solution, traction.", "Pitch narrative: slide-by-slide story arc, key messages, investor hook."),
    ("whitepaperSection",     "Write a technical section of a crypto whitepaper.",
     "0.10", 240, "Section topic, technical depth required, audience.", "Whitepaper section: structured prose, technical precision, citations where applicable."),
    ("marketingCopyBundle",   "Bundle of 5 crypto marketing copy pieces (tweet, email subject, CTA, bio, headline).",
     "0.05", 90, "Project name, audience, and key differentiator.", "5-piece copy bundle: tweet, email subject, CTA, bio, and landing page headline."),
    ("contentCalendarWeek",   "Create a 7-day content calendar for a crypto project or KOL.",
     "0.05", 90, "Project/persona and weekly goal (growth/education/sales).", "7-day calendar: daily topic, format, angle, and suggested publish time."),
    ("translateCryptoEN_PT",  "Translate crypto content from English to Portuguese (BR or PT).",
     "0.01", 30, "Content to translate and target dialect (BR or PT).", "Translated content with crypto terminology preserved correctly."),

    # ── Code & Automation ─────────────────────────────────────────────────────
    ("tradingBotSnippet",     "Write a Python trading bot snippet for a specific strategy.",
     "0.05", 90, "Strategy description, exchange (ccxt), and language.", "Working bot snippet with entry/exit logic, order placement, and error handling."),
    ("defiContractInteraction","Write Python/JS code to interact with a DeFi contract (deposit, withdraw, claim).",
     "0.05", 90, "Protocol name, action, and chain.", "Working code: contract ABI call, gas estimate, transaction construction."),
    ("priceAlertBot",         "Write a Python script that monitors a token price and sends alerts.",
     "0.05", 60, "Token, threshold, and alert method (Telegram/Discord/email).", "Alert bot: price polling loop, threshold check, notification dispatch."),
    ("onChainDataPipeline",   "Write a data pipeline to extract and store on-chain events to a database.",
     "0.10", 180, "Event type, chain, contract, and target DB (Postgres/Supabase).", "Pipeline code: event listener, data transform, DB insert, error handling."),
    ("walletTrackerScript",   "Python script to track multiple wallets and alert on new transactions.",
     "0.05", 90, "Wallet list, chain, and alert channel.", "Tracker script: polling loop, multi-wallet support, alert dispatch."),
    ("apiWrapperGenerator",   "Generate a typed Python wrapper for any REST API from its OpenAPI spec.",
     "0.05", 90, "API name and OpenAPI spec URL or paste.", "Typed Python wrapper: client class, all endpoints, type hints, error handling."),
    ("telegramBotQuick",      "Write a simple Telegram bot for a crypto use case.",
     "0.05", 90, "Bot purpose and key commands.", "Telegram bot: command handlers, API integrations, deployment guide."),
    ("subgraphQuery",         "Write a GraphQL query for The Graph subgraph to extract DeFi data.",
     "0.01", 30, "Protocol/subgraph name and data needed.", "GraphQL query with field selection, filters, ordering, and pagination."),
    ("soliditySnippet",       "Write or review a Solidity function for a specific contract purpose.",
     "0.05", 60, "Function description, security constraints, Solidity version.", "Solidity function: implementation, NatSpec comments, known security considerations."),
    ("web3jsSetup",           "Write the wallet connection and provider setup for a Web3 dApp (ethers.js).",
     "0.05", 60, "Framework (React/Next), wallet type (MetaMask/WalletConnect), chain.", "Provider setup: wallet connect, chain switching, signer access, error states."),

    # ── Market Data & Analytics ───────────────────────────────────────────────
    ("marketCapTierShift",    "Detect tokens that just moved between market cap tiers (micro→small, small→mid).",
     "0.05", 60, "No input required.", "Tier shifts: tokens that crossed tier boundaries in last 24h with context."),
    ("sectorHeatmap",         "Market sector performance heatmap: which sectors are pumping or dumping?",
     "0.01", 30, "No input required.", "Sector heatmap: 24h performance by category, top and bottom 3 sectors."),
    ("gasOptimizationReport", "Optimal gas timing for a transaction on Ethereum or L2.",
     "0.01", 30, "Chain and transaction type (swap/mint/bridge).", "Gas report: current fast/standard prices, optimal timing window, savings estimate."),
    ("crossChainArb",         "Cross-chain price arbitrage opportunities for a token right now.",
     "0.05", 60, "Token symbol.", "Arb opportunities: price diff by chain, bridge cost, net profit estimate, risk level."),
    ("stablecoinDepegMonitor","Check if any major stablecoin is showing depeg risk.",
     "0.01", 30, "No input required.", "Depeg monitor: current pegs, deviation %, risk level, historical context."),
    ("globalMacroImpact",     "How a macro event (CPI, FOMC, ETF news) will likely affect crypto markets.",
     "0.05", 60, "Event name and date.", "Macro impact: expected reaction, historical comps, key levels to watch."),
    ("correlationMatrix",     "Correlation matrix between BTC, ETH, and top alts for the last 30 days.",
     "0.05", 90, "No input required.", "Correlation matrix: heatmap data, highest/lowest correlations, diversification insight."),
    ("seasonalityReport",     "Historical seasonality for a token or the market by month.",
     "0.05", 90, "Token symbol or 'market'.", "Seasonality report: monthly returns heatmap, best/worst months, current month outlook."),
    ("regulatoryUpdateScan",  "Scan for recent regulatory news affecting crypto in key jurisdictions.",
     "0.05", 60, "No input required.", "Regulatory digest: top 3 updates, jurisdictions, risk level, market impact."),
    ("etfFlowMonitor",        "Monitor Bitcoin and Ethereum ETF flows for institutional demand signals.",
     "0.01", 30, "No input required.", "ETF flows: daily net inflow/outflow, rolling 7d trend, demand signal."),

    # ── AI Agents & Virtuals Ecosystem ────────────────────────────────────────
    ("agentPerformanceAudit", "Audit an AI agent's ACP performance: jobs, revenue, fail rate.",
     "0.05", 90, "Agent name or address.", "Performance audit: jobs completed, revenue, fail rate, improvement areas."),
    ("virtualTokenResearch",  "Research a Virtuals Protocol agent token: fundamentals, traction, price.",
     "0.05", 90, "Agent name or VIRTUAL token symbol.", "Agent token research: VA stats, traction metrics, token price analysis, verdict."),
    ("acpMarketplaceAnalysis","Analyse the ACP offerings marketplace: best-selling categories and prices.",
     "0.10", 180, "No input required.", "Marketplace analysis: top categories by volume, price distribution, whitespace niches."),
    ("agentCollaborationPlan","Design a multi-agent collaboration plan for a complex task.",
     "0.10", 180, "Task description and available agents.", "Collaboration plan: agent roles, task split, data handoffs, quality gates."),
    ("promptEngineeringFix",  "Diagnose and rewrite an underperforming AI agent prompt.",
     "0.05", 60, "Current prompt and what it's failing to do.", "Rewritten prompt with explanation of changes and expected improvement."),
    ("trainingDataCuration",  "Curate and clean a training dataset for a specific AI domain.",
     "0.10", 240, "Domain, format (JSON/CSV), and sample data.", "Curated dataset: clean examples, format guide, quality metrics."),
    ("agentSkillBlueprint",   "Write the technical blueprint for a new AI agent skill module.",
     "0.05", 90, "Skill purpose, inputs, outputs, constraints.", "Blueprint: architecture, function signatures, data contracts, test cases."),

    # ── Research & Due Diligence ──────────────────────────────────────────────
    ("teamBackgroundCheck",   "Research the team behind a crypto project: track record, red flags.",
     "0.05", 90, "Project name.", "Team report: key members, past projects, LinkedIn/social verification, red flags."),
    ("competitiveAnalysis",   "Competitive analysis of a crypto project vs its top 3 competitors.",
     "0.10", 180, "Project name and sector.", "Competitive analysis: feature matrix, market share, moat assessment, winner thesis."),
    ("investmentThesis",      "Build a structured investment thesis for a token: bull/bear/base case.",
     "0.10", 240, "Token name and investment horizon.", "Investment thesis: bull/bear/base cases, key catalysts, risk factors, price targets."),
    ("vcFundingAnalysis",     "Analyse VC funding rounds and investor quality for a crypto project.",
     "0.05", 90, "Project name.", "VC analysis: rounds, investors quality tier, unlock schedules, implied valuation."),
    ("githubActivityScan",    "Scan a crypto project's GitHub for developer activity and code quality signals.",
     "0.05", 60, "GitHub org or repo URL.", "GitHub scan: commit frequency, contributor count, issue resolution, code health score."),
    ("roadmapVerification",   "Verify a crypto project's roadmap claims against on-chain and off-chain evidence.",
     "0.10", 180, "Project name and roadmap source.", "Verification report: claims vs evidence, hit rate, credibility score."),
    ("tokenomicsAudit",       "Deep tokenomics audit: supply schedule, inflation rate, value accrual.",
     "0.10", 180, "Token name.", "Tokenomics audit: emission schedule, inflation rate, value capture, dilution risk."),
    ("communityHealthCheck",  "Community health metrics: Discord activity, Telegram growth, Twitter engagement.",
     "0.05", 60, "Project name.", "Community health: size, growth rate, engagement quality, spam/shill ratio."),

    # ── Productivity & Automation ─────────────────────────────────────────────
    ("meetingNotesFormatter", "Format raw meeting notes into structured action items and summary.",
     "0.01", 30, "Raw meeting notes.", "Formatted notes: summary, decisions, action items with owners."),
    ("emailDraftCrypto",      "Draft a professional email for a crypto/Web3 business context.",
     "0.01", 30, "Context, recipient type, and goal.", "Polished email draft with subject line, body, and CTA."),
    ("dataVisualizationSpec", "Write the data visualisation spec for a crypto dashboard widget.",
     "0.05", 60, "Data available and insight to show.", "Viz spec: chart type, axes, colors, interactions, data queries."),
    ("cronJobSpec",           "Write the specification and code for a recurring automation task.",
     "0.05", 60, "Task description, frequency, and tech stack.", "Cron spec: code, schedule expression, error handling, monitoring."),
    ("documentSummarizer",    "Summarise a long document (whitepaper, report, thread) into key points.",
     "0.01", 30, "Document text or URL.", "Summary: 5 key points, one-paragraph tldr, action items."),
]

# ─── ACP CLI helpers ──────────────────────────────────────────────────────────

def run(cmd: list[str], capture: bool = True) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=capture, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def switch_agent(agent_id: str) -> bool:
    code, _ = run(["acp", "agent", "use", "--agent-id", agent_id])
    return code == 0


def list_offerings() -> list[dict]:
    code, out = run(["acp", "offering", "list"])
    if code != 0 or not out or "No offerings" in out:
        return []
    offerings = []
    for line in out.strip().split("\n")[1:]:  # skip header
        parts = line.split("\t")
        if len(parts) >= 2:
            offerings.append({"id": parts[0].strip(), "name": parts[1].strip()})
    return offerings


def publish_offering(name: str, desc: str, price: str, sla: int, req: str, deliv: str) -> bool:
    if DRY_RUN:
        log.info("    [DRY-RUN] would publish: %s @ %s USDC", name, price)
        return True
    code, out = run([
        "acp", "offering", "create",
        "--name", name,
        "--description", desc,
        "--price-type", "fixed",
        "--price-value", price,
        "--sla-minutes", str(sla),
        "--requirements", req,
        "--deliverable", deliv,
        "--no-required-funds",
        "--no-hidden",
    ])
    return code == 0


def delete_offering(offering_id: str) -> bool:
    if DRY_RUN:
        log.info("    [DRY-RUN] would delete offering %s", offering_id)
        return True
    code, _ = run(["acp", "offering", "delete", "--offering-id", offering_id])
    return code == 0


# ─── State tracking ───────────────────────────────────────────────────────────

STATE_FILE = os.path.join(os.path.dirname(__file__), ".offerings_state.json")

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"published": {}, "last_rotation": None}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ─── Main rotation logic ──────────────────────────────────────────────────────

def fill_agent_slots(agent: dict, state: dict) -> dict:
    """Fill an agent to its max_slots with offerings from the catalog."""
    agent_id   = agent["id"]
    agent_name = agent["name"]
    max_slots  = agent["max_slots"]

    if not switch_agent(agent_id):
        log.error("  Failed to switch to agent %s", agent_name)
        return {"agent": agent_name, "published": 0, "skipped": 0, "errors": 0}

    current = list_offerings()
    current_names = {o["name"] for o in current}
    slots_used = len(current)
    slots_free = max_slots - slots_used

    log.info("  %s: %d/%d slots used, %d free", agent_name, slots_used, max_slots, slots_free)

    if slots_free == 0 and not FORCE:
        log.info("  %s: full, skipping", agent_name)
        return {"agent": agent_name, "published": 0, "skipped": slots_used, "errors": 0}

    # If FORCE and full — remove bottom N to make room for new ones
    if slots_free == 0 and FORCE:
        to_remove = min(10, len(current))
        log.info("  %s: FORCE — removing %d offerings to make room", agent_name, to_remove)
        for o in current[-to_remove:]:
            if delete_offering(o["id"]):
                current_names.discard(o["name"])
                slots_free += 1
            time.sleep(0.3)

    # Track which catalog entries have been published globally
    published_globally = state.get("published", {})
    published_count = 0
    error_count = 0

    for entry in CATALOG:
        if slots_free <= 0:
            break
        name, desc, price, sla, req, deliv = entry

        # Skip if already on this agent
        if name in current_names:
            continue

        # Skip if recently published on any agent (avoid duplicates across agents)
        if name in published_globally:
            continue

        log.info("    Publishing: %s @ %s USDC (sla %dm)", name, price, sla)
        ok = publish_offering(name, desc, price, sla, req, deliv)

        if ok:
            published_globally[name] = {"agent": agent_name, "ts": datetime.now(timezone.utc).isoformat()}
            current_names.add(name)
            slots_free -= 1
            published_count += 1
            time.sleep(0.4)
        else:
            log.warning("    Failed to publish: %s", name)
            error_count += 1

    state["published"] = published_globally
    return {"agent": agent_name, "published": published_count, "skipped": slots_used, "errors": error_count}


def run_rotation() -> None:
    log.info("=== Auto Offerings Manager — %s ===", datetime.now(timezone.utc).isoformat())
    if DRY_RUN:
        log.info("  Mode: DRY-RUN (no actual changes)")
    if FORCE:
        log.info("  Mode: FORCE (will rotate existing offerings)")

    state = load_state()
    summary = []

    for agent in AGENTS:
        log.info("── %s ──────────────────────────────────", agent["name"])
        result = fill_agent_slots(agent, state)
        summary.append(result)
        time.sleep(1)

    # Restore CLONE as active
    switch_agent(AGENTS[0]["id"])

    state["last_rotation"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    total_published = sum(r["published"] for r in summary)
    total_errors    = sum(r["errors"]    for r in summary)

    log.info("=== Done — %d published, %d errors ===", total_published, total_errors)
    for r in summary:
        log.info("  %s: +%d published, %d errors", r["agent"], r["published"], r["errors"])


if __name__ == "__main__":
    run_rotation()
