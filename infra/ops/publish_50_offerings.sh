#!/bin/bash
# iCLONE — 50 offerings baseados em dados reais de mercado
# Demand confirmada: crypto_news (3 jobs externos), wallet, research, threads
# Preços: 0.01 (micro) | 0.05 (standard) | 0.10 (deep)
set -euo pipefail

acp agent use --agent-id 019eae06-96cd-77d0-8f8b-a6abb71f0cd7 > /dev/null 2>&1

c() {
  acp offering create \
    --name "$1" \
    --description "$2" \
    --price-type fixed \
    --price-value "$3" \
    --sla-minutes "$4" \
    --requirements "$5" \
    --deliverable "$6" \
    --no-required-funds \
    --no-hidden 2>&1 | grep -c "created" > /dev/null && echo "  ✓ $1 @ \$$3"
}

echo "================================================"
echo "  iCLONE — 50 Offerings (market-validated)"
echo "================================================"

# ═══════════════════════════════════════════════════
# BLOCO 1 — CRYPTO NEWS (demand confirmada: 3 jobs externos)
# O agente 0x7457b... comprou crypto_news 3x. Expandir ao máximo.
# ═══════════════════════════════════════════════════
echo ""
echo "── [1] Crypto News (demand confirmada) ────────"

c "cryptoNewsFlash" \
  "Top 5 crypto news of the last hour. Bullet format, source links included." \
  0.01 30 \
  "No input required. Returns latest crypto news automatically." \
  "5 bullet-point news items with headlines, 1-line summaries and source links."

c "cryptoNewsDaily" \
  "Daily crypto news digest. Top 10 stories, market mood, key events." \
  0.01 60 \
  "Optional: specify tokens or sectors to prioritise (e.g. BTC, DeFi, L2)." \
  "Daily digest: top 10 stories, market mood score, 3 key events to watch."

c "cryptoNewsWeekly" \
  "Weekly crypto recap. Winners, losers, narratives, what to watch next week." \
  0.05 120 \
  "Optional: sectors or tokens to focus on." \
  "Weekly report: top narratives, winners/losers, outlook for next 7 days."

c "cryptoNewsByToken" \
  "All news for a specific token in the last 24h. Aggregated and summarised." \
  0.01 45 \
  "Token symbol (e.g. ETH, SOL, VIRTUAL)." \
  "Token news summary: latest headlines, sentiment score, key developments."

c "cryptoNewsSentiment" \
  "Sentiment analysis of crypto news. Bullish/bearish signal with confidence score." \
  0.01 30 \
  "Token symbol or market sector to analyse." \
  "Sentiment report: score -100 to +100, key drivers, confidence level."

c "cryptoNewsNarrative" \
  "Identify the dominant market narrative from today's news. What story is the market telling?" \
  0.05 60 \
  "Optional: time period (last 24h, 48h, 7d)." \
  "Narrative report: dominant theme, supporting evidence, trading implication."

c "cryptoNewsAlpha" \
  "Find alpha signals buried in today's crypto news. Underreported stories with price potential." \
  0.05 90 \
  "Optional: preferred sectors or chains to focus on." \
  "Alpha signals: 3-5 underreported stories, why they matter, potential impact."

# ═══════════════════════════════════════════════════
# BLOCO 2 — CRYPTO RESEARCH (validado: research-quick comprado)
# ═══════════════════════════════════════════════════
echo ""
echo "── [2] Crypto Research (validado) ─────────────"

c "tokenSnapshotQuick" \
  "Quick token snapshot: price, market cap, volume, 24h change, key metrics." \
  0.01 30 \
  "Token symbol (e.g. BTC, ETH, VIRTUAL)." \
  "Token snapshot: price, mcap, volume, 24h%, key on-chain metrics."

c "tokenResearchStandard" \
  "Research report on a token. Fundamentals, tokenomics, team, outlook." \
  0.05 120 \
  "Token name or symbol and specific research focus." \
  "Research report: overview, tokenomics, team, risks, 30-day outlook."

c "tokenResearchDeep" \
  "Deep-dive token research. Full fundamental analysis with competitive landscape." \
  0.10 240 \
  "Token or protocol name and research scope (fundamentals, tech, market, all)." \
  "Full report: fundamentals, tech analysis, competitive moat, risks, verdict."

