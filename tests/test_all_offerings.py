"""
iCLONE — Real execution tests for all 32 ACP offerings.
Run: python3 -m pytest tests/test_all_offerings.py -v --tb=short

Tests make real API calls (Claude, Etherscan, CoinGecko, DeFiLlama).
Requires ANTHROPIC_API_KEY in .env.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
from dotenv import load_dotenv
load_dotenv(Path.home() / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env", override=False)

import pytest
from iclone.skills.acp_skill import ACPSkill
from iclone.skills.execution_engine import (
    ResearchEngine, CodeEngine, WalletCryptoEngine, ContentEngine, PlatformEngine,
    ExecutionEngine,
)
from iclone.skills.base_skill import SkillResult

# ── Test fixtures ────────────────────────────────────────────────────────────

TEST_WALLET = "0x742d35Cc6634C0532925a3b8D4C9E62B25F7DA1E"

SAMPLE_CSV = """name,age,email,city
Alice,30,alice@test.com,New York
Bob,25,bob@test.com,London
Alice,30,alice@test.com,New York
Charlie,,charlie@test.com,Paris
Dave,35, dave@test.com ,Berlin
"""

BUGGY_CODE = """def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)
"""

BUGGY_TRACE = """Traceback (most recent call last):
  File "test.py", line 4, in <module>
    result = divide(10, 0)
  File "test.py", line 2, in divide
    return a / b
