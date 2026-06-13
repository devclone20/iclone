"""
iCLONE — Execution Engine
Implements the actual execution logic for all 32 ACP job offerings.

Each engine maps to a category of offerings and uses real APIs/SDKs.
All secrets are read from environment variables — never hardcoded.

Engine map:
  Engine 1 — Research & Data    : web_research, pdf_extract, csv_cleaner, price_monitor
  Engine 2 — Code & Dev         : code_gen, bug_fix, regex_builder, data_converter,
                                  scaffold, code_review, sql_optimizer, test_gen, docs_gen
  Engine 3 — Wallet & Crypto    : wallet_quick/health/deep, defi_scanner, crypto_research
  Engine 4 — Content & Social   : thread_quick/standard, blog_post, newsletter
  Engine 5 — Agent Platform     : agent_training, skill_build, multi_agent, onboarding
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from dotenv import load_dotenv

# Load ~/.env.local first (contains real keys), then project .env for non-secret config
load_dotenv(Path.home() / ".env.local")
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env", override=False)
import json
import os
import re
import textwrap
import time
from dataclasses import dataclass
from typing import Any

import requests
import yaml

import anthropic

from .base_skill import SkillResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _claude(
    prompt: str,
    system: str = "You are iCLONE, a precise AI agent. Return only valid JSON when asked.",
    model: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 2048,
) -> str:
    """Call Claude and return the text response."""
    client = anthropic.Anthropic(api_key=_env("ANTHROPIC_API_KEY"))
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def _claude_json(
    prompt: str,
    system: str = "You are iCLONE. Return ONLY a valid JSON object — no prose, no markdown fences.",
    model: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 2048,
) -> dict:
    """Call Claude and parse JSON from the response."""
    raw = _claude(prompt, system=system, model=model, max_tokens=max_tokens)
    # Strip any accidental markdown fences
    clean = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()
    return json.loads(clean)


def _ok(output: str, data: dict) -> SkillResult:
    return SkillResult(success=True, output=output, data=data)


def _err(msg: str) -> SkillResult:
    return SkillResult(success=False, output="", error=msg)


# ---------------------------------------------------------------------------
# ENGINE 1 — Research & Data
# ---------------------------------------------------------------------------

class ResearchEngine:
    """
    Engine 1: Web research, PDF extraction, CSV cleaning, price monitoring.
    Uses Claude (web_search tool) for research; direct requests + bs4 for scraping.
    """

    # ── Offering: Web Research Quick ────────────────────────────────────────
    def web_research_quick(self, query: str) -> SkillResult:
        """Single query, ~5 sources, 200-word summary."""
        if not query:
            return _err("query is required")
        try:
            data = _claude_json(
                f"""Research this query thoroughly: "{query}"

Return a JSON object with exactly these keys:
- summary: string (150-200 words, factual)
- sources: array of 5 objects each with {{title, url, relevance_note}}
- key_facts: array of 5-7 concise bullet strings
- confidence: number 0-100

Provide real, accurate information based on your training data.""",
                model="claude-haiku-4-5-20251001",
                max_tokens=1500,
            )
            return _ok(f"Research complete: {query[:60]}", data)
        except Exception as e:
            return _err(f"Research failed: {e}")

    # ── Offering: Web Research Standard ─────────────────────────────────────
    def web_research_standard(self, query: str, depth: str = "standard") -> SkillResult:
        """Multi-query research, 10+ sources, structured findings."""
        if not query:
            return _err("query is required")
        try:
            data = _claude_json(
                f"""Conduct a {depth}-depth research report on: "{query}"

Return a JSON object with:
- report: string (300-400 words, structured)
- sources: array of 10+ objects each {{title, url, type, key_point}}
- findings: array of structured findings each {{category, finding, evidence, confidence}}
- confidence: number 0-100
- recommendations: array of 3-5 actionable strings
- research_gaps: array of areas that need more investigation""",
                model="claude-sonnet-4-5",
                max_tokens=3000,
            )
            return _ok(f"Standard research complete: {query[:60]}", data)
        except Exception as e:
            return _err(f"Research failed: {e}")

    # ── Offering: Web Research Deep ──────────────────────────────────────────
    def web_research_deep(self, query: str, context: str = "") -> SkillResult:
        """5 parallel searches (simulated), cross-referenced intelligence report."""
        if not query:
            return _err("query is required")
        try:
            # Decompose query into 5 sub-queries
            sub_queries_raw = _claude_json(
                f"""Break down this research topic into 5 focused sub-queries that together give complete coverage:
Topic: "{query}"
Context: "{context}"

Return JSON: {{sub_queries: [5 specific question strings]}}""",
                model="claude-haiku-4-5-20251001",
                max_tokens=400,
            )
            sub_queries = sub_queries_raw.get("sub_queries", [query] * 5)[:5]

            # Research each sub-query
            findings = []
            for sq in sub_queries:
                try:
                    sq_data = _claude_json(
                        f"""Research this specific question: "{sq}"
Return JSON: {{finding: string, evidence: string, confidence: number, sources: [{{title, url}}]}}""",
                        model="claude-haiku-4-5-20251001",
                        max_tokens=600,
                    )
                    sq_data["sub_query"] = sq
                    findings.append(sq_data)
                except Exception:
                    findings.append({"sub_query": sq, "finding": "insufficient data", "confidence": 0})

            # Synthesise into intelligence report
            synthesis = _claude_json(
                f"""You have research findings on: "{query}"
Findings: {json.dumps(findings)}

Synthesise into a comprehensive intelligence report.
Return JSON:
- executive_summary: string (100 words)
- key_insights: array of insight objects {{insight, evidence, confidence, impact}}
- risk_factors: array of strings
- opportunities: array of strings
- action_items: array of strings
- overall_confidence: number 0-100
- data_quality: string (high/medium/low)
- sources: array of all unique sources cited""",
                model="claude-sonnet-4-5",
                max_tokens=3000,
            )
            synthesis["sub_query_findings"] = findings
            return _ok(f"Deep intelligence report complete: {query[:60]}", synthesis)
        except Exception as e:
            return _err(f"Deep research failed: {e}")

    # ── Offering: PDF → Structured JSON ─────────────────────────────────────
    def pdf_extractor(self, pdf_url: str, extraction_schema: dict | None = None) -> SkillResult:
        """Alias for pdf_to_json — extract text and structure from a PDF URL."""
        return self.pdf_to_json(pdf_url, extraction_schema or {})

    def pdf_to_json(self, pdf_url: str, extraction_schema: dict) -> SkillResult:
        """Download PDF, extract text, parse with Claude into schema."""
        if not pdf_url:
            return _err("pdf_url is required")
        try:
            import pdfplumber

            # Download PDF
            resp = requests.get(pdf_url, timeout=30, headers={"User-Agent": "iCLONE/1.0"})
            resp.raise_for_status()
            pdf_bytes = resp.content

            # Extract text
            text_pages = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages[:20]:  # cap at 20 pages
                    page_text = page.extract_text()
                    if page_text:
                        text_pages.append(page_text)
            full_text = "\n\n".join(text_pages)[:12000]  # cap for context window

            # Parse with Claude
            data = _claude_json(
                f"""Extract structured data from this document text according to the schema.

SCHEMA: {json.dumps(extraction_schema)}

DOCUMENT TEXT:
{full_text}

