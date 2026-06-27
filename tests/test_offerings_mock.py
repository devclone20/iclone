"""
iCLONE — Mock-based tests for all 32 ACP offerings.

These tests mock the Claude API and external HTTP calls so the full routing
and logic can be verified without API credits or network access.

Run: python3 -m pytest tests/test_offerings_mock.py -v --tb=short
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
from dotenv import load_dotenv
load_dotenv(Path.home() / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env", override=False)

import pytest
from iclone.skills.acp_skill import ACPSkill
from iclone.skills.base_skill import SkillResult

# ---------------------------------------------------------------------------
# Mock responses — realistic JSON bodies that prove each skill returns
# the contract it promises on the ACP marketplace.
# ---------------------------------------------------------------------------

MOCK_RESPONSES = {
    # Engine 1
    "iclone-research-quick-v1": {
        "summary": "Base is an Ethereum Layer 2 blockchain built by Coinbase...",
        "sources": [{"title": "Base Docs", "url": "https://docs.base.org", "relevance_note": "official"}] * 5,
        "key_facts": ["Built by Coinbase", "OP Stack", "EVM compatible"],
        "confidence": 92,
    },
    "iclone-research-standard-v1": {
        "report": "Comprehensive report on Ethereum L2 solutions...",
        "sources": [{"title": f"Source {i}", "url": f"https://example{i}.com", "type": "article", "key_point": "point"} for i in range(10)],
        "findings": [{"category": "tech", "finding": "OP Stack dominates", "evidence": "TVL data", "confidence": 85}],
        "confidence": 88,
        "recommendations": ["Monitor adoption", "Track TVL"],
        "research_gaps": ["Long-term security analysis"],
    },
    "iclone-research-deep-v1": {
        "executive_summary": "Virtuals Protocol is a pioneering AI agent platform...",
        "key_insights": [{"insight": "AI agents growing 10x YoY", "evidence": "metrics", "confidence": 87, "impact": "high"}],
        "risk_factors": ["Regulatory uncertainty"],
        "opportunities": ["Early agent marketplace participation"],
        "action_items": ["Evaluate VIRTUAL token"],
        "overall_confidence": 84,
        "data_quality": "medium",
        "sources": [],
    },
    "iclone-pdf-extract-v1": {
        "extracted_data": {"title": "Sample Document", "sections": ["Introduction", "Methods"], "summary": "A research document"},
        "pages_processed": 5,
        "text_length": 12000,
        "source_url": "https://example.com/doc.pdf",
    },
    "iclone-csv-cleaner-v1": {
        "cleaned_csv": "name,age,email\nAlice,30,alice@test.com\nBob,25,bob@test.com",
        "original_rows": 5,
        "final_rows": 4,
        "rows_removed": 1,
        "rows_modified": 2,
        "issues_found": ["Removed 1 duplicate", "Stripped whitespace from 2 cells"],
        "columns": ["name", "age", "email"],
    },
    "iclone-price-monitor-v1": {
        "current_value": "$29.99",
        "currency": "USD",
        "item_name": "Product X",
        "in_stock": True,
        "confidence": 90,
        "url": "https://example.com/product",
        "timestamp": "2026-06-11T10:00:00Z",
        "previous_value": None,
        "change_pct": None,
    },
    # Engine 2
    "iclone-code-gen-quick-v1": {
        "code": "import re\ndef validate_email(email: str) -> bool:\n    pattern = r'^[\\w.-]+@[\\w.-]+\\.\\w+$'\n    return bool(re.match(pattern, email))",
        "language": "python",
        "function_name": "validate_email",
        "docstring": "Validates an email address using regex.",
        "example_usage": "validate_email('user@example.com')  # True",
        "dependencies": ["re"],
    },
    "iclone-code-gen-standard-v1": {
        "module_code": "# Rate limiter module\nclass TokenBucket:\n    pass",
        "test_code": "def test_rate_limiter(): pass",
        "readme": "# Rate Limiter\nA Python rate limiting module.",
        "dependencies": ["time"],
        "module_name": "rate_limiter",
        "exports": ["TokenBucket", "RateLimiter"],
    },
    "iclone-bug-fix-v1": {
        "fixed_code": "def divide(a, b):\n    if b == 0:\n        raise ValueError('Cannot divide by zero')\n    return a / b",
        "root_cause": "ZeroDivisionError: division by zero — no guard on b==0",
        "explanation": "Added explicit check for zero divisor before division",
        "prevention_tip": "Always validate divisors before division operations",
        "changes_made": [{"line_or_area": "line 2", "what_changed": "Added zero check", "why": "Prevent ZeroDivisionError"}],
    },
    "iclone-regex-builder-v1": {
        "pattern": r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$",
        "flags": "IGNORECASE",
        "explanation": "Matches standard email format",
        "test_cases": [{"input": "user@test.com", "should_match": True, "reason": "valid email"}],
        "matches": ["user@example.com", "test@test.org"],
        "non_matches": ["invalid-email", "notanemail"],
        "python_code": "import re\nresult = re.match(pattern, email)",
        "pattern_valid": True,
        "validated_matches": ["user@example.com"],
    },
    "iclone-data-format-converter-v1": {
        "converted_data": "name: iCLONE\nversion: '1.0'\ntype: AI Agent\n",
        "input_format": "JSON",
        "output_format": "YAML",
        "warnings": [],
    },
    "iclone-scaffold-v1": {
        "file_tree": "my-api/\n├── main.py\n├── requirements.txt\n└── .env.example",
        "files": {
            "main.py": "from fastapi import FastAPI\napp = FastAPI()",
            "requirements.txt": "fastapi\nuvicorn",
            ".env.example": "DATABASE_URL=postgresql://...",
            "README.md": "# my-api\nA FastAPI project.",
        },
        "setup_instructions": ["pip install -r requirements.txt", "uvicorn main:app --reload"],
        "env_example": "DATABASE_URL=postgresql://...",
        "dependencies": {"fastapi": "*", "uvicorn": "*"},
        "scripts": {"start": "uvicorn main:app --reload", "test": "pytest"},
    },
    "iclone-code-review-v1": {
        "issues": [
            {"id": "OWASP-A03", "title": "SQL Injection", "severity": "critical",
             "category": "security", "description": "String interpolation in SQL query",
             "line_hint": "line 3", "recommendation": "Use parameterized queries", "owasp_ref": "A03:2021"},
        ],
        "severity_counts": {"critical": 1, "high": 0, "medium": 0, "low": 0, "info": 1},
        "recommendations": ["Use parameterized queries immediately"],
        "score": 35,
        "security_posture": "critical",
        "summary": "Critical SQL injection vulnerability found",
    },
    "iclone-sql-optimizer-v1": {
        "optimized_query": "SELECT id, status, total FROM orders WHERE customer_id = 123 ORDER BY created_at DESC LIMIT 100",
        "changes": [{"change": "SELECT * → specific columns", "reason": "Reduce data transfer", "impact": "medium"}],
        "estimated_improvement": "30-50% faster with index",
        "indexes_suggested": [{"table": "orders", "columns": ["customer_id", "created_at"], "type": "BTREE", "rationale": "Covers WHERE + ORDER BY"}],
        "anti_patterns_found": ["SELECT *"],
        "query_complexity": "simple",
        "warnings": [],
    },
    "iclone-test-generator-v1": {
        "test_code": "import pytest\nfrom fibonacci import calculate_fibonacci\n\ndef test_empty():\n    assert calculate_fibonacci(0) == []\n\ndef test_single():\n    assert calculate_fibonacci(1) == [0]\n\ndef test_sequence():\n    assert calculate_fibonacci(5) == [0, 1, 1, 2, 3]",
        "cases_covered": [
            {"name": "test_empty", "type": "edge_case", "description": "n=0 returns empty"},
            {"name": "test_single", "type": "edge_case", "description": "n=1 returns [0]"},
            {"name": "test_sequence", "type": "happy_path", "description": "n=5 returns correct sequence"},
        ],
        "coverage_estimate": "~90% line coverage",
        "setup_instructions": "pytest tests/",
        "mocks_needed": [],
    },
    "iclone-docs-generator-v1": {
        "documentation": "# fibonacci\n\n## Overview\nFibonacci sequence generator.\n\n## Usage\n```python\ncalculate_fibonacci(10)\n```",
        "format": "markdown",
        "sections": ["Overview", "Usage", "API Reference"],
    },
    # Engine 3
    "iclone-wallet-quick-v1": {
        "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E",
        "chain": "ethereum",
        "eth_balance": 0.0,
        "eth_usd_value": 0.0,
        "eth_price_usd": 1676.92,
        "token_count": 0,
        "holdings": [{"asset": "ETH", "balance": 0.0, "usd_value": 0.0, "price_usd": 1676.92, "type": "native"}],
        "total_usd_estimate": 0.0,
        "timestamp": "2026-06-11T10:00:00Z",
        "data_source": "Etherscan + CoinGecko",
    },
    "iclone-wallet-health-v1": {
        "risk_score": 75,
        "risk_level": "low",
        "holdings_summary": "Clean wallet with minimal activity",
        "activity_pattern": "Sparse transaction history",
        "risky_approvals": [],
        "dust_detected": False,
        "recommendations": ["Enable hardware wallet", "Review active approvals quarterly"],
        "health_grade": "B",
        "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E",
        "eth_balance": 0.0,
        "eth_usd_value": 0.0,
    },
    "iclone-wallet-deep-v1": {
        "portfolio_summary": "Minimal ETH holdings, no active DeFi positions detected",
        "pnl_estimate": {"note": "Historical PnL requires transaction indexing", "direction": "insufficient data"},
        "defi_positions": [],
        "risk_matrix": {"liquidity_risk": 20, "smart_contract_risk": 10, "concentration_risk": 90, "overall": 40},
        "yield_opportunities": [{"protocol": "Aave", "strategy": "ETH lending", "estimated_apy": "2-4%"}],
        "tax_summary": {"note": "Limited tx history detected", "events_count": 0, "disclaimer": "Not financial/tax advice"},
        "recommendations": ["Diversify assets", "Consider yield strategies"],
        "chains_analyzed": ["ethereum"],
        "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E",
    },
    "iclone-defi-opportunity-v1": {
        "opportunities": [
            {"protocol": "Aave V3", "chain": "ethereum", "strategy": "USDC lending",
             "estimated_apy_range": "4-6%", "risk_level": "low", "min_deposit": "$100",
             "tvl_usd": 8_000_000_000, "risk_adjusted_score": 85, "how_to_enter": "Deposit USDC on app.aave.com"},
            {"protocol": "Curve Finance", "chain": "ethereum", "strategy": "Stablecoin LP",
             "estimated_apy_range": "3-8%", "risk_level": "low", "min_deposit": "$50",
             "tvl_usd": 3_000_000_000, "risk_adjusted_score": 80, "how_to_enter": "Add liquidity on curve.fi"},
        ],
        "market_context": "DeFi yields are compressed in current environment",
        "risk_warnings": ["Smart contract risk", "Impermanent loss for LPs"],
        "data_sources": ["DeFiLlama", "Claude Analysis"],
        "scan_timestamp": "2026-06-11T10:00:00Z",
    },
    "iclone-crypto-research-quick-v1": {
        "asset": "BTC",
        "price_usd": 67500,
        "metrics": {"market_cap_note": "~$1.3T market cap", "volume_note": "$25B daily volume", "momentum": "bullish"},
        "sentiment": "bullish",
        "summary": "Bitcoin is the original cryptocurrency and store of value...",
        "signal": "hold",
        "key_risks": ["Regulatory crackdown", "ETF outflows", "Mining difficulty"],
        "key_catalysts": ["Halving cycle", "ETF inflows", "Institutional adoption"],
    },
    "iclone-crypto-research-deep-v1": {
        "title": "Bitcoin: Comprehensive Research Report",
        "executive_summary": "Bitcoin remains the dominant cryptocurrency with unmatched security...",
        "overview": {"description": "Decentralized digital currency", "category": "Store of Value", "launch_date": "2009", "team": "Pseudonymous (Satoshi Nakamoto)", "key_links": {}},
        "tokenomics": {"supply_model": "Fixed 21M cap", "distribution": "Mined", "vesting": "N/A", "inflation_rate": "Decreasing (halving)", "utility": "Store of value, medium of exchange"},
        "market_metrics": {"price_note": "~$67K", "market_cap_tier": "Mega cap", "volume_patterns": "High", "correlations": "Low correlation to equities"},
        "on_chain_analysis": {"activity_description": "High network utilization", "growth_trend": "Upward", "whale_behavior_notes": "Accumulation phase"},
        "competitive_landscape": {"position": "Dominant #1", "competitors": ["Ethereum", "Gold"], "moat": "Network effect + brand", "differentiators": ["Security", "Decentralization", "Brand"]},
        "macro_context": "Benefits from dollar debasement and institutional adoption",
        "risk_assessment": {"regulatory_risk": 40, "technical_risk": 10, "market_risk": 55, "team_risk": 5, "overall_risk_level": "medium", "risk_factors": ["Regulatory uncertainty"]},
        "investment_thesis": {"bull_case": "Digital gold replacing physical gold", "bear_case": "Regulatory ban in major economies", "neutral_case": "Gradual institutional adoption"},
        "recommendation": {"signal": "accumulate", "conviction": "high", "time_horizon": "3-5 years", "rationale": "Halving cycle + ETF demand", "disclaimer": "Not financial advice"},
        "data_sources": ["CoinGecko", "Claude Analysis"],
        "research_date": "2026-06-11",
    },
    # Engine 4
    "iclone-thread-quick-v1": {
        "tweets": [
            {"number": 1, "content": "Base blockchain is quietly becoming the home of DeFi on Ethereum. Here's why it matters:", "char_count": 88},
            {"number": 2, "content": "Built by Coinbase on the OP Stack, Base processes 10M+ daily txs with sub-cent fees. The infrastructure is ready.", "char_count": 115},
            {"number": 3, "content": "If you're not paying attention to Base yet, you're late. The ecosystem is just getting started. Follow @base_network", "char_count": 117},
        ],
        "hashtags": ["#Base", "#DeFi", "#Ethereum", "#Web3"],
        "thread_hook": "Base blockchain is quietly becoming the home of DeFi on Ethereum.",
    },
    "iclone-thread-standard-v1": {
        "tweets": [
            {"number": i, "content": f"Tweet {i} about AI agents on blockchain.", "char_count": 45, "purpose": "body"}
            for i in range(1, 8)
        ],
        "hashtags": ["#AIAgents", "#Base", "#Virtuals", "#DeFi", "#Web3", "#AI", "#Crypto"],
        "engagement_tips": ["Post on Tuesday 9-11 AM EST", "Reply to top crypto accounts"],
        "best_time_to_post": "Tuesday 9-11 AM EST",
        "thread_hook": "AI agents on blockchain — the next wave is here.",
    },
    "iclone-blog-post-v1": {
        "title": "How AI Agents Are Transforming DeFi in 2025",
        "markdown_content": "# How AI Agents Are Transforming DeFi in 2025\n\n## Introduction\nAI agents are revolutionizing how we interact with DeFi protocols...\n\n## The Rise of Autonomous Finance\nWith protocols like Virtuals Protocol...\n\n## Key Developments\n1. **Automated yield optimization** — AI agents now manage billions in DeFi\n2. **Risk assessment** — Real-time portfolio risk monitoring\n3. **Cross-chain coordination** — Agents bridge multiple protocols seamlessly\n\n## What This Means for Investors\nThe integration of AI into DeFi creates new opportunities...\n\n## Conclusion\nAI agents represent the next frontier of decentralized finance.",
        "meta_description": "Explore how AI agents are revolutionizing DeFi in 2025 with automated yield optimization and cross-chain coordination.",
        "seo_score": 82,
        "word_count": 520,
        "reading_time_minutes": 3,
        "keywords_used": ["AI agents", "DeFi", "Virtuals Protocol"],
    },
    "iclone-newsletter-v1": {
        "subject_line": "This Week in Crypto & AI Agents — June 11, 2026",
        "items": [
            {"number": i, "headline": f"Headline {i}", "summary": "Summary of the story in 2-3 sentences.", "category": "crypto", "why_it_matters": "Important because..."}
            for i in range(1, 6)
        ],
        "intro": "Welcome to this week's digest of the most important developments in crypto and AI agents.",
        "outro": "Thanks for reading. Follow iCLONE for daily insights.",
        "markdown_ready": "# This Week in Crypto & AI Agents\n\n...",
        "themes_covered": ["AI Agents", "DeFi", "Layer 2"],
    },
    # Engine 5
    "iclone-agent-training-module-v1": {
        "module_id": "tm_defi_protocols_v1",
        "domain": "defi_protocols",
        "title": "DeFi Protocols: Comprehensive Knowledge Module",
        "overview": "After this module, the agent will understand AMMs, lending protocols, yield aggregators, and cross-chain bridges.",
        "knowledge_sections": [
            {"title": "AMMs", "content": "Automated Market Makers use x*y=k...", "key_concepts": ["liquidity pools", "impermanent loss"], "practical_examples": ["Uniswap V3"]},
        ],
        "knowledge_tests": [
            {"question": "What formula does Uniswap V2 use?", "expected_answer_keywords": ["x*y=k", "constant product"], "difficulty": "medium"},
        ],
        "integration_notes": "Add soul_md_addition to the agent's soul.md file",
        "soul_md_addition": "## DeFi Protocol Knowledge\nExpert in AMMs, lending protocols...",
        "estimated_impact": "Enables autonomous DeFi strategy execution",
    },
    "iclone-agent-training-full-v1": {
        "agent_id": "test-agent-001",
        "agent_name": "TestClone",
        "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E",
        "modules_count": 15,
        "modules": [
            {"module_number": i, "module_id": f"tm_module_{i}", "title": f"Module {i}", "overview": "Overview...", "key_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"], "soul_md_snippet": f"## Module {i}"}
            for i in range(1, 16)
        ],
        "deployment_report": "15 training modules generated for TestClone",
        "next_steps": ["Review modules", "Install soul_md_snippets", "Run tests", "Deploy"],
    },
    "iclone-build-skill-quick-v1": {
        "skill_id": "temperature_converter_v1",
        "skill_name": "Temperature Converter",
        "python_code": "from iclone.skills.base_skill import SkillResult\n\nclass TemperatureConverterSkill:\n    def convert(self, value: float, from_unit: str, to_unit: str) -> SkillResult:\n        conversions = {'C_to_F': lambda x: x*9/5+32}\n        key = f'{from_unit}_to_{to_unit}'\n        if key not in conversions:\n            return SkillResult(success=False, output='', error=f'Unsupported: {key}')\n        result = conversions[key](value)\n        return SkillResult(success=True, output=str(result), data={'result': result})",
        "test_code": "def test_celsius_to_fahrenheit():\n    skill = TemperatureConverterSkill()\n    result = skill.convert(100, 'C', 'F')\n    assert result.success\n    assert result.data['result'] == 212.0",
        "plaza_listing": {"name": "Temperature Converter", "description": "Convert temperatures", "price_range": "$0.05-0.10", "category": "utility", "use_cases": ["scientific", "cooking"]},
        "dependencies": [],
    },
    "iclone-build-skill-standard-v1": {
        "skill_id": "web_scraper_skill_v1",
        "skill_name": "Web Scraper",
        "skill_description": "Production web scraping skill with retry logic and structured output",
        "python_code": "# Full production skill with multiple methods...\n" + "# " * 100 + "\nclass WebScraperSkill:\n    def scrape(self, url): pass",
        "test_code": "def test_scraper(): pass",
        "documentation": "# Web Scraper Skill\nProduction-quality web scraping for CLONE agents.",
        "plaza_listing": {"name": "Web Scraper", "description": "Production web scraping", "price_usdc": 5.0, "category": "data_extraction", "use_cases": ["price monitoring"], "requirements": ["url"]},
        "dependencies": ["requests", "beautifulsoup4"],
        "changelog": "v1.0.0: Initial release",
    },
    "iclone-coordinate-agents-v1": {
        "coordination_id": "coord_001",
        "task_decomposition": [
            {"agent_id": "research-agent-1", "sub_task": "Research Base blockchain", "inputs_needed": ["query"], "outputs_produced": ["research_report"], "order": 1},
            {"agent_id": "writer-agent-1", "sub_task": "Write summary from research", "inputs_needed": ["research_report"], "outputs_produced": ["summary"], "order": 2},
        ],
        "execution_dag": "research-agent-1 → writer-agent-1",
        "estimated_duration": "5-10 minutes",
        "quality_gates": [{"after_step": 1, "check": "Research completeness", "pass_criteria": "Sources cited"}],
        "execution_log": ["Step 1: research-agent-1 completed", "Step 2: writer-agent-1 completed"],
        "final_result": "Structured research report on Base blockchain completed",
        "agents_used": ["research-agent-1", "writer-agent-1"],
        "status": "completed",
        "success": True,
    },
    "iclone-onboarding-v1": {
        "user_id": "user-test-12345",
        "welcome_message": "Welcome to CLONE! I'm iCLONE, your platform guide.",
        "platform_access": {"acp_status": "registered", "hub_status": "ready", "marketplace_status": "active"},
        "wallet_status": "ready",
        "recommended_skills": [
            {"skill_id": "crypto_skill_v1", "name": "Crypto Intelligence", "reason": "For trading insights", "price_usdc": 5.0},
        ],
        "recommended_agents": [{"category": "iCLONE", "use_case": "Personal AI assistant"}],
        "quick_start_steps": ["Connect wallet", "Browse Plaza", "Purchase your first skill"],
        "platform_overview": {
            "agents": "AI agents for every task",
            "skills": "Modular capabilities for agents",
            "hub": "Central control panel",
            "acp": "Agent Commerce Protocol for earning USDC",
            "plaza": "Skill marketplace",
        },
        "support_resources": [{"title": "CLONE Docs", "url": "https://docs.clone.ai"}],
        "onboarding_complete": True,
    },
}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def acp():
    return ACPSkill()


def mock_claude_json(prompt, system="", model="claude-haiku-4-5", max_tokens=2048):
    """Return a mock response that matches the first offering_id found in the call stack."""
    import traceback
    stack = traceback.extract_stack()
    for frame in reversed(stack):
        code = frame.name
        # Try to find which test is running
        for offering_id, response in MOCK_RESPONSES.items():
            if offering_id in str(frame):
                return response
    # Return a generic valid response
    return {"result": "mock", "status": "ok", "data": {}}


def make_mock_claude(offering_id: str):
    """Create a mock _claude_json that returns the mock response for a specific offering."""
    def _mock(*args, **kwargs):
        return MOCK_RESPONSES.get(offering_id, {"result": "mock"})
    return _mock


# ---------------------------------------------------------------------------
# Tests — one per offering, each patches Claude at the module level
# ---------------------------------------------------------------------------

ENGINE_MODULE = "iclone.skills.execution_engine"


def run_offering_test(acp, offering_id: str, requirements: dict, checks: dict | None = None):
    """
    Generic test runner: patches Claude, runs the offering, asserts success.
    checks: dict of {key: expected_value} to verify in result.data
    """
    mock_response = MOCK_RESPONSES[offering_id]

    with patch(f"{ENGINE_MODULE}._claude_json", return_value=mock_response):
        with patch(f"{ENGINE_MODULE}._claude", return_value=str(mock_response)):
            result = acp.execute_offering(offering_id, requirements)

    assert result.success, f"[{offering_id}] FAILED: {result.error}"
    assert result.output, f"[{offering_id}] empty output"

    if checks and result.data:
        for key, expected in checks.items():
            assert key in result.data, f"[{offering_id}] missing key '{key}' in data"
            if expected is not None:
                assert result.data[key] == expected, f"[{offering_id}] {key}: expected {expected}, got {result.data[key]}"

    return result


# ENGINE 1 — Research & Data

class TestEngine1Research:

    def test_01_research_quick(self, acp):
        result = run_offering_test(acp, "iclone-research-quick-v1",
            {"query": "What is Base blockchain?"},
            {"summary": MOCK_RESPONSES["iclone-research-quick-v1"]["summary"]})
        assert len(result.data["sources"]) >= 3

    def test_02_research_standard(self, acp):
        result = run_offering_test(acp, "iclone-research-standard-v1",
            {"query": "Ethereum L2 comparison", "depth": "standard"},
            {"confidence": 88})
        assert "findings" in result.data

    def test_03_research_deep(self, acp):
        result = run_offering_test(acp, "iclone-research-deep-v1",
            {"query": "Virtuals Protocol", "context": "crypto AI agents"})
        assert "executive_summary" in result.data

    def test_04_pdf_extract(self, acp):
        with patch(f"{ENGINE_MODULE}.requests.get") as mock_get:
            import io
            mock_resp = MagicMock()
            mock_resp.content = b"%PDF-1.4 fake pdf content"
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            with patch("pdfplumber.open") as mock_pdf:
                mock_page = MagicMock()
                mock_page.extract_text.return_value = "This is a test document with title and sections."
                mock_pdf.return_value.__enter__.return_value.pages = [mock_page]

                with patch(f"{ENGINE_MODULE}._claude_json", return_value=MOCK_RESPONSES["iclone-pdf-extract-v1"]["extracted_data"]):
                    result = acp.execute_offering("iclone-pdf-extract-v1", {
                        "pdf_url": "https://example.com/doc.pdf",
                        "extraction_schema": {"title": "string"}
                    })
        assert result.success, f"PDF extract failed: {result.error}"
        assert "extracted_data" in result.data

    def test_05_csv_cleaner(self, acp):
        # This test does NOT mock Claude — it uses pure pandas logic
        csv_data = "name,age,email\nAlice,30,alice@test.com\nBob,25,bob@test.com\nAlice,30,alice@test.com\n Dave,35, dave@test.com \n"
        result = acp.execute_offering("iclone-csv-cleaner-v1", {"csv_data": csv_data, "cleaning_rules": {}})
        assert result.success, f"CSV cleaner failed: {result.error}"
        assert result.data["rows_removed"] >= 1
        assert result.data["original_rows"] > result.data["final_rows"]

    def test_06_price_monitor(self, acp):
        with patch(f"{ENGINE_MODULE}.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = "<html><body><span class='price'>$29.99</span></body></html>"
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp
            with patch(f"{ENGINE_MODULE}._claude_json", return_value=MOCK_RESPONSES["iclone-price-monitor-v1"]):
                result = acp.execute_offering("iclone-price-monitor-v1", {
                    "url": "https://example.com/product",
                    "selector_or_description": "product price"
                })
        assert result.success, f"Price monitor failed: {result.error}"
        assert "current_value" in result.data


# ENGINE 2 — Code & Dev

class TestEngine2Code:

    def test_07_code_gen_quick(self, acp):
        result = run_offering_test(acp, "iclone-code-gen-quick-v1",
            {"description": "validate email with regex", "language": "python"},
            {"language": "python"})
        assert "def " in result.data["code"] or "class " in result.data["code"]

    def test_08_code_gen_standard(self, acp):
        result = run_offering_test(acp, "iclone-code-gen-standard-v1",
            {"spec": "Rate limiter module", "language": "python", "test_framework": "pytest"})
        assert "module_code" in result.data
        assert "test_code" in result.data

    def test_09_bug_fix(self, acp):
        result = run_offering_test(acp, "iclone-bug-fix-v1",
            {"error_trace": "ZeroDivisionError", "code_snippet": "return a/b", "language": "python"})
        assert "fixed_code" in result.data
        assert "zero" in result.data["root_cause"].lower() or "ZeroDivision" in result.data["root_cause"]

    def test_10_regex_builder(self, acp):
        # Regex validation runs without Claude — only the generation needs mocking
        with patch(f"{ENGINE_MODULE}._claude_json", return_value={
            "pattern": r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$",
            "flags": "",
            "explanation": "Matches emails",
            "test_cases": [],
            "matches": [],
            "non_matches": [],
            "python_code": "re.match(pattern, s)",
        }):
            result = acp.execute_offering("iclone-regex-builder-v1", {
                "description": "match emails",
                "sample_inputs[]": ["user@test.com", "notanemail"]
            })
        assert result.success
        assert result.data.get("pattern_valid") is True

    def test_11_data_format_converter_json_yaml(self, acp):
        # Pure conversion — no Claude needed for JSON→YAML
        result = acp.execute_offering("iclone-data-format-converter-v1", {
            "input_data": '{"name": "iCLONE", "version": "1.0"}',
            "input_format": "JSON",
            "output_format": "YAML"
        })
        assert result.success, f"Converter failed: {result.error}"
        assert "name: iCLONE" in result.data["converted_data"]

    def test_12_data_format_converter_csv_json(self, acp):
        result = acp.execute_offering("iclone-data-format-converter-v1", {
            "input_data": "name,age\nAlice,30\nBob,25",
            "input_format": "CSV",
            "output_format": "JSON"
        })
        assert result.success, f"Converter failed: {result.error}"
        parsed = json.loads(result.data["converted_data"])
        assert isinstance(parsed, list) and len(parsed) == 2

    def test_13_scaffold_generator(self, acp):
        result = run_offering_test(acp, "iclone-scaffold-v1",
            {"stack": "FastAPI", "project_name": "my-api", "features[]": ["auth"]})
        assert "file_tree" in result.data
        assert len(result.data.get("files", {})) >= 3

    def test_14_code_review(self, acp):
        result = run_offering_test(acp, "iclone-code-review-v1",
            {"code": "SELECT * FROM users WHERE name = '" + "' + username", "language": "python"})
        assert "issues" in result.data
        severities = [i.get("severity") for i in result.data["issues"]]
        assert "critical" in severities

    def test_15_sql_optimizer(self, acp):
        result = run_offering_test(acp, "iclone-sql-optimizer-v1",
            {"sql_query": "SELECT * FROM orders WHERE customer_id = 123", "schema_context": ""})
        assert "optimized_query" in result.data
        assert "indexes_suggested" in result.data

    def test_16_test_generator(self, acp):
        result = run_offering_test(acp, "iclone-test-generator-v1",
            {"code": "def fibonacci(n): pass", "language": "python", "test_framework": "pytest"})
        assert "def test_" in result.data["test_code"]

    def test_17_docs_generator_readme(self, acp):
        result = run_offering_test(acp, "iclone-docs-generator-v1",
            {"code": "def fibonacci(n): pass", "doc_type": "readme"})
        assert "#" in result.data["documentation"]

    def test_18_docs_generator_docstrings(self, acp):
        # Override mock for docstrings variant
        docstring_mock = {
            "documentation": 'def fibonacci(n):\n    """Calculate Fibonacci sequence."""\n    pass',
            "format": "code_with_docstrings",
            "sections": ["fibonacci"]
        }
        with patch(f"{ENGINE_MODULE}._claude_json", return_value=docstring_mock):
            result = acp.execute_offering("iclone-docs-generator-v1",
                {"code": "def fibonacci(n): pass", "doc_type": "docstrings"})
        assert result.success
        assert '"""' in result.data["documentation"]