ZeroDivisionError: division by zero
"""

SAMPLE_PYTHON_CODE = """def calculate_fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence
"""

# ── Helpers ──────────────────────────────────────────────────────────────────

def assert_skill_result(result: SkillResult, test_name: str) -> None:
    """Assert that a SkillResult succeeded and has data."""
    assert isinstance(result, SkillResult), f"{test_name}: expected SkillResult"
    if not result.success:
        pytest.fail(f"{test_name}: FAILED — {result.error}")
    assert result.output, f"{test_name}: empty output"
    print(f"\n  [{test_name}] OK: {result.output[:80]}")
    if result.data:
        # Print first 200 chars of data summary
        data_preview = json.dumps(result.data, default=str)[:200]
        print(f"  Data preview: {data_preview}...")


@pytest.fixture(scope="module")
def acp():
    return ACPSkill()


@pytest.fixture(scope="module")
def engine():
    return ExecutionEngine()


# ── ENGINE 1: Research & Data ────────────────────────────────────────────────

class TestResearchEngine:

    def test_web_research_quick(self, acp):
        result = acp.execute_offering(
            "iclone-research-quick-v1",
            {"query": "What is Base blockchain?"}
        )
        assert_skill_result(result, "web_research_quick")
        data = result.data
        assert "summary" in data
        assert "sources" in data
        assert "key_facts" in data
        assert len(data["sources"]) >= 3

    def test_web_research_standard(self, acp):
        result = acp.execute_offering(
            "iclone-research-standard-v1",
            {"query": "Ethereum Layer 2 scaling solutions comparison", "depth": "standard"}
        )
        assert_skill_result(result, "web_research_standard")
        data = result.data
        assert "report" in data
        assert "findings" in data

    def test_web_research_deep(self, acp):
        result = acp.execute_offering(
            "iclone-research-deep-v1",
            {"query": "Virtuals Protocol AI agent ecosystem", "context": "crypto AI agents"}
        )
        assert_skill_result(result, "web_research_deep")
        data = result.data
        assert "executive_summary" in data
        assert "key_insights" in data

    def test_pdf_extract(self, acp):
        # Use a known public PDF
        result = acp.execute_offering(
            "iclone-pdf-extract-v1",
            {
                "pdf_url": "https://www.w3.org/WAI/WCAG21/wcag21.pdf",
                "extraction_schema": {"title": "string", "sections": ["array"], "summary": "string"}
            }
        )
        # PDF fetch may fail on network — that's acceptable, check for graceful handling
        assert isinstance(result, SkillResult)
        if result.success:
            assert "extracted_data" in result.data
            print(f"\n  [pdf_extract] OK: {result.output[:80]}")
        else:
            print(f"\n  [pdf_extract] SKIP (network): {result.error}")
            pytest.skip(f"PDF fetch failed (expected in restricted network): {result.error}")

    def test_csv_cleaner(self, acp):
        result = acp.execute_offering(
            "iclone-csv-cleaner-v1",
            {"csv_data": SAMPLE_CSV, "cleaning_rules": {"remove_duplicates": True}}
        )
        assert_skill_result(result, "csv_cleaner")
        data = result.data
        assert data["rows_removed"] >= 1  # at least the Alice duplicate
        assert "cleaned_csv" in data
        assert data["original_rows"] > data["final_rows"]

    def test_price_monitor(self, acp):
        result = acp.execute_offering(
            "iclone-price-monitor-v1",
            {
                "url": "https://www.amazon.com/dp/B0CHX1W1XY",
                "selector_or_description": "product price"
            }
        )
        # Amazon may block — graceful handling
        assert isinstance(result, SkillResult)
        if result.success:
            assert "url" in result.data
            print(f"\n  [price_monitor] OK: {result.output[:80]}")
        else:
            print(f"\n  [price_monitor] SKIP (blocked): {result.error}")
            pytest.skip(f"Site blocked scraping (expected): {result.error}")


# ── ENGINE 2: Code & Dev ─────────────────────────────────────────────────────

class TestCodeEngine:

    def test_code_gen_quick(self, acp):
        result = acp.execute_offering(
            "iclone-code-gen-quick-v1",
            {
                "description": "A function that validates an email address using regex",
                "language": "python"
            }
        )
        assert_skill_result(result, "code_gen_quick")
        data = result.data
        assert "code" in data
        assert "python" in data.get("language", "").lower()
        assert len(data["code"]) > 50

    def test_code_gen_standard(self, acp):
        result = acp.execute_offering(
            "iclone-code-gen-standard-v1",
            {
                "spec": "A Python module for rate limiting HTTP requests. Supports token bucket algorithm.",
                "language": "python",
                "test_framework": "pytest"
            }
        )
        assert_skill_result(result, "code_gen_standard")
        data = result.data
        assert "module_code" in data
        assert "test_code" in data

    def test_bug_fix(self, acp):
        result = acp.execute_offering(
            "iclone-bug-fix-v1",
            {
                "error_trace": BUGGY_TRACE,
                "code_snippet": BUGGY_CODE,
                "language": "python"
            }
        )
        assert_skill_result(result, "bug_fix")
        data = result.data
        assert "fixed_code" in data
        assert "root_cause" in data
        assert "ZeroDivision" in data.get("root_cause", "") or "zero" in data.get("root_cause", "").lower()

    def test_regex_builder(self, acp):
        result = acp.execute_offering(
            "iclone-regex-builder-v1",
            {
                "description": "Match valid email addresses",
                "sample_inputs[]": ["user@example.com", "invalid-email", "test@test.org", "notanemail"]
            }
        )
        assert_skill_result(result, "regex_builder")
        data = result.data
        assert "pattern" in data
        assert data.get("pattern_valid") is True

    def test_data_format_converter_json_to_yaml(self, acp):
        result = acp.execute_offering(
            "iclone-data-format-converter-v1",
            {
                "input_data": '{"name": "iCLONE", "version": "1.0", "type": "AI Agent"}',
                "input_format": "JSON",
                "output_format": "YAML"
            }
        )
        assert_skill_result(result, "data_format_converter_json_yaml")
        assert "name: iCLONE" in result.data.get("converted_data", "")

    def test_data_format_converter_csv_to_json(self, acp):
        result = acp.execute_offering(
            "iclone-data-format-converter-v1",
            {
                "input_data": "name,age\nAlice,30\nBob,25",
                "input_format": "CSV",
                "output_format": "JSON"
            }
        )
        assert_skill_result(result, "data_format_converter_csv_json")
        converted = json.loads(result.data["converted_data"])
        assert isinstance(converted, list)
        assert len(converted) == 2

    def test_scaffold_generator(self, acp):
        result = acp.execute_offering(
            "iclone-scaffold-v1",
            {
                "stack": "FastAPI",
                "project_name": "my-api",
                "features[]": ["authentication", "database", "docker"]
            }
        )
        assert_skill_result(result, "scaffold_generator")
        data = result.data
        assert "file_tree" in data
        assert "files" in data
        assert len(data.get("files", {})) >= 3

    def test_code_review(self, acp):
        vulnerable_code = """