c "protocolAnalysis" \
  "Analyse a DeFi or Web3 protocol. TVL, revenue, risks, user growth." \
  0.05 120 \
  "Protocol name and chain." \
  "Protocol report: TVL trend, revenue, user growth, security history, outlook."

c "narrativeScanner" \
  "Scan current crypto narratives and rank them by momentum and longevity." \
  0.05 90 \
  "Optional: time horizon (short-term trading vs. 3-month positioning)." \
  "Narrative ranking: top 5 active narratives, momentum score, suggested plays."

c "sectorComparison" \
  "Compare two crypto sectors head-to-head. Which is stronger right now and why." \
  0.05 90 \
  "Two sectors to compare (e.g. DeFi vs. L2, AI tokens vs. GameFi)." \
  "Comparison report: metrics, momentum, risk, verdict on which to favour."

c "competitorMap" \
  "Map the competitive landscape for a token or protocol. Who are the real competitors?" \
  0.05 120 \
  "Token or protocol name." \
  "Competitor map: top 5 rivals, differentiators, market share, competitive moat."

# ═══════════════════════════════════════════════════
# BLOCO 3 — WALLET ANALYSIS (validado: wallet-health comprado a $0.50)
# ═══════════════════════════════════════════════════
echo ""
echo "── [3] Wallet Analysis (validado) ─────────────"

c "walletSnapshot" \
  "Instant wallet snapshot. Token holdings and USD values for any EVM wallet." \
  0.01 30 \
  "EVM wallet address and chain (Base, Ethereum, Polygon, Arbitrum, etc)." \
  "Holdings snapshot: tokens, amounts, USD values, total portfolio value."

c "walletHealthAudit" \
  "Wallet health audit. Risky approvals, dust attacks, exposed assets, risk score." \
  0.05 90 \
  "Wallet address and chains to audit." \
  "Health report: risk score 0-100, risky approvals list, dust flagged, recommendations."

c "walletPnL" \
  "Calculate wallet PnL for a given period. Realised and unrealised gains/losses." \
  0.05 120 \
  "Wallet address, chain and time period (7d, 30d, 90d, all-time)." \
  "PnL report: realised gains/losses, unrealised positions, best/worst trades."

c "walletBehaviourProfile" \
  "Profile a wallet's trading behaviour. Degen, holder, bot, whale, or smart money?" \
  0.05 120 \
  "Wallet address and chain." \
  "Behaviour profile: category label, activity patterns, risk appetite, consistency score."

c "walletForensics" \
  "Full wallet forensics. Transaction history, counterparties, flow of funds." \
  0.10 180 \
  "Wallet address, chain and investigation focus." \
  "Forensics report: transaction history, key counterparties, fund flows, red flags."

c "smartMoneyTracker" \
  "Track what smart money wallets are buying right now. Follow the alpha." \
  0.05 90 \
  "Optional: sector focus or chain preference." \
  "Smart money report: top 5 recent moves, tokens being accumulated, thesis."

c "whaleActivityAlert" \
  "Detect recent whale activity for a token. Large buys, sells, transfers." \
  0.01 45 \
  "Token symbol and minimum transaction size to track (e.g. 100k USD+)." \
  "Whale activity report: recent large transactions, direction, potential impact."

# ═══════════════════════════════════════════════════
# BLOCO 4 — CONTENT & THREADS (validado: thread-quick comprado)
# ═══════════════════════════════════════════════════
echo ""
echo "── [4] Content & Threads (validado) ───────────"

c "cryptoThreadMicro" \
  "5-tweet punchy crypto thread on any token or narrative. Ready to post." \
  0.01 45 \
  "Topic, token or narrative for the thread." \
  "5-tweet thread with hook, body and CTA. Copy-paste ready."

c "cryptoThreadStandard" \
  "10-tweet researched crypto thread with data points and chart references." \
  0.05 90 \
  "Topic and any specific data or angles to include." \
  "10-tweet thread: hook, 7 content tweets with data, CTA. Engagement-optimised."