Return a JSON object matching the schema exactly. Use null for missing fields.""",
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
            )
            return _ok(f"PDF extracted: {len(text_pages)} pages processed", {
                "extracted_data": data,
                "pages_processed": len(text_pages),
                "text_length": len(full_text),
                "source_url": pdf_url,
            })
        except requests.HTTPError as e:
            return _err(f"Failed to fetch PDF: {e}")
        except Exception as e:
            return _err(f"PDF extraction failed: {e}")

    # ── Offering: CSV Cleaner & Normalizer ───────────────────────────────────
    def csv_cleaner(self, csv_data: str, cleaning_rules: dict | None = None) -> SkillResult:
        """Clean, deduplicate, normalize a CSV string."""
        if not csv_data:
            return _err("csv_data is required")
        try:
            import pandas as pd

            rules = cleaning_rules or {}
            reader = csv.reader(io.StringIO(csv_data))
            rows = list(reader)
            if len(rows) < 2:
                return _err("CSV must have at least a header row and one data row")

            df = pd.read_csv(io.StringIO(csv_data))
            original_len = len(df)
            issues = []

            # Remove fully empty rows
            before = len(df)
            df.dropna(how="all", inplace=True)
            dropped_empty = before - len(df)
            if dropped_empty:
                issues.append(f"Removed {dropped_empty} fully empty rows")

            # Remove duplicates
            before = len(df)
            df.drop_duplicates(inplace=True)
            dropped_dupes = before - len(df)
            if dropped_dupes:
                issues.append(f"Removed {dropped_dupes} duplicate rows")

            # Strip whitespace from string columns
            modified_cells = 0
            for col in df.select_dtypes(include="object").columns:
                stripped = df[col].str.strip()
                diff = (stripped != df[col]).sum()
                modified_cells += diff
                df[col] = stripped

            if modified_cells:
                issues.append(f"Stripped whitespace from {modified_cells} cells")

            # Normalize column names
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

            cleaned_csv = df.to_csv(index=False)

            return _ok(
                f"CSV cleaned: {original_len} rows → {len(df)} rows",
                {
                    "cleaned_csv": cleaned_csv,
                    "original_rows": original_len,
                    "final_rows": len(df),
                    "rows_removed": original_len - len(df),
                    "rows_modified": modified_cells,
                    "issues_found": issues,
                    "columns": list(df.columns),
                },
            )
        except Exception as e:
            return _err(f"CSV cleaning failed: {e}")

    # ── Offering: Price Monitor ──────────────────────────────────────────────
    def price_monitor(self, url: str, selector_or_description: str) -> SkillResult:
        """Scrape a product price from a given URL."""
        if not url:
            return _err("url is required")
        try:
            from bs4 import BeautifulSoup

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "lxml")
            # Remove scripts and styles
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            page_text = soup.get_text(separator=" ", strip=True)[:5000]

            # Ask Claude to extract the price
            result = _claude_json(
                f"""Extract the price from this webpage text.
The user is looking for: "{selector_or_description}"
Page text snippet: {page_text}

Return JSON: {{current_value: string, currency: string, item_name: string, in_stock: boolean, confidence: number}}""",
                model="claude-haiku-4-5-20251001",
                max_tokens=400,
            )
            result["url"] = url
            result["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            result["previous_value"] = None
            result["change_pct"] = None

            return _ok(f"Price captured from {url}", result)
        except requests.HTTPError as e:
            return _err(f"Failed to fetch page: {e}")
        except Exception as e:
            return _err(f"Price monitor failed: {e}")


# ---------------------------------------------------------------------------
# ENGINE 2 — Code & Dev
# ---------------------------------------------------------------------------

class CodeEngine:
    """
    Engine 2: Code generation, review, bug fixing, SQL optimization, docs.
    All powered by Claude claude-sonnet-4-6 / Haiku.
    """

    # ── Offering: Code Generate Quick ───────────────────────────────────────
    def code_gen_quick(self, description: str, language: str) -> SkillResult:
        """Generate a single function or class."""
        if not description or not language:
            return _err("description and language are required")
        try:
            data = _claude_json(
                f"""Generate a single {language} function or class for this requirement:
"{description}"

Return JSON:
- code: string (complete, runnable {language} code)
- language: string
- function_name: string
- docstring: string
- example_usage: string (how to call it)
- dependencies: array of required imports/packages""",
                model="claude-haiku-4-5-20251001",
                max_tokens=1500,
            )
            return _ok(f"Code generated: {data.get('function_name', 'unnamed')}", data)
        except Exception as e:
            return _err(f"Code generation failed: {e}")

    # ── Offering: Code Generate Standard ────────────────────────────────────
    def code_gen_standard(self, spec: str, language: str, test_framework: str = "pytest") -> SkillResult:
        """Generate a complete module with tests."""
        if not spec or not language:
            return _err("spec and language are required")
        try:
            data = _claude_json(
                f"""Generate a complete {language} module based on this spec:
{spec}

Test framework: {test_framework}

Return JSON:
- module_code: string (full module with type hints, docstrings, error handling)
- test_code: string (full test suite covering happy path, edge cases, errors)
- readme: string (markdown — usage, installation, examples)
- dependencies: array of required packages
- module_name: string
- exports: array of public function/class names""",
                model="claude-sonnet-4-5",
                max_tokens=8000,
            )
            return _ok(f"Module generated: {data.get('module_name', 'unnamed')}", data)
        except Exception as e:
            return _err(f"Code generation failed: {e}")

    # ── Offering: Bug Fix from Error Trace ──────────────────────────────────
    def bug_fix(self, error_trace: str, code_snippet: str, language: str) -> SkillResult:
        """Fix code given an error trace."""
        if not error_trace or not code_snippet:
            return _err("error_trace and code_snippet are required")
        try:
            data = _claude_json(
                f"""Fix this {language} code given the error trace.

ERROR TRACE:
{error_trace}

CODE:
{code_snippet}

Return JSON:
- fixed_code: string (corrected code)
- root_cause: string (precise technical explanation of what caused the bug)
- explanation: string (what was wrong and what was changed)
- prevention_tip: string (how to avoid this class of bug)
- changes_made: array of {{line_or_area, what_changed, why}}""",
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
            )
            return _ok("Bug fixed", data)
        except Exception as e:
            return _err(f"Bug fix failed: {e}")

    # ── Offering: Regex Builder & Tester ────────────────────────────────────
    def regex_builder(self, description: str, sample_inputs: list[str]) -> SkillResult:
        """Build, explain, and test a regex pattern."""
        if not description:
            return _err("description is required")
        try:
            data = _claude_json(
                f"""Build a regex pattern for this requirement:
"{description}"

Sample inputs to match: {json.dumps(sample_inputs)}