import sqlite3
def get_user(username):
    conn = sqlite3.connect('users.db')
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return conn.execute(query).fetchall()
"""
        result = acp.execute_offering(
            "iclone-code-review-v1",
            {"code": vulnerable_code, "language": "python"}
        )
        assert_skill_result(result, "code_review")
        data = result.data
        assert "issues" in data
        assert len(data["issues"]) > 0
        severities = [i.get("severity") for i in data["issues"]]
        assert any(s in ("critical", "high") for s in severities), "Should catch SQL injection"

    def test_sql_optimizer(self, acp):
        result = acp.execute_offering(
            "iclone-sql-optimizer-v1",
            {
                "sql_query": "SELECT * FROM orders WHERE customer_id = 123 ORDER BY created_at DESC",
                "schema_context": "orders table: id, customer_id, created_at, status, total"
            }
        )
        assert_skill_result(result, "sql_optimizer")
        data = result.data
        assert "optimized_query" in data
        assert "indexes_suggested" in data

    def test_test_generator(self, acp):
        result = acp.execute_offering(
            "iclone-test-generator-v1",
            {
                "code": SAMPLE_PYTHON_CODE,
                "language": "python",
                "test_framework": "pytest"
            }
        )
        assert_skill_result(result, "test_generator")
        data = result.data
        assert "test_code" in data
        assert "def test_" in data["test_code"]

    def test_docs_generator_readme(self, acp):
        result = acp.execute_offering(
            "iclone-docs-generator-v1",
            {"code": SAMPLE_PYTHON_CODE, "doc_type": "readme"}
        )
        assert_skill_result(result, "docs_generator_readme")
        data = result.data
        assert "documentation" in data
        assert "#" in data["documentation"]  # Should have markdown headers

    def test_docs_generator_docstrings(self, acp):
        result = acp.execute_offering(
            "iclone-docs-generator-v1",
            {"code": SAMPLE_PYTHON_CODE, "doc_type": "docstrings"}
        )
        assert_skill_result(result, "docs_generator_docstrings")
        data = result.data
        assert '"""' in data.get("documentation", "")


# ── ENGINE 3: Wallet & Crypto ────────────────────────────────────────────────

class TestWalletCryptoEngine:

    def test_wallet_quick(self, acp):
        result = acp.execute_offering(
            "iclone-wallet-quick-v1",
            {"wallet_address": TEST_WALLET, "chain": "ethereum"}
        )
        assert_skill_result(result, "wallet_quick")
        data = result.data
        assert "wallet_address" in data
        assert "eth_balance" in data
        assert isinstance(data["eth_balance"], float)

    def test_wallet_health(self, acp):
        result = acp.execute_offering(
            "iclone-wallet-health-v1",
            {"wallet_address": TEST_WALLET}
        )
        assert_skill_result(result, "wallet_health")
        data = result.data
        assert "risk_score" in data
        assert 0 <= data["risk_score"] <= 100
        assert "recommendations" in data

    def test_wallet_deep(self, acp):
        result = acp.execute_offering(
            "iclone-wallet-deep-v1",
            {"wallet_address": TEST_WALLET, "chains[]": ["ethereum"]}
        )
        assert_skill_result(result, "wallet_deep")
        data = result.data
        assert "portfolio_summary" in data

    def test_defi_opportunity_scanner(self, acp):
        result = acp.execute_offering(
            "iclone-defi-opportunity-v1",
            {
                "min_apy": 5.0,
                "chains[]": ["ethereum"],
                "risk_tolerance": "medium"
            }
        )
        assert_skill_result(result, "defi_opportunity_scanner")
        data = result.data
        assert "opportunities" in data

    def test_crypto_research_quick_btc(self, acp):
        result = acp.execute_offering(
            "iclone-crypto-research-quick-v1",
            {"asset_symbol": "BTC"}
        )
        assert_skill_result(result, "crypto_research_quick_btc")
        data = result.data
        assert "summary" in data or "sentiment" in data
        assert "signal" in data

    def test_crypto_research_deep(self, acp):
        result = acp.execute_offering(
            "iclone-crypto-research-deep-v1",
            {"asset_or_protocol": "Bitcoin", "research_depth": "comprehensive"}
        )
        assert_skill_result(result, "crypto_research_deep")
        data = result.data
        assert "executive_summary" in data
        assert "recommendation" in data
        assert "risk_assessment" in data