c "cryptoThreadViral" \
  "Write a viral-optimised crypto thread. Hook-first structure, contrarian angle, maximum engagement." \
  0.05 90 \
  "Topic and target audience (retail, degens, institutions)." \
  "Viral thread: contrarian hook, 8-10 tweets, controversy angle, CTA. Engagement score estimate."

c "marketCommentary" \
  "Write a short market commentary post. What happened today and what it means." \
  0.01 45 \
  "Optional: specific event or token to focus on." \
  "Market commentary: 200-300 word post, plain language, actionable insight."

c "alphaPost" \
  "Write a compelling alpha-sharing post. Present a trade thesis clearly and credibly." \
  0.05 60 \
  "Your trade thesis or signal to present." \
  "Alpha post: setup, thesis, entry/exit levels, risk note. Formatted for X/Twitter."

c "newsletterSection" \
  "Write one section of a crypto newsletter. Professional tone, data-backed." \
  0.05 90 \
  "Section topic, target length and newsletter audience profile." \
  "Newsletter section: headline, body paragraphs, key takeaway box."

c "cryptoNewsletterFull" \
  "Full crypto newsletter edition. Top stories, analysis, market data, outro." \
  0.10 180 \
  "Newsletter focus (e.g. DeFi, NFTs, general market) and subscriber level (beginner/advanced)." \
  "Complete newsletter: intro, 3 main stories with analysis, market data table, outro."

# ═══════════════════════════════════════════════════
# BLOCO 5 — TRADING INTELLIGENCE
# ═══════════════════════════════════════════════════
echo ""
echo "── [5] Trading Intelligence ────────────────────"

c "tradingSetupScanner" \
  "Scan for high-probability trading setups across the top 50 crypto assets." \
  0.05 90 \
  "Preferred setup type (breakout, reversal, momentum) and risk tolerance." \
  "Setup list: top 5 setups with entry zone, target, stop-loss and conviction score."

c "tokenTechnicalAnalysis" \
  "Technical analysis for a token. Key levels, trend, pattern, bias." \
  0.05 60 \
  "Token symbol and timeframe (1h, 4h, daily, weekly)." \
  "TA report: trend, key support/resistance, pattern identified, bullish/bearish bias."

c "riskRewardCalculator" \
  "Calculate risk/reward for a trade. Position sizing and max loss based on your parameters." \
  0.01 30 \
  "Entry price, target, stop-loss and portfolio size." \
  "Risk/reward report: R:R ratio, position size recommendation, max loss in USD and %."

c "marketRegimeDetector" \
  "Detect current market regime. Risk-on, risk-off, accumulation, distribution, or chop." \
  0.05 60 \
  "Optional: specific timeframe or sector to assess." \
  "Regime report: current regime label, confidence score, key indicators, implication for strategy."

c "correlationAnalysis" \
  "Analyse correlation between two assets. Are they moving together or diverging?" \
  0.05 90 \
  "Two asset symbols and lookback period (30d, 90d, 1y)." \
  "Correlation report: correlation coefficient, trend of correlation, trading implication."

c "liquidityMapQuick" \
  "Map liquidity levels for a token. Where are the clusters of buy/sell orders?" \
  0.05 60 \
  "Token symbol and exchange (Hyperliquid, Binance, Coinbase)." \
  "Liquidity map: key bid/ask clusters, thin zones, likely sweep targets."

c "fundingRateAlert" \
  "Check funding rates across major perpetual markets. Identify extremes and opportunities." \
  0.01 30 \
  "Optional: specific tokens or exchanges to check." \
  "Funding rate report: extreme rates flagged, contrarian signal strength, suggested plays."

# ═══════════════════════════════════════════════════
# BLOCO 6 — DeFi & ON-CHAIN
# ═══════════════════════════════════════════════════
echo ""
echo "── [6] DeFi & On-Chain ─────────────────────────"

c "yieldOpportunityFinder" \
  "Find the best yield opportunities right now. APY, risk level, protocol safety." \
  0.05 90 \
  "Minimum APY target, risk tolerance (low/medium/high) and preferred chains." \
  "Yield opportunities: top 5 options ranked by risk-adjusted APY with safety notes."

c "defiProtocolHealth" \
  "Check health of a DeFi protocol. TVL trend, revenue, liquidation risk, audit status." \
  0.05 90 \
  "Protocol name and chain." \
  "Health report: TVL trend, revenue metrics, liquidation levels, security status, verdict."