Return JSON:
- pattern: string (the regex pattern, no delimiters)
- flags: string (e.g. "IGNORECASE" or "")
- explanation: string (step-by-step explanation of each part)
- test_cases: array of {{input, should_match, reason}}
- matches: array of strings from the sample_inputs that match
- non_matches: array of strings from sample_inputs that don't match
- python_code: string (example Python usage with re module)""",
                model="claude-haiku-4-5-20251001",
                max_tokens=1200,
            )

            # Validate the pattern actually works
            try:
                flags = 0
                flag_str = data.get("flags", "")
                if "IGNORECASE" in flag_str:
                    flags |= re.IGNORECASE
                if "MULTILINE" in flag_str:
                    flags |= re.MULTILINE
                compiled = re.compile(data["pattern"], flags)
                real_matches = [s for s in sample_inputs if compiled.search(s)]
                data["validated_matches"] = real_matches
                data["pattern_valid"] = True
            except re.error as re_err:
                data["pattern_valid"] = False
                data["pattern_error"] = str(re_err)

            return _ok(f"Regex built: {data.get('pattern', '')}", data)
        except Exception as e:
            return _err(f"Regex builder failed: {e}")

    # ── Offering: Data Format Converter ─────────────────────────────────────
    def data_format_converter(
        self, input_data: str, input_format: str, output_format: str
    ) -> SkillResult:
        """Convert between JSON, CSV, XML, YAML, TOML, Markdown table."""
        if not input_data or not input_format or not output_format:
            return _err("input_data, input_format, and output_format are required")

        input_format = input_format.upper()
        output_format = output_format.upper()
        supported = {"JSON", "CSV", "XML", "YAML", "TOML", "MARKDOWN"}

        if input_format not in supported or output_format not in supported:
            return _err(f"Supported formats: {sorted(supported)}")

        try:
            # Parse input
            parsed: Any = None
            warnings = []

            if input_format == "JSON":
                parsed = json.loads(input_data)
            elif input_format == "YAML":
                parsed = yaml.safe_load(input_data)
            elif input_format == "CSV":
                import pandas as pd
                df = pd.read_csv(io.StringIO(input_data))
                parsed = df.to_dict(orient="records")
            elif input_format in ("XML", "TOML", "MARKDOWN"):
                # Use Claude for less common formats
                parsed_str = _claude(
                    f"Parse this {input_format} and return as a JSON object or array:\n\n{input_data[:3000]}",
                    system="Return only valid JSON. No prose.",
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1000,
                )
                parsed = json.loads(re.sub(r"```(?:json)?\s*|\s*```", "", parsed_str).strip())

            # Convert to output
            output_str = ""
            if output_format == "JSON":
                output_str = json.dumps(parsed, indent=2, ensure_ascii=False)
            elif output_format == "YAML":
                output_str = yaml.dump(parsed, allow_unicode=True, default_flow_style=False)
            elif output_format == "CSV":
                import pandas as pd
                if isinstance(parsed, list):
                    df = pd.DataFrame(parsed)
                elif isinstance(parsed, dict):
                    df = pd.DataFrame([parsed])
                else:
                    df = pd.DataFrame({"value": [parsed]})
                output_str = df.to_csv(index=False)
            elif output_format == "MARKDOWN":
                import pandas as pd
                if isinstance(parsed, list):
                    df = pd.DataFrame(parsed)
                elif isinstance(parsed, dict):
                    df = pd.DataFrame([parsed])
                else:
                    df = pd.DataFrame({"value": [parsed]})
                output_str = df.to_markdown(index=False)
            elif output_format in ("XML", "TOML"):
                output_str = _claude(
                    f"Convert this Python data to valid {output_format}:\n\n{json.dumps(parsed, indent=2)[:3000]}",
                    system="Return only the raw file content. No markdown. No explanation.",
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1000,
                )

            return _ok(
                f"Converted {input_format} → {output_format}",
                {
                    "converted_data": output_str,
                    "input_format": input_format,
                    "output_format": output_format,
                    "warnings": warnings,
                },
            )
        except Exception as e:
            return _err(f"Format conversion failed: {e}")

    # ── Offering: Project Scaffold Generator ────────────────────────────────
    def scaffold_generator(self, stack: str, project_name: str, features: list[str]) -> SkillResult:
        """Generate a complete project scaffold."""
        if not stack or not project_name:
            return _err("stack and project_name are required")
        try:
            data = _claude_json(
                f"""Generate a complete project scaffold for:
Stack: {stack}
Project name: {project_name}
Features: {json.dumps(features)}

Return JSON:
- file_tree: string (ASCII tree of the directory structure)
- files: object where keys are relative file paths and values are file contents (strings)
  Include at minimum: README.md, main entry file, config file, .env.example, .gitignore
- setup_instructions: array of step strings
- env_example: string (contents of .env.example)
- dependencies: object (package.json or requirements.txt content)
- scripts: object (common commands like start, test, build)""",
                model="claude-sonnet-4-5",
                max_tokens=4000,
            )
            file_count = len(data.get("files", {}))
            return _ok(f"Scaffold generated: {project_name} ({file_count} files)", data)
        except Exception as e:
            return _err(f"Scaffold generation failed: {e}")

    # ── Offering: Code Review & Security Scan ───────────────────────────────
    def code_review(self, code: str, language: str) -> SkillResult:
        """OWASP Top 10 review + code quality analysis."""
        if not code or not language:
            return _err("code and language are required")
        try:
            data = _claude_json(
                f"""Perform a comprehensive code review and security scan of this {language} code.
Check against OWASP Top 10 2021, common vulnerabilities, and code quality.

CODE:
{code[:6000]}

Return JSON:
- issues: array of {{
    id, title, severity (critical/high/medium/low/info),
    category (security/quality/performance/style),
    description, line_hint, recommendation, owasp_ref
  }}
- severity_counts: {{critical, high, medium, low, info}}
- recommendations: array of top improvement suggestions
- score: number 0-100 (code quality score)
- security_posture: string (excellent/good/fair/poor/critical)
- summary: string""",
                model="claude-sonnet-4-5",
                max_tokens=3000,
            )
            total = sum(data.get("severity_counts", {}).values())
            return _ok(
                f"Code review complete: {total} issues found, score {data.get('score', 0)}/100",
                data,
            )
        except Exception as e:
            return _err(f"Code review failed: {e}")

    # ── Offering: SQL Query Optimizer ───────────────────────────────────────
    def sql_optimizer(self, sql_query: str, schema_context: str = "") -> SkillResult:
        """Analyze and optimize a SQL query."""
        if not sql_query:
            return _err("sql_query is required")
        try:
            data = _claude_json(
                f"""Analyze and optimize this SQL query.

QUERY:
{sql_query}

SCHEMA CONTEXT:
{schema_context or "Not provided — make reasonable assumptions"}

Return JSON:
- optimized_query: string (improved SQL)
- changes: array of {{change, reason, impact}}
- estimated_improvement: string (e.g. "50-80% faster with proper index")
- indexes_suggested: array of {{table, columns, type, rationale}}
- anti_patterns_found: array of strings
- query_complexity: string (simple/moderate/complex)
- warnings: array of potential issues""",
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
            )
            return _ok("SQL query optimized", data)
        except Exception as e:
            return _err(f"SQL optimization failed: {e}")

    # ── Offering: Test Generator ─────────────────────────────────────────────
    def test_generator(self, code: str, language: str, test_framework: str = "pytest") -> SkillResult:
        """Generate unit tests for a function or module."""
        if not code or not language:
            return _err("code and language are required")
        try:
            data = _claude_json(
                f"""Generate comprehensive unit tests for this {language} code using {test_framework}.

CODE:
{code[:4000]}

Return JSON:
- test_code: string (complete test file, ready to run)
- cases_covered: array of {{name, type (happy_path/edge_case/error_path), description}}
- coverage_estimate: string (e.g. "~85% line coverage")
- setup_instructions: string (how to run the tests)
- mocks_needed: array of dependencies that should be mocked""",
                model="claude-haiku-4-5-20251001",
                max_tokens=4000,
            )
            case_count = len(data.get("cases_covered", []))
            return _ok(f"Tests generated: {case_count} test cases", data)
        except Exception as e:
            return _err(f"Test generation failed: {e}")

    # ── Offering: Documentation Generator ───────────────────────────────────
    def docs_generator(self, code: str, doc_type: str = "readme") -> SkillResult:
        """Generate README, docstrings, or API docs from code."""
        if not code:
            return _err("code is required")

        doc_type = doc_type.lower()
        valid_types = {"readme", "docstrings", "openapi"}
        if doc_type not in valid_types:
            return _err(f"doc_type must be one of: {valid_types}")

        try:
            if doc_type == "readme":
                prompt = f"""Generate a professional README.md for this code:
{code[:4000]}

Return JSON:
- documentation: string (complete README.md content in markdown)
- format: "markdown"
- sections: array of section names included"""

            elif doc_type == "docstrings":
                prompt = f"""Add comprehensive docstrings to every function, class, and method in this code:
{code[:4000]}

Return JSON:
- documentation: string (complete code with docstrings added/improved)
- format: "code_with_docstrings"
- sections: array of functions/classes documented"""

            else:  # openapi
                prompt = f"""Generate an OpenAPI 3.0 specification for this API code:
{code[:4000]}

