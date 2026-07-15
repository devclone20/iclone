#!/bin/bash
# iCLONE — Publish all 32 offerings with market-rate pricing
# Prices: 0.01 (quick) | 0.05 (standard) | 0.10 (deep/complex)
set -euo pipefail

echo "================================================"
echo "  iCLONE — Publishing offerings (CLONE agent)"
echo "================================================"

# Ensure CLONE is active
acp agent use --agent-id 019eae06-96cd-77d0-8f8b-a6abb71f0cd7 > /dev/null 2>&1

create() {
  local name="$1" desc="$2" price="$3" sla="$4" req="$5" del="$6"
  acp offering create \
    --name "$name" \
    --description "$desc" \
    --price-type fixed \
    --price-value "$price" \
    --sla-minutes "$sla" \
    --requirements "$req" \
    --deliverable "$del" \
    --no-required-funds \
    --no-hidden 2>&1 | grep -E "^(Offering created|Error|\+)" | head -1
  echo "  ✓ $name @ \$$price USDC"
}

echo ""
echo "── Web Research ──────────────────────────────"
create "webResearchQuick" \
  "Fast web research on any topic. Key facts and sources in minutes." \
  0.01 60 \
  "Topic or question to research." \
  "Summary with key findings and source links."

create "webResearchStandard" \
  "Structured research report with sources, summaries and key insights." \
  0.05 120 \
  "Topic, scope and any specific angles to cover." \
  "Structured report: overview, key findings, sources, conclusions."

create "webResearchDeep" \
  "Deep multi-source research with analysis, trends and actionable conclusions." \
  0.10 180 \
  "Topic, depth required and desired output format." \
  "Full research report: executive summary, analysis, trends, recommendations."

echo ""
echo "── Code ──────────────────────────────────────"
create "codeGenerateQuick" \
  "Generate a function, snippet or small script from a plain description." \
  0.01 60 \
  "Describe the function or script you need and the language." \
  "Working code with brief inline comments."

create "codeGenerateStandard" \
  "Generate a complete module, class or feature with tests and docs." \
  0.05 120 \
  "Feature description, language, framework and any constraints." \
  "Complete module with tests and usage documentation."

create "bugFixFromErrorTrace" \
  "Diagnose and fix a bug from an error trace or failing test." \
  0.05 60 \
  "Error trace or failing test output plus relevant code snippet." \
  "Root cause analysis and corrected code."

create "codeReviewAndSecurityScan" \
  "Review code for bugs, security issues and best-practice violations." \
  0.05 120 \
  "Code to review and language/framework context." \
  "Review report: issues found, severity, and suggested fixes."

create "testGenerator" \
  "Generate unit or integration tests for existing code." \
  0.01 60 \
  "Code to test and testing framework preference." \
  "Complete test suite with coverage for key scenarios."

create "sqlQueryOptimizer" \
  "Optimise a slow SQL query. Returns rewritten query with explanation." \
  0.01 60 \
  "SQL query to optimise and database type (PostgreSQL, MySQL, etc)." \
  "Optimised query with explanation of changes."

create "regexBuilderAndTester" \
  "Build and validate a regex pattern from a plain-English description." \
  0.01 60 \
  "Describe the pattern you need and provide test strings." \
  "Regex pattern with explanation and test results."

create "projectScaffoldGenerator" \
  "Generate a production-ready project scaffold with folder structure and config." \
  0.05 180 \
  "Project type, language, framework and any specific requirements." \
  "Complete project scaffold with folder structure, config files and README."

echo ""
echo "── Data ──────────────────────────────────────"
create "dataFormatConverter" \
  "Convert between JSON, CSV, XML, YAML, TOML, Markdown. Any direction." \
  0.01 60 \
  "Source data and target format." \
  "Converted data in the requested format."

create "csvCleanerAndNormalizer" \
  "Clean, deduplicate and normalise a CSV dataset." \
  0.01 60 \
  "CSV data and cleaning rules (dedup fields, normalisation preferences)." \
  "Cleaned CSV with a summary of changes made."

create "pdfToStructuredJson" \
  "Extract and structure content from a PDF into clean JSON." \
  0.05 60 \
  "PDF content or URL and desired JSON structure." \
  "Structured JSON extracted from the PDF."

create "documentationGenerator" \
  "Generate README, docstrings or API docs from code or description." \
  0.01 60 \
  "Code or description and documentation format (README, docstrings, OpenAPI)." \
  "Complete documentation in the requested format."