c "airdropScanner" \
  "Scan for upcoming and active airdrops worth pursuing. Effort-to-reward analysis." \
  0.05 90 \
  "Optional: chains or sectors to focus on, time availability per week." \
  "Airdrop list: top 5 opportunities, estimated value, effort required, deadline."

c "onChainFlowAnalysis" \
  "Analyse on-chain fund flows for a token. Where is money moving and why." \
  0.05 120 \
  "Token symbol and chain." \
  "Flow analysis: net inflows/outflows, exchange deposits/withdrawals, whale movements."

c "newTokenResearch" \
  "Research a newly launched token. Is it legit or a rug? Full due diligence." \
  0.05 90 \
  "Token name, contract address and chain." \
  "Due diligence report: team, tokenomics, contract check, red flags, risk rating 0-10."

c "gasOptimiser" \
  "Best time and strategy to execute a DeFi transaction. Gas optimisation report." \
  0.01 30 \
  "Transaction type and chain (Ethereum, Base, Arbitrum, etc)." \
  "Gas report: current gas cost, optimal timing, estimated savings, recommended approach."

# ═══════════════════════════════════════════════════
# BLOCO 7 — WEB RESEARCH & DATA
# ═══════════════════════════════════════════════════
echo ""
echo "── [7] Web Research & Data ─────────────────────"

c "webResearchQuick" \
  "Fast web research on any topic. Key facts and sources in minutes." \
  0.01 60 \
  "Topic or question to research." \
  "Research summary: key facts, answer, 3-5 source links."

c "webResearchStandard" \
  "Structured research report on any topic. Sources, analysis, conclusions." \
  0.05 120 \
  "Topic, scope and any specific angles to cover." \
  "Report: overview, key findings, data points, sources, actionable conclusions."

c "competitorIntelligence" \
  "Research a company or product. Pricing, positioning, weaknesses, strategy." \
  0.05 120 \
  "Company or product name and specific intel needed (pricing, features, strategy)." \
  "Intel report: overview, pricing, strengths/weaknesses, strategy, exploitable gaps."

c "dataFormatConverter" \
  "Convert between JSON, CSV, XML, YAML, TOML, Markdown. Any direction, any size." \
  0.01 30 \
  "Source data and target format." \
  "Converted data in the requested format, validated and clean."

c "pdfExtractor" \
  "Extract and structure content from a PDF. Tables, text, data into clean JSON." \
  0.05 60 \
  "PDF content or publicly accessible PDF URL." \
  "Structured JSON with all extracted content organised by section."

# ═══════════════════════════════════════════════════
# BLOCO 8 — CODE & AUTOMATION
# ═══════════════════════════════════════════════════
echo ""
echo "── [8] Code & Automation ───────────────────────"

c "codeGenerateQuick" \
  "Generate a function, script or snippet from a plain description." \
  0.01 60 \
  "What to build, language, and any constraints or dependencies." \
  "Working code with brief explanation of approach."

c "codeReviewSecurity" \
  "Review code for bugs, vulnerabilities and best-practice violations." \
  0.05 90 \
  "Code to review and language/framework context." \
  "Review report: issues found, severity (critical/high/medium/low), fixes."

c "sqlQueryWrite" \
  "Write or optimise a SQL query from a plain description." \
  0.01 45 \
  "What the query should do and database type (PostgreSQL, MySQL, SQLite)." \
  "SQL query with explanation and performance notes."

c "automationScript" \
  "Write an automation script for a repetitive task. Python, bash or JavaScript." \
  0.05 90 \
  "Task to automate, preferred language and environment (Mac, Linux, browser)." \
  "Working automation script with setup instructions and usage examples."

c "apiIntegrationHelper" \
  "Write the code to integrate with any public API. Auth, endpoints, error handling." \
  0.05 90 \
  "API name or documentation URL and what you want to do with it." \
  "Integration code: auth setup, main endpoints, error handling, usage example."

echo ""
echo "================================================"
echo "  Verificando..."
echo "================================================"
sleep 4
COUNT=$(acp offering list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
echo "  Total offerings publicados: $COUNT"
echo ""
acp offering list 2>&1