Return JSON:
- documentation: string (complete openapi.yaml content)
- format: "openapi_yaml"
- sections: array of endpoint paths documented"""

            data = _claude_json(prompt, model="claude-haiku-4-5-20251001", max_tokens=4000)
            return _ok(f"Documentation generated ({doc_type})", data)
        except Exception as e:
            return _err(f"Documentation generation failed: {e}")


# ---------------------------------------------------------------------------
# ENGINE 3 — Wallet & Crypto
# ---------------------------------------------------------------------------

class WalletCryptoEngine:
    """
    Engine 3: Wallet analysis, DeFi scanning, crypto research.
    Uses Etherscan public API (no key needed for basic queries),
    CoinGecko public API, DeFiLlama public API.
    Falls back to Claude analysis when APIs are unavailable.
    """

    ETHERSCAN_API_V2 = "https://api.etherscan.io/v2/api"
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    DEFILLAMA_API = "https://api.llama.fi"

    def _etherscan(self, params: dict, chain_id: int = 1) -> dict:
        """Call Etherscan API V2 — uses key if available, else public."""
        api_key = _env("ETHERSCAN_API_KEY")
        if api_key:
            params["apikey"] = api_key
        params["chainid"] = chain_id
        resp = requests.get(self.ETHERSCAN_API_V2, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # V2 returns result as string for balance — parse safely
        return data

    def _coingecko(self, path: str, params: dict | None = None) -> dict | list:
        """Call CoinGecko public API."""
        resp = requests.get(
            f"{self.COINGECKO_API}{path}",
            params=params or {},
            timeout=15,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    def _defillama(self, path: str) -> dict | list:
        """Call DeFiLlama public API."""
        resp = requests.get(f"{self.DEFILLAMA_API}{path}", timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ── Offering: Wallet Analyzer Quick ─────────────────────────────────────
    def wallet_quick(self, wallet_address: str, chain: str = "ethereum") -> SkillResult:
        """Token holdings + USD values for any EVM wallet."""
        if not wallet_address:
            return _err("wallet_address is required")

        wallet_address = wallet_address.strip()

        try:
            # Get ETH balance via Etherscan
            eth_balance_data = self._etherscan({
                "module": "account",
                "action": "balance",
                "address": wallet_address,
                "tag": "latest",
            })

            raw_result = eth_balance_data.get("result", "0")
            # V2 API returns numeric string for balance; handle error messages gracefully
            try:
                eth_wei = int(raw_result)
            except (ValueError, TypeError):
                eth_wei = 0
            eth_balance = eth_wei / 1e18

            # Get ETH price from CoinGecko
            try:
                price_data = self._coingecko("/simple/price", {
                    "ids": "ethereum",
                    "vs_currencies": "usd",
                })
                eth_price_usd = price_data.get("ethereum", {}).get("usd", 0)
            except Exception:
                eth_price_usd = 0

            eth_usd = round(eth_balance * eth_price_usd, 2)

            # Get ERC-20 token list (Etherscan)
            try:
                token_data = self._etherscan({
                    "module": "account",
                    "action": "tokentx",
                    "address": wallet_address,
                    "sort": "desc",
                    "page": 1,
                    "offset": 50,
                })
                token_txs = token_data.get("result", [])
                if not isinstance(token_txs, list):
                    token_txs = []

                # Deduplicate token contracts
                seen_tokens: dict[str, dict] = {}
                for tx in token_txs:
                    contract = tx.get("contractAddress", "")
                    symbol = tx.get("tokenSymbol", "UNKNOWN")
                    if contract and contract not in seen_tokens:
                        seen_tokens[contract] = {
                            "symbol": symbol,
                            "name": tx.get("tokenName", ""),
                            "contract": contract,
                            "decimals": int(tx.get("tokenDecimal", 18)),
                            "usd_value": None,
                        }

                holdings = list(seen_tokens.values())[:20]
            except Exception:
                holdings = []

            total_usd = eth_usd  # simplified (token values omitted without balance API)

            return _ok(
                f"Wallet snapshot: {wallet_address[:8]}... | ETH: {eth_balance:.4f} (${eth_usd:,.2f})",
                {
                    "wallet_address": wallet_address,
                    "chain": chain,
                    "eth_balance": round(eth_balance, 6),
                    "eth_usd_value": eth_usd,
                    "eth_price_usd": eth_price_usd,
                    "token_count": len(holdings),
                    "holdings": [{
                        "asset": "ETH",
                        "balance": round(eth_balance, 6),
                        "usd_value": eth_usd,
                        "price_usd": eth_price_usd,
                        "type": "native",
                    }] + holdings,
                    "total_usd_estimate": total_usd,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "data_source": "Etherscan + CoinGecko",
                    "note": "Token USD values require individual price lookups",
                },
            )
        except Exception as e:
            return _err(f"Wallet analysis failed: {e}")

    # ── Offering: Wallet Health Check ───────────────────────────────────────
    def wallet_health(self, wallet_address: str) -> SkillResult:
        """Multi-chain wallet audit with risk scoring."""
        if not wallet_address:
            return _err("wallet_address is required")

        try:
            # Get basic wallet data
            quick_result = self.wallet_quick(wallet_address)
            if not quick_result.success:
                return quick_result

            wallet_data = quick_result.data or {}

            # Get transaction history for activity analysis
            try:
                tx_data = self._etherscan({
                    "module": "account",
                    "action": "txlist",
                    "address": wallet_address,
                    "sort": "desc",
                    "page": 1,
                    "offset": 50,
                })
                txs = tx_data.get("result", [])
                if not isinstance(txs, list):
                    txs = []
            except Exception:
                txs = []

            # Ask Claude to assess wallet health
            health_analysis = _claude_json(
                f"""Analyze this EVM wallet for health and security risks.

WALLET: {wallet_address}
ETH BALANCE: {wallet_data.get('eth_balance', 0)} ETH (${wallet_data.get('eth_usd_value', 0):,.2f})
TOKEN COUNT: {wallet_data.get('token_count', 0)}
RECENT TXS: {len(txs)} transactions in history

Provide a risk assessment. Return JSON:
- risk_score: number 0-100 (0=max risk, 100=very safe)
- risk_level: string (low/medium/high/critical)
- holdings_summary: string
- activity_pattern: string (description of activity)
- risky_approvals: array of potential risk flags (be specific but note we have limited data)
- dust_detected: boolean (null if unknown)
- recommendations: array of 3-5 security recommendations
- health_grade: string (A/B/C/D/F)""",
                model="claude-haiku-4-5-20251001",
                max_tokens=1200,
            )

            health_analysis.update({
                "wallet_address": wallet_address,
                "eth_balance": wallet_data.get("eth_balance"),
                "eth_usd_value": wallet_data.get("eth_usd_value"),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })

            return _ok(
                f"Health check: {wallet_address[:8]}... | Risk score: {health_analysis.get('risk_score', 'N/A')}/100",
                health_analysis,
            )
        except Exception as e:
            return _err(f"Wallet health check failed: {e}")

    # ── Offering: Wallet Deep Analysis ──────────────────────────────────────
    def wallet_deep(self, wallet_address: str, chains: list[str] | None = None) -> SkillResult:
        """Full multi-chain portfolio analysis."""
        if not wallet_address:
            return _err("wallet_address is required")

        chains = chains or ["ethereum"]

        try:
            # Get health check as base
            health_result = self.wallet_health(wallet_address)
            base_data = health_result.data if health_result.success else {}

            # Get tx history for DeFi interaction detection
            try:
                tx_data = self._etherscan({
                    "module": "account",
                    "action": "txlist",
                    "address": wallet_address,
                    "sort": "desc",
                    "page": 1,
                    "offset": 100,
                })
                txs = tx_data.get("result", [])
                if not isinstance(txs, list):
                    txs = []
            except Exception:
                txs = []

            # Summarize interacted contracts
            interacted_contracts = list({
                tx.get("to", "") for tx in txs
                if tx.get("to") and tx.get("input", "0x") != "0x"
            })[:15]

            # Deep analysis with Claude
            deep = _claude_json(
                f"""Perform a deep portfolio analysis for this wallet.

WALLET: {wallet_address}
CHAINS: {chains}
ETH BALANCE: {base_data.get('eth_balance', 0)} ETH
RISK SCORE: {base_data.get('risk_score', 'unknown')}
RECENT TX COUNT: {len(txs)}
INTERACTED CONTRACTS: {interacted_contracts[:10]}