# ENGINE 3 — Wallet & Crypto

class TestEngine3WalletCrypto:

    def test_19_wallet_quick(self, acp):
        # Uses real Etherscan V2 + CoinGecko — no mock needed for this tier
        result = acp.execute_offering("iclone-wallet-quick-v1", {
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E",
            "chain": "ethereum"
        })
        assert result.success, f"wallet_quick failed: {result.error}"
        assert "eth_balance" in result.data
        assert isinstance(result.data["eth_balance"], float)

    def test_20_wallet_health(self, acp):
        with patch(f"{ENGINE_MODULE}._claude_json", return_value=MOCK_RESPONSES["iclone-wallet-health-v1"]):
            result = acp.execute_offering("iclone-wallet-health-v1", {
                "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E"
            })
        assert result.success, f"wallet_health failed: {result.error}"
        assert 0 <= result.data["risk_score"] <= 100
        assert "recommendations" in result.data

    def test_21_wallet_deep(self, acp):
        with patch(f"{ENGINE_MODULE}._claude_json", return_value=MOCK_RESPONSES["iclone-wallet-deep-v1"]):
            result = acp.execute_offering("iclone-wallet-deep-v1", {
                "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E",
                "chains[]": ["ethereum"]
            })
        assert result.success, f"wallet_deep failed: {result.error}"
        assert "portfolio_summary" in result.data

    def test_22_defi_opportunity_scanner(self, acp):
        mock_protocols = [
            {"name": "Aave", "tvl": 8_000_000_000, "chains": ["ethereum"], "category": "Lending"}
        ] * 5
        with patch(f"{ENGINE_MODULE}.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_protocols
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp
            with patch(f"{ENGINE_MODULE}._claude_json", return_value=MOCK_RESPONSES["iclone-defi-opportunity-v1"]):
                result = acp.execute_offering("iclone-defi-opportunity-v1", {
                    "min_apy": 5.0,
                    "chains[]": ["ethereum"],
                    "risk_tolerance": "medium"
                })
        assert result.success, f"defi_scanner failed: {result.error}"
        assert "opportunities" in result.data

    def test_23_crypto_research_quick(self, acp):
        with patch(f"{ENGINE_MODULE}._claude_json", return_value=MOCK_RESPONSES["iclone-crypto-research-quick-v1"]):
            with patch(f"{ENGINE_MODULE}.requests.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.json.return_value = {
                    "market_data": {
                        "current_price": {"usd": 67500},
                        "price_change_percentage_24h": 2.5,
                        "price_change_percentage_7d": 5.0,
                        "market_cap": {"usd": 1_300_000_000_000},
                        "total_volume": {"usd": 25_000_000_000},
                    },
                    "sentiment_votes_up_percentage": 75,
                    "description": {"en": "Bitcoin is the first cryptocurrency."},
                }
                mock_resp.raise_for_status = MagicMock()
                mock_get.return_value = mock_resp
                result = acp.execute_offering("iclone-crypto-research-quick-v1", {"asset_symbol": "BTC"})
        assert result.success, f"crypto_quick failed: {result.error}"
        assert "sentiment" in result.data

    def test_24_crypto_research_deep(self, acp):
        result = run_offering_test(acp, "iclone-crypto-research-deep-v1",
            {"asset_or_protocol": "Bitcoin", "research_depth": "comprehensive"})
        assert "executive_summary" in result.data
        assert "recommendation" in result.data


# ENGINE 4 — Content & Social

class TestEngine4Content:

    def test_25_thread_quick(self, acp):
        result = run_offering_test(acp, "iclone-thread-quick-v1",
            {"topic": "Base blockchain DeFi", "tone": "bullish"})
        assert len(result.data["tweets"]) == 3
        for tweet in result.data["tweets"]:
            assert len(tweet.get("content", "")) <= 280

    def test_26_thread_standard(self, acp):
        result = run_offering_test(acp, "iclone-thread-standard-v1",
            {"topic": "AI agents on blockchain", "tone": "analytical", "data_points[]": ["$2B market cap"]})
        assert len(result.data["tweets"]) == 7

    def test_27_blog_post(self, acp):
        result = run_offering_test(acp, "iclone-blog-post-v1",
            {"topic": "AI agents transforming DeFi", "target_audience": "crypto enthusiasts", "keywords[]": ["AI", "DeFi"]})
        assert "title" in result.data
        assert "markdown_content" in result.data
        word_count = len(result.data["markdown_content"].split())
        assert word_count >= 100, f"Content too short: {word_count} words"

    def test_28_newsletter_digest(self, acp):
        result = run_offering_test(acp, "iclone-newsletter-v1",
            {"category": "crypto and AI", "num_items": 5, "audience": "DeFi users"})
        assert "items" in result.data
        assert len(result.data["items"]) >= 3
        assert "markdown_ready" in result.data


# ENGINE 5 — Agent Platform

class TestEngine5Platform:

    def test_29_agent_training_module(self, acp):
        result = run_offering_test(acp, "iclone-agent-training-module-v1",
            {"agent_id": "test-agent-001", "domain": "defi_protocols"})
        assert "knowledge_sections" in result.data
        assert "soul_md_addition" in result.data

    def test_30_agent_training_full(self, acp):
        # This calls Claude 15 times — mock each call
        with patch(f"{ENGINE_MODULE}._claude_json") as mock_cj:
            mock_cj.return_value = {
                "module_id": "tm_test", "title": "Test Module",
                "overview": "Test overview", "key_skills": ["s1", "s2", "s3", "s4", "s5"],
                "soul_md_snippet": "## Test"
            }
            result = acp.execute_offering("iclone-agent-training-full-v1", {
                "agent_id": "test-agent-001",
                "agent_name": "TestClone",
                "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E"
            })
        assert result.success, f"training_full failed: {result.error}"
        assert result.data["modules_count"] == 15
        assert len(result.data["modules"]) == 15

    def test_31_skill_build_quick(self, acp):
        result = run_offering_test(acp, "iclone-build-skill-quick-v1",
            {"skill_description": "temperature converter", "input_schema": {}, "output_schema": {}})
        assert "python_code" in result.data
        assert "def " in result.data["python_code"] or "class " in result.data["python_code"]

    def test_32_multi_agent_coordination(self, acp):
        result = run_offering_test(acp, "iclone-coordinate-agents-v1",
            {"task_description": "research task", "agent_ids[]": ["agent-1", "agent-2"], "expected_output": "report"})
        assert "task_decomposition" in result.data or "execution_dag" in result.data

    def test_33_platform_onboarding(self, acp):
        result = run_offering_test(acp, "iclone-onboarding-v1",
            {"agent_id_or_user_id": "user-test-12345"})
        assert result.data["onboarding_complete"] is True
        assert "welcome_message" in result.data


# ACP Lifecycle

class TestACPLifecycle:

    def test_list_offerings_count(self, acp):
        offerings = acp.list_offerings()
        assert len(offerings) == 32, f"Expected 32, got {len(offerings)}"

    def test_full_lifecycle_with_mock(self, acp):
        """Full ACP lifecycle: accept → execute (mocked) → deliver → complete."""
        with patch(f"{ENGINE_MODULE}._claude_json", return_value=MOCK_RESPONSES["iclone-research-quick-v1"]):
            accept = acp.accept_job(
                job_id="mock-job-001",
                offering_id="iclone-research-quick-v1",
                client_agent_id="client-abc",
                requirements={"query": "Base blockchain"},
            )
            assert accept.success

            execute = acp.execute_offering("iclone-research-quick-v1", {"query": "Base blockchain"})
            assert execute.success

            deliver = acp.submit_deliverable(
                job_id="mock-job-001",
                deliverable_content=json.dumps(execute.data),
                deliverable_url="https://ipfs.io/ipfs/placeholder",
            )
            assert deliver.success

            complete = acp.complete_job("mock-job-001")
            assert complete.success
            assert complete.data["usdc_earned"] == 0.25

    def test_execute_unknown_offering(self, acp):
        result = acp.execute_offering("nonexistent-v999", {})
        assert not result.success
        assert "Unknown offering" in result.error

    def test_missing_required_fields_validation(self, acp):
        result = acp.execute_offering("iclone-research-quick-v1", {})
        assert not result.success
        assert "query" in result.error