# ── ENGINE 4: Content & Social ───────────────────────────────────────────────

class TestContentEngine:

    def test_thread_quick(self, acp):
        result = acp.execute_offering(
            "iclone-thread-quick-v1",
            {"topic": "Why Base blockchain is the future of DeFi", "tone": "bullish"}
        )
        assert_skill_result(result, "thread_quick")
        data = result.data
        assert "tweets" in data
        assert len(data["tweets"]) == 3
        for tweet in data["tweets"]:
            assert len(tweet.get("content", "")) <= 280

    def test_thread_standard(self, acp):
        result = acp.execute_offering(
            "iclone-thread-standard-v1",
            {
                "topic": "AI agents on blockchain — the next wave",
                "tone": "analytical",
                "data_points[]": ["$2B+ AI agent market cap", "1000+ agents on Virtuals Protocol"]
            }
        )
        assert_skill_result(result, "thread_standard")
        data = result.data
        assert "tweets" in data
        assert len(data["tweets"]) == 7

    def test_blog_post(self, acp):
        result = acp.execute_offering(
            "iclone-blog-post-v1",
            {
                "topic": "How AI agents are transforming DeFi in 2025",
                "target_audience": "crypto enthusiasts",
                "keywords[]": ["AI agents", "DeFi", "Virtuals Protocol", "autonomous finance"]
            }
        )
        assert_skill_result(result, "blog_post")
        data = result.data
        assert "title" in data
        assert "markdown_content" in data
        word_count = len(data["markdown_content"].split())
        assert word_count >= 300, f"Blog post too short: {word_count} words"

    def test_newsletter_digest(self, acp):
        result = acp.execute_offering(
            "iclone-newsletter-v1",
            {
                "category": "crypto and AI agents",
                "num_items": 5,
                "audience": "DeFi users and AI enthusiasts"
            }
        )
        assert_skill_result(result, "newsletter_digest")
        data = result.data
        assert "items" in data
        assert len(data["items"]) >= 3
        assert "markdown_ready" in data


# ── ENGINE 5: Agent Platform ─────────────────────────────────────────────────