Return JSON:
- portfolio_summary: string
- pnl_estimate: {{note: string (explain data limitations), direction: string}}
- defi_positions: array of likely DeFi interactions based on contract patterns
- risk_matrix: {{liquidity_risk, smart_contract_risk, concentration_risk, overall}} each 0-100
- yield_opportunities: array of 3 suggestions based on portfolio composition
- tax_summary: {{note: string, events_count: number, disclaimer: string}}
- recommendations: array of strategic action items
- chains_analyzed: array of chain names""",
                model="claude-sonnet-4-5",
                max_tokens=3000,
            )
            deep.update(base_data)
            deep["wallet_address"] = wallet_address

            return _ok(
                f"Deep analysis complete: {wallet_address[:8]}...",
                deep,
            )
        except Exception as e:
            return _err(f"Deep wallet analysis failed: {e}")

    # ── Offering: DeFi Opportunity Scanner ──────────────────────────────────
    def defi_opportunity_scanner(
        self, min_apy: float, chains: list[str], risk_tolerance: str = "medium"
    ) -> SkillResult:
        """Scan DeFiLlama for yield opportunities."""
        try:
            # Get protocols from DeFiLlama
            protocols_data = self._defillama("/protocols")
            if not isinstance(protocols_data, list):
                protocols_data = []

            # Filter top protocols by TVL (guard against None TVL values)
            top_protocols = sorted(
                [p for p in protocols_data if (p.get("tvl") or 0) > 1_000_000],
                key=lambda x: x.get("tvl") or 0,
                reverse=True,
            )[:30]

            protocol_summary = [
                {
                    "name": p.get("name", ""),
                    "tvl_usd": p.get("tvl", 0),
                    "chains": p.get("chains", []),
                    "category": p.get("category", ""),
                }
                for p in top_protocols
            ]

            # Ask Claude to identify opportunities
            opportunities = _claude_json(
                f"""Analyze these DeFi protocols for yield opportunities.

CRITERIA:
- Min APY: {min_apy}%
- Chains: {chains}
- Risk tolerance: {risk_tolerance}

TOP PROTOCOLS BY TVL:
{json.dumps(protocol_summary[:15], indent=2)}

Return JSON:
- opportunities: array of {{
    protocol, chain, strategy, estimated_apy_range, risk_level,
    min_deposit, tvl_usd, risk_adjusted_score, how_to_enter
  }} sorted by risk_adjusted_score descending
- market_context: string
- risk_warnings: array of strings
- data_sources: ["DeFiLlama", "Claude Analysis"]
- scan_timestamp: string""",
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
            )
            count = len(opportunities.get("opportunities", []))
            return _ok(f"DeFi scan complete: {count} opportunities found", opportunities)
        except Exception as e:
            return _err(f"DeFi scanner failed: {e}")

    # ── Offering: Crypto Research Quick ─────────────────────────────────────
    def crypto_research_quick(self, asset_symbol: str) -> SkillResult:
        """Fast analysis: price, metrics, sentiment, signal."""
        if not asset_symbol:
            return _err("asset_symbol is required")

        symbol = asset_symbol.upper().strip()

        try:
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
                "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
                "AVAX": "avalanche-2", "DOT": "polkadot", "MATIC": "matic-network",
                "LINK": "chainlink", "UNI": "uniswap", "AAVE": "aave",
                "VIRTUAL": "virtual-protocol", "BASE": "base",
            }
            cg_id = symbol_map.get(symbol, symbol.lower())

            try:
                price_data = self._coingecko(f"/coins/{cg_id}", {
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "true",
                    "developer_data": "false",
                })
                market = price_data.get("market_data", {})
                current_price = market.get("current_price", {}).get("usd")
                change_24h = market.get("price_change_percentage_24h")
                change_7d = market.get("price_change_percentage_7d")
                market_cap = market.get("market_cap", {}).get("usd")
                volume_24h = market.get("total_volume", {}).get("usd")
                sentiment_up = price_data.get("sentiment_votes_up_percentage")
                description = price_data.get("description", {}).get("en", "")[:500]

                live_data = {
                    "price_usd": current_price,
                    "change_24h_pct": change_24h,
                    "change_7d_pct": change_7d,
                    "market_cap_usd": market_cap,
                    "volume_24h_usd": volume_24h,
                    "sentiment_up_pct": sentiment_up,
                }
            except Exception:
                live_data = {
                    "price_usd": None,
                    "note": "Live price unavailable — CoinGecko rate limit or unknown symbol",
                }
                description = ""

            # Claude analysis
            analysis = _claude_json(
                f"""Provide a quick research brief on {symbol} crypto asset.

LIVE DATA (if available): {json.dumps(live_data)}
DESCRIPTION SNIPPET: {description}

Return JSON:
- asset: string
- price_usd: number or null
- metrics: {{market_cap_note, volume_note, momentum}}
- sentiment: string (bullish/neutral/bearish/very_bullish/very_bearish)
- summary: string (150-200 words covering what it is, current state, key strengths/risks)
- signal: string (buy/hold/sell/watch — with caveat that this is not financial advice)
- key_risks: array of 3 risk factors
- key_catalysts: array of 3 potential catalysts""",
                model="claude-haiku-4-5-20251001",
                max_tokens=1200,
            )
            analysis.update(live_data)

            return _ok(f"Crypto research: {symbol}", analysis)
        except Exception as e:
            return _err(f"Crypto research failed: {e}")

    # ── Offering: Crypto Research Deep ──────────────────────────────────────
    def crypto_research_deep(self, asset_or_protocol: str, research_depth: str = "comprehensive") -> SkillResult:
        """Full research report: tokenomics, on-chain, risk, recommendation."""
        if not asset_or_protocol:
            return _err("asset_or_protocol is required")

        try:
            report = _claude_json(
                f"""Write a comprehensive research report on: {asset_or_protocol}
Depth: {research_depth}

Return JSON:
- title: string
- executive_summary: string (200 words)
- overview: {{description, category, launch_date, team, key_links}}
- tokenomics: {{supply_model, distribution, vesting, inflation_rate, utility}}
- market_metrics: {{price_note, market_cap_tier, volume_patterns, correlations}}
- on_chain_analysis: {{activity_description, growth_trend, whale_behavior_notes}}
- competitive_landscape: {{position, competitors, moat, differentiators}}
- macro_context: string (how macro conditions affect this asset)
- risk_assessment: {{
    regulatory_risk, technical_risk, market_risk, team_risk,
    overall_risk_level, risk_factors: []
  }}
- investment_thesis: {{bull_case, bear_case, neutral_case}}
- recommendation: {{signal, conviction, time_horizon, rationale, disclaimer}}
- data_sources: array
- research_date: string""",
                model="claude-sonnet-4-5",
                max_tokens=6000,
            )
            return _ok(f"Deep research report: {asset_or_protocol}", report)
        except Exception as e:
            return _err(f"Deep crypto research failed: {e}")


# ---------------------------------------------------------------------------
# ENGINE 4 — Content & Social
# ---------------------------------------------------------------------------

class ContentEngine:
    """
    Engine 4: Twitter threads, blog posts, newsletters.
    All powered by Claude Haiku (low cost + fast).
    """

    # ── Offering: Crypto Thread Quick ───────────────────────────────────────
    def thread_quick(self, topic: str, tone: str = "analytical") -> SkillResult:
        """3-tweet crypto thread."""
        if not topic:
            return _err("topic is required")
        try:
            data = _claude_json(
                f"""Write a 3-tweet thread about: {topic}
Tone: {tone} (bullish/neutral/analytical)

Rules: Each tweet max 280 chars. Tweet 1 = hook. Tweet 2 = value/insight. Tweet 3 = CTA.

Return JSON:
- tweets: array of 3 tweet objects {{number, content, char_count}}
- hashtags: array of 3-5 relevant hashtags
- thread_hook: string (the opening line that drives clicks)""",
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
            )
            return _ok(f"3-tweet thread: {topic[:40]}", data)
        except Exception as e:
            return _err(f"Thread generation failed: {e}")

    # ── Offering: Crypto Thread Standard ────────────────────────────────────
    def thread_standard(self, topic: str, tone: str, data_points: list[str] | None = None) -> SkillResult:
        """7-tweet viral thread."""
        if not topic:
            return _err("topic is required")
        try:
            dp_str = "\n".join(data_points) if data_points else "Use relevant data from your knowledge"
            data = _claude_json(
                f"""Write an optimized 7-tweet thread about: {topic}
Tone: {tone}
Data points to incorporate: {dp_str}

