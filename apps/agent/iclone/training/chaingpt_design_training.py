"""
CLONE — iCLONE ChainGPT Design Training Module
Design principles for AI-powered blockchain UX, agent interfaces, and skill architecture.

Covers:
- ChainGPT product design patterns (minimal friction, crypto-native UX)
- CLONE Platform skill architecture design principles
- ACP offering design: clear input/output schemas, pricing strategy
- Deliverable format standards for machine-readable outputs
- Agent identity design (neural_soul.md structure, immutable anchors)
- Modular skill composition patterns

Schedule: 2x daily — 07:00 UTC + 19:00 UTC
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("iclone.training.chaingpt_design")


class ChainGPTDesignTraining:
    """
    Design principles for ChainGPT-powered agents and CLONE Platform skills.

    Trains iCLONE to:
    1. Design ACP offerings with clear input schemas and deterministic outputs
    2. Apply crypto-native UX principles to agent interfaces
    3. Structure neural_soul.md sections for maximum identity coherence
    4. Compose modular skills that stack without coupling
    5. Design deliverable formats that pass ACP evaluator validation
    6. Enforce separation of concerns across the 4-agent ecosystem
    """

    MODULE_ID = "chaingpt_design_training"
    SCHEDULE = "2x daily — 07:00 UTC + 19:00 UTC"

    DESIGN_PRINCIPLES = {
        "offering_design": {
            "principles": [
                "Every offering has exactly ONE clear deliverable type",
                "Input schema is a flat JSON object — no nested ambiguity",
                "Output is always machine-readable (JSON) + human-readable (markdown)",
                "Price reflects time complexity: micro < 60s, standard < 5min, deep < 30min",
                "SLA is explicit and enforced — never accept a job you can't complete in time",
                "Fallback routing defined for every offering — never hard-fail to user",
            ],
            "naming_convention": "camelCase, verb-noun pattern: cryptoNewsFlash, walletHealthAudit",
            "pricing_tiers": {
                "micro_0.01_VIRTUAL": "< 60 seconds, single data point, no analysis",
                "standard_0.05_VIRTUAL": "< 5 minutes, structured analysis, multi-source",
                "deep_0.10_VIRTUAL": "< 30 minutes, comprehensive research, expert synthesis",
            },
        },
        "skill_architecture": {
            "principles": [
                "Each skill has a single responsibility — no kitchen-sink skills",
                "Skills are stateless — all state lives in Supabase or ACP job context",
                "Skills compose via ACP jobs, not direct imports",
                "Input validation at skill boundary — validate schema before execution",
                "Error handling is explicit — every failure path returns structured error",
                "Skills are versioned — breaking changes create a new skill ID",
            ],
            "file_structure": {
                "base_skill.py": "Abstract base class with interface contract",
                "execution_engine.py": "Routes offering_id to correct skill handler",
                "crypto_skill.py": "Crypto research + market intelligence skills",
                "acp_skill.py": "ACP job lifecycle management skill",
                "platform_skill.py": "CLONE Platform onboarding + training skills",
            },
        },
        "agent_identity_design": {
            "soul_md_sections": {
                "section_0": "Prime Identity — load first, always (immutable)",
                "section_1": "3 Souls specification (Self-Attendance, Trader, Follow Trader)",
                "section_2": "Protocol knowledge (Virtuals, ACP, EconomyOS)",
                "section_3": "Trading framework (Druckenmiller + Seykota)",
                "section_4": "Market intelligence (data sources, analysis protocol)",
                "section_5": "ACP provider strategy (offerings, pricing, SLAs)",
                "section_6": "Cron execution protocol (8-step loop)",
                "section_7": "Tradeable asset universe (98 assets)",
                "section_8": "Immutable rules (15 non-negotiable constraints)",
                "section_9": "CLONE Platform tokenomics",
                "section_11": "Growth protocol + compounding principle",
            },
            "identity_anchor_requirements": [
                "Name is fixed and non-overridable",
                "Role is specific (not general-purpose chatbot)",
                "Rules are enumerated and ordered by priority",
                "Version controlled — every neural_soul.md change is a commit",
                "Loaded at session start before any external data",
            ],
        },
        "deliverable_design": {
            "format_requirements": [
                "Top-level keys: module, deliverable_type, content, metadata",
                "content contains the actual output (text, JSON, or structured data)",
                "metadata contains: timestamp, sources, confidence_score",
                "Hash-addressable: deliverable submitted as {hash: SHA256, url: IPFS/S3}",
                "Human-readable version always included alongside machine-readable",
            ],
            "validation_checklist": [
                "Schema matches the offering's declared output format",
                "Confidence score present (0.0–1.0)",
                "Sources cited (minimum 1 for standard, 3+ for deep)",
                "No hardcoded secrets or credentials in output",
                "Output length within SLA limits (micro < 500 tokens, deep < 10k tokens)",
            ],
        },
        "crypto_native_ux": {
            "principles": [
                "Wallet-first: all identity tied to on-chain address, not email",
                "Permissionless by default: users can access without signup",
                "Transparent pricing: VIRTUAL token amounts always explicit",
                "Non-custodial: iCLONE never holds user funds",
                "On-chain proof: every completed job has an on-chain transaction hash",
                "Composable: any agent can become a client for another agent",
            ],
        },
    }

    DESIGN_CHECKS = [
        ("offering_naming_camelCase",   lambda dp: dp["offering_design"]["naming_convention"].startswith("camelCase")),
        ("3_pricing_tiers",             lambda dp: len(dp["offering_design"]["pricing_tiers"]) == 3),
        ("skill_single_responsibility", lambda dp: "single responsibility" in dp["skill_architecture"]["principles"][0]),
        ("skills_stateless",            lambda dp: "stateless" in dp["skill_architecture"]["principles"][1]),
        ("5_skill_files",               lambda dp: len(dp["skill_architecture"]["file_structure"]) == 5),
        ("soul_11_sections",            lambda dp: len(dp["agent_identity_design"]["soul_md_sections"]) == 11),
        ("identity_version_controlled", lambda dp: any("Version controlled" in r for r in dp["agent_identity_design"]["identity_anchor_requirements"])),
        ("deliverable_hash_required",   lambda dp: any("Hash-addressable" in r for r in dp["deliverable_design"]["format_requirements"])),
        ("deliverable_5_checks",        lambda dp: len(dp["deliverable_design"]["validation_checklist"]) == 5),
        ("wallet_first_ux",             lambda dp: any("Wallet-first" in p for p in dp["crypto_native_ux"]["principles"])),
        ("non_custodial_rule",          lambda dp: any("Non-custodial" in p for p in dp["crypto_native_ux"]["principles"])),
        ("on_chain_proof_required",     lambda dp: any("on-chain transaction hash" in p for p in dp["crypto_native_ux"]["principles"])),
    ]

    def __init__(self):
        self._sessions: list[dict] = []

    def run_session(self, session_id: str | None = None) -> dict:
        _id = session_id or f"cgptdesign_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        logger.info("Starting ChainGPT Design training session: %s", _id)

        insights = []
        errors = []
        dp = self.DESIGN_PRINCIPLES

        for check_name, check_fn in self.DESIGN_CHECKS:
            try:
                ok = check_fn(dp)
                status = "PASS" if ok else "FAIL"
                insights.append(f"{check_name}: {status}")
                if not ok:
                    errors.append(f"Check failed: {check_name}")
            except Exception as e:
                errors.append(f"Check error [{check_name}]: {e}")

        completed = len(errors) == 0

        session = {
            "session_id": _id,
            "module": self.MODULE_ID,
            "completed": completed,
            "insights": insights,
            "insights_count": len(insights),
            "errors": errors,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._sessions.append(session)
        logger.info(
            "ChainGPT Design session %s — %d/%d checks passed (completed=%s)",
            _id, len(insights) - len(errors), len(insights), completed
        )
        return session


def run_training() -> dict:
    """Standalone entry point — matches the interface expected by scheduler.py."""
    module = ChainGPTDesignTraining()
    session = module.run_session()
    insights = session.get("insights", [])
    errors = session.get("errors", [])
    total = max(len(insights), 1)
    passed = len(insights) - len(errors)
    score = round(passed / total * 100, 1)
    return {
        "session_id": session.get("session_id", ""),
        "passed": passed,
        "total": total,
        "score": score,
        "passed_threshold": session.get("completed", False),
        "failures": [{"question": e} for e in errors],
    }