class TestPlatformEngine:

    def test_agent_training_module(self, acp):
        result = acp.execute_offering(
            "iclone-agent-training-module-v1",
            {"agent_id": "test-agent-001", "domain": "defi_protocols"}
        )
        assert_skill_result(result, "agent_training_module")
        data = result.data
        assert "knowledge_sections" in data
        assert "soul_md_addition" in data

    def test_agent_training_full(self, acp):
        result = acp.execute_offering(
            "iclone-agent-training-full-v1",
            {
                "agent_id": "test-agent-001",
                "agent_name": "TestClone",
                "wallet_address": TEST_WALLET
            }
        )
        assert_skill_result(result, "agent_training_full")
        data = result.data
        assert data["modules_count"] == 15
        assert len(data["modules"]) == 15

    def test_skill_build_quick(self, acp):
        result = acp.execute_offering(
            "iclone-build-skill-quick-v1",
            {
                "skill_description": "A skill that converts temperature between Celsius, Fahrenheit, and Kelvin",
                "input_schema": {"value": "float", "from_unit": "string", "to_unit": "string"},
                "output_schema": {"result": "float", "conversion": "string"}
            }
        )
        assert_skill_result(result, "skill_build_quick")
        data = result.data
        assert "python_code" in data
        assert "def " in data["python_code"]

    def test_skill_build_standard(self, acp):
        result = acp.execute_offering(
            "iclone-build-skill-standard-v1",
            {
                "skill_description": "A web scraping skill that extracts structured data from e-commerce product pages",
                "target_agent": "iCLONE",
                "input_output_examples[]": [
                    {"input": {"url": "https://example.com/product/123"}, "output": {"name": "Product", "price": 29.99}}
                ]
            }
        )
        assert_skill_result(result, "skill_build_standard")
        data = result.data
        assert "python_code" in data
        assert len(data["python_code"]) > 200

    def test_multi_agent_coordination(self, acp):
        result = acp.execute_offering(
            "iclone-coordinate-agents-v1",
            {
                "task_description": "Research Base blockchain and write a summary report",
                "agent_ids[]": ["research-agent-1", "writer-agent-1"],
                "expected_output": "A structured research report on Base blockchain"
            }
        )
        assert_skill_result(result, "multi_agent_coordination")
        data = result.data
        assert "execution_dag" in data or "task_decomposition" in data

    def test_platform_onboarding(self, acp):
        result = acp.execute_offering(
            "iclone-onboarding-v1",
            {"agent_id_or_user_id": "user-test-12345"}
        )
        assert_skill_result(result, "platform_onboarding")
        data = result.data
        assert "welcome_message" in data
        assert "recommended_skills" in data
        assert data.get("onboarding_complete") is True


# ── ACP Lifecycle ─────────────────────────────────────────────────────────────

class TestACPLifecycle:
    """Tests for the ACP job lifecycle (accept → execute → deliver → complete)."""

    def test_full_job_lifecycle(self):
        """Accept a job, execute it, deliver, complete."""
        acp = ACPSkill()

        # Step 1: Accept job
        accept = acp.accept_job(
            job_id="test-job-001",
            offering_id="iclone-research-quick-v1",
            client_agent_id="client-agent-abc",
            requirements={"query": "What is Base blockchain?"},
        )
        assert accept.success, f"Accept failed: {accept.error}"
        assert accept.data["job_id"] == "test-job-001"

        # Step 2: Execute the offering
        execute_result = acp.execute_offering(
            "iclone-research-quick-v1",
            {"query": "What is Base blockchain?"}
        )
        assert execute_result.success, f"Execute failed: {execute_result.error}"

        # Step 3: Submit deliverable
        deliverable = json.dumps(execute_result.data, default=str)
        deliver = acp.submit_deliverable(
            job_id="test-job-001",
            deliverable_content=deliverable,
            deliverable_url="https://ipfs.io/ipfs/placeholder",
        )
        assert deliver.success, f"Deliver failed: {deliver.error}"

        # Step 4: Complete job
        complete = acp.complete_job("test-job-001")
        assert complete.success, f"Complete failed: {complete.error}"
        assert complete.data["usdc_earned"] == 0.25

        print("\n  [full_lifecycle] OK: Job accepted → executed → delivered → completed")

    def test_list_offerings_count(self):
        acp = ACPSkill()
        offerings = acp.list_offerings()
        assert len(offerings) == 32, f"Expected 32 offerings, got {len(offerings)}"
        print(f"\n  [list_offerings] OK: {len(offerings)} offerings registered")

    def test_execute_unknown_offering(self):
        acp = ACPSkill()
        result = acp.execute_offering("nonexistent-offering-id", {})
        assert not result.success
        assert "Unknown offering" in result.error