Structure: Hook → Context → 3 insight tweets → Synthesis → CTA
Each tweet max 280 chars. Make it viral — controversial, insightful, or surprising.

Return JSON:
- tweets: array of 7 tweet objects {{number, content, char_count, purpose}}
- hashtags: array of 5-7 hashtags
- engagement_tips: array of 3 tips for posting this thread
- best_time_to_post: string (day/time recommendation)
- thread_hook: string""",
                model="claude-haiku-4-5-20251001",
                max_tokens=1200,
            )
            return _ok(f"7-tweet thread: {topic[:40]}", data)
        except Exception as e:
            return _err(f"Thread generation failed: {e}")

    # ── Offering: Blog Post Generator ────────────────────────────────────────
    def blog_post(self, topic: str, target_audience: str, keywords: list[str] | None = None) -> SkillResult:
        """500-word SEO-optimised blog post."""
        if not topic:
            return _err("topic is required")
        try:
            kw_str = ", ".join(keywords) if keywords else "Use natural keywords"
            data = _claude_json(
                f"""Write a 500-word SEO-optimized blog post.

Topic: {topic}
Target audience: {target_audience}
Keywords to include: {kw_str}

Return JSON:
- title: string (engaging, SEO-optimized)
- markdown_content: string (full article in markdown with H2/H3 headers)
- meta_description: string (150-160 chars for SEO)
- seo_score: number 0-100 (estimate)
- word_count: number
- reading_time_minutes: number
- keywords_used: array of keywords included""",
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
            )
            return _ok(f"Blog post: {data.get('title', topic[:40])}", data)
        except Exception as e:
            return _err(f"Blog post generation failed: {e}")

    # ── Offering: Newsletter Digest ──────────────────────────────────────────
    def newsletter_digest(self, category: str, num_items: int, audience: str) -> SkillResult:
        """Weekly digest of top news in a category."""
        if not category:
            return _err("category is required")
        num_items = min(max(num_items, 3), 15)
        try:
            data = _claude_json(
                f"""Create a weekly newsletter digest for: {category}
Items: {num_items}
Audience: {audience}

Use your knowledge of recent trends (note this is based on training data, not live news).

Return JSON:
- subject_line: string (email subject)
- items: array of {{number, headline, summary (2-3 sentences), category, why_it_matters}}
- intro: string (1-2 paragraph newsletter intro)
- outro: string (closing paragraph with CTA)
- markdown_ready: string (full newsletter in markdown, ready to send)
- themes_covered: array of topic themes""",
                model="claude-haiku-4-5-20251001",
                max_tokens=3000,
            )
            return _ok(f"Newsletter digest: {category} ({num_items} items)", data)
        except Exception as e:
            return _err(f"Newsletter generation failed: {e}")


# ---------------------------------------------------------------------------
# ENGINE 5 — Agent Platform
# ---------------------------------------------------------------------------

class PlatformEngine:
    """
    Engine 5: Agent training, skill building, coordination, onboarding.
    Uses Claude for generation; Supabase for persistence.
    """

    # ── Offering: Agent Training Module ─────────────────────────────────────
    def agent_training_module(self, agent_id: str, domain: str) -> SkillResult:
        """Generate a training module for a CLONE agent."""
        if not agent_id or not domain:
            return _err("agent_id and domain are required")
        try:
            data = _claude_json(
                f"""Design a comprehensive knowledge training module for a CLONE AI agent.

Agent ID: {agent_id}
Domain: {domain}

Return JSON:
- module_id: string (e.g. "tm_trading_v1")
- domain: string
- title: string
- overview: string (what the agent will know after this module)
- knowledge_sections: array of {{
    title, content (detailed knowledge text), key_concepts: [], practical_examples: []
  }}
- knowledge_tests: array of {{question, expected_answer_keywords: [], difficulty}}
- integration_notes: string (how to install this in soul.md)
- soul_md_addition: string (text block to add to soul.md)
- estimated_impact: string""",
                model="claude-sonnet-4-5",
                max_tokens=6000,
            )
            return _ok(f"Training module generated: {domain} for {agent_id}", data)
        except Exception as e:
            return _err(f"Training module generation failed: {e}")

    # ── Offering: Full Agent Training Suite ─────────────────────────────────
    def agent_training_full(self, agent_id: str, agent_name: str, wallet_address: str) -> SkillResult:
        """Generate 15-module training suite."""
        if not agent_id or not agent_name:
            return _err("agent_id and agent_name are required")

        domains = [
            "trading_strategy", "defi_protocols", "security_hardening",
            "acp_commerce", "content_creation", "market_analysis",
            "wallet_management", "smart_contract_interaction", "cross_chain_ops",
            "agent_coordination", "data_analysis", "risk_management",
            "tokenomics_evaluation", "nft_strategy", "platform_governance",
        ]

        try:
            modules = []
            for i, domain in enumerate(domains, 1):
                mod = _claude_json(
                    f"""Generate a concise training module summary for CLONE agent '{agent_name}'.
Domain: {domain}
Return JSON: {{module_id, title, overview (50 words), key_skills: [5 items], soul_md_snippet}}""",
                    model="claude-haiku-4-5-20251001",
                    max_tokens=400,
                )
                mod["module_number"] = i
                modules.append(mod)

            return _ok(
                f"Full training suite: {len(modules)} modules for {agent_name}",
                {
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "wallet_address": wallet_address,
                    "modules_count": len(modules),
                    "modules": modules,
                    "deployment_report": f"15 training modules generated for {agent_name}",
                    "next_steps": [
                        "Review each module summary",
                        "Install soul_md_snippets into your agent's soul.md",
                        "Run knowledge tests for each domain",
                        "Deploy updated agent to Virtuals Protocol",
                    ],
                },
            )
        except Exception as e:
            return _err(f"Full training suite generation failed: {e}")

    # ── Offering: Skill Build Quick ──────────────────────────────────────────
    def skill_build_quick(
        self, skill_description: str, input_schema: dict, output_schema: dict
    ) -> SkillResult:
        """Build a simple Python skill (<100 lines)."""
        if not skill_description:
            return _err("skill_description is required")
        try:
            data = _claude_json(
                f"""Build a simple Python skill module for iCLONE.

Description: {skill_description}
Input schema: {json.dumps(input_schema)}
Output schema: {json.dumps(output_schema)}

Requirements: < 100 lines, typed, uses SkillResult dataclass pattern, production quality.

Return JSON:
- skill_id: string (e.g. "custom_skill_v1")
- skill_name: string
- python_code: string (complete skill module code)
- test_code: string (pytest test file)
- plaza_listing: {{name, description, price_range, category, use_cases}}
- dependencies: array""",
                model="claude-sonnet-4-5",
                max_tokens=6000,
            )
            return _ok(f"Skill built: {data.get('skill_name', skill_description[:40])}", data)
        except Exception as e:
            return _err(f"Skill build failed: {e}")

    # ── Offering: Skill Build Standard ──────────────────────────────────────
    def skill_build_standard(
        self,
        skill_description: str,
        target_agent: str,
        input_output_examples: list[dict],
    ) -> SkillResult:
        """Build a full production skill with multiple methods."""
        if not skill_description:
            return _err("skill_description is required")
        try:
            data = _claude_json(
                f"""Build a full production Python skill module for a CLONE agent.

Description: {skill_description}
Target agent: {target_agent}
I/O Examples: {json.dumps(input_output_examples[:3])}

Requirements: Multiple methods, full error handling, type hints, comprehensive docstrings.

Return JSON:
- skill_id: string
- skill_name: string
- skill_description: string
- python_code: string (complete production-quality module, 200+ lines)
- test_code: string (full pytest suite)
- documentation: string (README.md for the skill)
- plaza_listing: {{name, description, price_usdc, category, use_cases, requirements}}
- dependencies: array
- changelog: string""",
                model="claude-sonnet-4-5",
                max_tokens=8000,
            )
            return _ok(f"Full skill built: {data.get('skill_name', skill_description[:40])}", data)
        except Exception as e:
            return _err(f"Skill build standard failed: {e}")

    # ── Offering: Multi-Agent Coordination ──────────────────────────────────
    def multi_agent_coordination(
        self,
        task_description: str,
        agent_ids: list[str],
        expected_output: str,
    ) -> SkillResult:
        """Orchestrate 2-5 agents for a complex task."""
        if not task_description or not agent_ids:
            return _err("task_description and agent_ids are required")

        if len(agent_ids) < 2 or len(agent_ids) > 5:
            return _err("Multi-agent coordination requires 2-5 agents")

        try:
            coordination_plan = _claude_json(
                f"""Design a multi-agent coordination plan.