echo ""
echo "── Crypto Research ───────────────────────────"
create "cryptoResearchQuick" \
  "Quick token or protocol snapshot: price, volume, sentiment, key metrics." \
  0.05 60 \
  "Token symbol or protocol name." \
  "Snapshot report: price, volume, sentiment, key metrics and brief outlook."

create "cryptoResearchDeep" \
  "Deep research on a token or protocol. Fundamentals, risks, outlook." \
  0.10 240 \
  "Token or protocol name and research focus (tokenomics, team, tech, risk)." \
  "Full research report: fundamentals, competitive analysis, risks, verdict."

create "priceMonitor" \
  "Monitor a token price and alert when it crosses a threshold." \
  0.01 60 \
  "Token symbol, current price and alert threshold." \
  "Price status report with threshold comparison."

create "defiOpportunityScanner" \
  "Scan top DeFi protocols for yield opportunities above your threshold." \
  0.05 120 \
  "Minimum APY threshold and preferred chains/risk level." \
  "Ranked list of yield opportunities with risk-adjusted APY."

echo ""
echo "── Wallet ────────────────────────────────────"
create "walletAnalyzerQuick" \
  "Token holdings and USD values for any EVM wallet. Snapshot in seconds." \
  0.01 60 \
  "EVM wallet address and chain (Ethereum, Base, Polygon, etc)." \
  "Holdings snapshot with token amounts and USD values."

create "walletHealthCheck" \
  "Multi-chain wallet audit: holdings, risky approvals, dust, risk score 0-100." \
  0.05 120 \
  "Wallet address and chains to audit." \
  "Audit report: holdings, risky approvals flagged, dust attacks, overall risk score."

create "walletDeepAnalysis" \
  "Full wallet forensics: transaction history, PnL, behaviour patterns, risk report." \
  0.10 180 \
  "Wallet address, chain and time period for analysis." \
  "Forensics report: transaction history, PnL breakdown, behaviour analysis, risk assessment."

echo ""
echo "── Content ───────────────────────────────────"
create "cryptoThreadQuick" \
  "Write a punchy crypto Twitter/X thread on a topic or token." \
  0.01 60 \
  "Topic, token or narrative for the thread." \
  "Ready-to-post thread (5-8 tweets) with hooks and CTAs."

create "cryptoThreadStandard" \
  "Write a researched, data-backed crypto thread with chart references." \
  0.05 60 \
  "Topic and any data or charts to reference." \
  "Researched thread (8-12 tweets) with data points and source references."

create "blogPostGenerator" \
  "Write a full blog post on any topic. SEO-optimised, ready to publish." \
  0.05 120 \
  "Topic, target audience and approximate length." \
  "Full blog post with title, headings, body and SEO meta description."

create "newsletterDigest" \
  "Curate and summarise top news from a sector into a newsletter digest." \
  0.05 180 \
  "Sector or topic and time period to cover." \
  "Newsletter-ready digest: top stories, summaries and key takeaways."

echo ""
echo "── Training & Agents ─────────────────────────"
create "agentTrainingModule" \
  "Run a structured training module for an AI agent. Returns score and insights." \
  0.10 240 \
  "Agent name, training topic and current knowledge gaps." \
  "Training report with score, key learnings and improvement areas."

create "skillBuildQuick" \
  "Build and test a new skill module for an AI agent. Quick scope." \
  0.10 360 \
  "Skill description, expected inputs and outputs." \
  "Working skill module with tests and integration guide."

create "skillBuildStandard" \
  "Full skill build: spec, implementation, tests, integration. Production-ready." \
  0.10 720 \
  "Detailed skill spec with use cases, inputs, outputs and constraints." \
  "Production-ready skill: spec, implementation, full test suite, integration docs."

create "fullAgentTrainingSuite" \
  "Complete agent training suite: identity, context, skills, evaluation." \
  0.10 1440 \
  "Agent profile, training goals and performance targets." \
  "Full training report with scores across all modules and improvement roadmap."

create "multiAgentCoordination" \
  "Coordinate multiple agents on a complex task. Orchestration and synthesis." \
  0.10 360 \
  "Task description, available agents and desired outcome." \
  "Coordinated output with agent contributions, synthesis and final result."

echo ""
echo "── Platform ──────────────────────────────────"
create "clonePlatformOnboarding" \
  "AI-scored onboarding for CLONE Platform clients. Tier and plan suggestion." \
  0.05 60 \
  "Client name, email, use case and budget range." \
  "Onboarding report with AI score (0-100), recommended tier and plan."

echo ""
echo "================================================"
echo "  Verifying..."
echo "================================================"
sleep 3
acp offering list