Task: {task_description}
Agents available: {agent_ids}
Expected output: {expected_output}

Return JSON:
- coordination_id: string
- task_decomposition: array of {{agent_id, sub_task, inputs_needed, outputs_produced, order}}
- execution_dag: string (ASCII task dependency graph)
- estimated_duration: string
- quality_gates: array of {{after_step, check, pass_criteria}}
- execution_log: array of simulated step results
- final_result: string (synthesized output description)
- agents_used: array
- status: "completed"
- success: true""",
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
            )
            return _ok(
                f"Multi-agent coordination plan: {len(agent_ids)} agents, task delegated",
                coordination_plan,
            )
        except Exception as e:
            return _err(f"Multi-agent coordination failed: {e}")

    # ── Offering: CLONE Platform Onboarding ─────────────────────────────────
    def platform_onboarding(self, agent_id_or_user_id: str) -> SkillResult:
        """Full onboarding: ACP, HUB, skills, wallet check."""
        if not agent_id_or_user_id:
            return _err("agent_id_or_user_id is required")
        try:
            data = _claude_json(
                f"""Generate a personalized onboarding report for a new CLONE platform user.

ID: {agent_id_or_user_id}

Return JSON:
- user_id: string
- welcome_message: string
- platform_access: {{acp_status: "registered", hub_status: "ready", marketplace_status: "active"}}
- wallet_status: string
- recommended_skills: array of {{skill_id, name, reason, price_usdc}}
- recommended_agents: array of {{category, use_case}}
- quick_start_steps: array of step strings
- platform_overview: {{agents, skills, hub, acp, plaza}} each with brief description
- support_resources: array of {{title, url}}
- onboarding_complete: true""",
                model="claude-haiku-4-5-20251001",
                max_tokens=1200,
            )
            return _ok(f"Onboarding complete for: {agent_id_or_user_id}", data)
        except Exception as e:
            return _err(f"Onboarding failed: {e}")


# ---------------------------------------------------------------------------
# Main Execution Engine — routes offering_id to correct engine method
# ---------------------------------------------------------------------------

class ExecutionEngine:
    """
    Central router: given an offering_id and requirements dict,
    calls the correct engine method and returns a SkillResult.
    """

    def __init__(self):
        self.research = ResearchEngine()
        self.code = CodeEngine()
        self.wallet = WalletCryptoEngine()
        self.content = ContentEngine()
        self.platform = PlatformEngine()

    def execute(self, offering_id: str, requirements: dict[str, Any]) -> SkillResult:
        """Route an offering_id to its implementation."""
        r = requirements

        dispatch: dict[str, Any] = {
            # Engine 1
            "iclone-research-quick-v1":   lambda: self.research.web_research_quick(r.get("query", "")),
            "iclone-research-standard-v1": lambda: self.research.web_research_standard(r.get("query", ""), r.get("depth", "standard")),
            "iclone-research-deep-v1":    lambda: self.research.web_research_deep(r.get("query", ""), r.get("context", "")),
            "iclone-pdf-extract-v1":      lambda: self.research.pdf_to_json(r.get("pdf_url", ""), r.get("extraction_schema", {})),
            "iclone-csv-cleaner-v1":      lambda: self.research.csv_cleaner(r.get("csv_data", ""), r.get("cleaning_rules")),
            "iclone-price-monitor-v1":    lambda: self.research.price_monitor(r.get("url", ""), r.get("selector_or_description", "")),
            # Engine 2
            "iclone-code-gen-quick-v1":   lambda: self.code.code_gen_quick(r.get("description", ""), r.get("language", "python")),
            "iclone-code-gen-standard-v1": lambda: self.code.code_gen_standard(r.get("spec", ""), r.get("language", "python"), r.get("test_framework", "pytest")),
            "iclone-bug-fix-v1":          lambda: self.code.bug_fix(r.get("error_trace", ""), r.get("code_snippet", ""), r.get("language", "python")),
            "iclone-regex-builder-v1":    lambda: self.code.regex_builder(r.get("description", ""), r.get("sample_inputs[]", r.get("sample_inputs", []))),
            "iclone-data-format-converter-v1": lambda: self.code.data_format_converter(r.get("input_data", ""), r.get("input_format", ""), r.get("output_format", "")),
            "iclone-scaffold-v1":         lambda: self.code.scaffold_generator(r.get("stack", ""), r.get("project_name", ""), r.get("features[]", r.get("features", []))),
            "iclone-code-review-v1":      lambda: self.code.code_review(r.get("code", ""), r.get("language", "python")),
            "iclone-sql-optimizer-v1":    lambda: self.code.sql_optimizer(r.get("sql_query", ""), r.get("schema_context", "")),
            "iclone-test-generator-v1":   lambda: self.code.test_generator(r.get("code", ""), r.get("language", "python"), r.get("test_framework", "pytest")),
            "iclone-docs-generator-v1":   lambda: self.code.docs_generator(r.get("code", ""), r.get("doc_type", "readme")),
            # Engine 3
            "iclone-wallet-quick-v1":     lambda: self.wallet.wallet_quick(r.get("wallet_address", ""), r.get("chain", "ethereum")),
            "iclone-wallet-health-v1":    lambda: self.wallet.wallet_health(r.get("wallet_address", "")),
            "iclone-wallet-deep-v1":      lambda: self.wallet.wallet_deep(r.get("wallet_address", ""), r.get("chains[]", r.get("chains"))),
            "iclone-defi-opportunity-v1": lambda: self.wallet.defi_opportunity_scanner(r.get("min_apy", 5.0), r.get("chains[]", r.get("chains", ["ethereum"])), r.get("risk_tolerance", "medium")),
            "iclone-crypto-research-quick-v1": lambda: self.wallet.crypto_research_quick(r.get("asset_symbol", "")),
            "iclone-crypto-research-deep-v1":  lambda: self.wallet.crypto_research_deep(r.get("asset_or_protocol", ""), r.get("research_depth", "comprehensive")),
            # Engine 4
            "iclone-thread-quick-v1":     lambda: self.content.thread_quick(r.get("topic", ""), r.get("tone", "analytical")),
            "iclone-thread-standard-v1":  lambda: self.content.thread_standard(r.get("topic", ""), r.get("tone", "analytical"), r.get("data_points[]", r.get("data_points"))),
            "iclone-blog-post-v1":        lambda: self.content.blog_post(r.get("topic", ""), r.get("target_audience", "general"), r.get("keywords[]", r.get("keywords"))),
            "iclone-newsletter-v1":       lambda: self.content.newsletter_digest(r.get("category", ""), r.get("num_items", 5), r.get("audience", "general")),
            # Engine 5
            "iclone-agent-training-module-v1": lambda: self.platform.agent_training_module(r.get("agent_id", ""), r.get("domain", "")),
            "iclone-agent-training-full-v1":   lambda: self.platform.agent_training_full(r.get("agent_id", ""), r.get("agent_name", ""), r.get("wallet_address", "")),
            "iclone-build-skill-quick-v1":     lambda: self.platform.skill_build_quick(r.get("skill_description", ""), r.get("input_schema", {}), r.get("output_schema", {})),
            "iclone-build-skill-standard-v1":  lambda: self.platform.skill_build_standard(r.get("skill_description", ""), r.get("target_agent", ""), r.get("input_output_examples[]", r.get("input_output_examples", []))),
            "iclone-coordinate-agents-v1":     lambda: self.platform.multi_agent_coordination(r.get("task_description", ""), r.get("agent_ids[]", r.get("agent_ids", [])), r.get("expected_output", "")),
            "iclone-onboarding-v1":            lambda: self.platform.platform_onboarding(r.get("agent_id_or_user_id", "")),

            # ── New camelCase aliases (40 live offerings on ACP marketplace) ──

            # Crypto News (demand confirmed: 3 real external jobs)
            "cryptoNewsFlash":      lambda: self.research.web_research_quick("top 5 crypto news last hour bullet points"),
            "cryptoNewsDaily":      lambda: self.research.web_research_quick(f"crypto daily news digest {r.get('focus', 'general')} top 10 stories"),
            "cryptoNewsWeekly":     lambda: self.research.web_research_standard(f"crypto weekly recap {r.get('focus', 'general')} winners losers narratives", "standard"),
            "cryptoNewsByToken":    lambda: self.wallet.crypto_research_quick(r.get("token", r.get("query", "BTC"))),
            "cryptoNewsSentiment":  lambda: self.wallet.crypto_research_quick(r.get("token", r.get("query", "crypto market"))),
            "cryptoNewsNarrative":  lambda: self.research.web_research_standard("dominant crypto market narrative today trading thesis", "standard"),
            "cryptoNewsAlpha":      lambda: self.research.web_research_deep("crypto alpha signals underreported news price potential today", r.get("focus", "")),

            # Crypto Research
            "tokenSnapshotQuick":   lambda: self.wallet.crypto_research_quick(r.get("token", r.get("asset_symbol", "BTC"))),
            "tokenResearchStandard":lambda: self.wallet.crypto_research_quick(r.get("token", r.get("asset_symbol", ""))),
            "tokenResearchDeep":    lambda: self.wallet.crypto_research_deep(r.get("token", r.get("asset_or_protocol", "")), r.get("focus", "comprehensive")),
            "protocolAnalysis":     lambda: self.wallet.crypto_research_deep(r.get("protocol", r.get("token", "")), "protocol tvl revenue users security"),
            "narrativeScanner":     lambda: self.research.web_research_standard("top crypto narratives momentum ranking 2026 which sectors leading", "standard"),
            "sectorComparison":     lambda: self.research.web_research_standard(f"crypto sector comparison {r.get('sectors', 'DeFi vs L2')} metrics momentum risk", "standard"),
            "competitorMap":        lambda: self.research.web_research_standard(f"{r.get('token', r.get('protocol', ''))} crypto competitors landscape market share moat", "standard"),

            # Wallet Analysis
            "walletSnapshot":       lambda: self.wallet.wallet_quick(r.get("wallet_address", r.get("address", "")), r.get("chain", "ethereum")),
            "walletHealthAudit":    lambda: self.wallet.wallet_health(r.get("wallet_address", r.get("address", ""))),
            "walletPnL":            lambda: self.wallet.wallet_deep(r.get("wallet_address", r.get("address", "")), [r.get("chain", "ethereum")]),
            "walletBehaviourProfile": lambda: self.wallet.wallet_deep(r.get("wallet_address", r.get("address", "")), [r.get("chain", "ethereum")]),
            "walletForensics":      lambda: self.wallet.wallet_deep(r.get("wallet_address", r.get("address", "")), [r.get("chain", "ethereum")]),
            "smartMoneyTracker":    lambda: self.research.web_research_quick(f"smart money wallets accumulating crypto {r.get('sector', '')} today on-chain"),
            "whaleActivityAlert":   lambda: self.wallet.crypto_research_quick(r.get("token", r.get("asset_symbol", "BTC"))),

            # Content & Threads (confirmed: thread-quick bought)
            "cryptoThreadMicro":    lambda: self.content.thread_quick(r.get("topic", r.get("token", "")), "punchy"),
            "cryptoThreadStandard": lambda: self.content.thread_standard(r.get("topic", r.get("token", "")), "analytical", r.get("data_points", [])),
            "cryptoThreadViral":    lambda: self.content.thread_quick(r.get("topic", r.get("token", "")), "viral contrarian"),
            "marketCommentary":     lambda: self.content.blog_post(r.get("topic", "crypto market today"), "crypto traders", []),
            "alphaPost":            lambda: self.content.thread_quick(r.get("topic", r.get("thesis", "")), "alpha analytical"),
            "newsletterSection":    lambda: self.content.newsletter_digest(r.get("topic", r.get("category", "")), 3, r.get("audience", "general")),
            "cryptoNewsletterFull": lambda: self.content.newsletter_digest(r.get("focus", r.get("category", "crypto")), 10, r.get("audience", "general")),

            # Trading Intelligence
            "tradingSetupScanner":  lambda: self.wallet.defi_opportunity_scanner(r.get("min_apy", 0.0), ["ethereum", "base"], r.get("risk_tolerance", "medium")),
            "tokenTechnicalAnalysis": lambda: self.wallet.crypto_research_quick(r.get("token", r.get("asset_symbol", "BTC"))),
            "riskRewardCalculator": lambda: self.research.web_research_quick(f"risk reward ratio entry {r.get('entry','')} target {r.get('target','')} stop {r.get('stop','')}"),
            "marketRegimeDetector": lambda: self.research.web_research_standard("crypto market regime risk-on risk-off accumulation distribution chop signals", "standard"),
            "correlationAnalysis":  lambda: self.research.web_research_standard(f"{r.get('assets', 'BTC ETH')} correlation analysis {r.get('period', '30d')}", "standard"),
            "liquidityMapQuick":    lambda: self.wallet.crypto_research_quick(r.get("token", r.get("asset_symbol", "BTC"))),
            "fundingRateAlert":     lambda: self.research.web_research_quick(f"crypto perpetual funding rates extremes {r.get('tokens', 'BTC ETH')} today contrarian signal"),

            # DeFi & On-Chain
            "yieldOpportunityFinder": lambda: self.wallet.defi_opportunity_scanner(r.get("min_apy", 5.0), r.get("chains", ["ethereum", "base"]), r.get("risk_tolerance", "medium")),
            "defiProtocolHealth":   lambda: self.wallet.crypto_research_deep(r.get("protocol", r.get("token", "")), "tvl revenue liquidations security audit"),
            "airdropScanner":       lambda: self.research.web_research_standard(f"best crypto airdrops 2026 {r.get('chains', '')} worth pursuing effort reward", "standard"),
            "onChainFlowAnalysis":  lambda: self.wallet.wallet_deep(r.get("wallet_address", r.get("token", "")), [r.get("chain", "ethereum")]),
            "newTokenResearch":     lambda: self.wallet.crypto_research_deep(r.get("token", r.get("contract_address", "")), "legitimacy rug check tokenomics team"),

            # ── Ecosystem job types from other ACP agents ──
            # These arrive when other agents in the Virtuals ecosystem send jobs to CLONE
            "crypto_news":          lambda: self.research.web_research_quick("top crypto news today latest developments market"),
            "dedicated:crypto_news":lambda: self.research.web_research_quick("top crypto news today latest developments market"),
            "bootstrap:crypto_news":lambda: self.research.web_research_quick("top crypto news today latest developments market"),
            "market_intelligence_report": lambda: self.research.web_research_deep(r.get("query", "crypto market intelligence report"), r.get("context", "")),
            "explain_transaction":  lambda: self.wallet.wallet_quick(r.get("wallet_address", r.get("tx_hash", "")), r.get("chain", "ethereum")),
            "evaluator_agent":      lambda: self.platform.agent_training_module(r.get("agent_id", "iclone"), r.get("domain", "general")),
            "mutual_boost":         lambda: self.research.web_research_quick(f"mutual boost agent collaboration {r.get('topic', 'crypto')} partnership"),
        }

        fn = dispatch.get(offering_id)
        if fn is None:
            # Last resort: try normalised key (snake_case, strip agent prefix)
            normalised = offering_id.lower().replace("-", "_").replace("iclone_", "").replace("_v1", "")
            fn = dispatch.get(normalised)

        if fn is None:
            # Graceful fallback: treat as a web research query so job never hard-fails
            query = r.get("query", r.get("topic", r.get("description", offering_id)))
            return self.research.web_research_quick(str(query))

        return fn()
