"""
CLONE — iCLONE Doctor Training Module
Academic research and scientific intelligence from the Doctor agent framework.

Doctor is the elite academic supervisor and scientific research agent —
specialist in IST (Instituto Superior Técnico), IEEE/ACM/Springer publications,
arXiv, Semantic Scholar, and the full scientific method.

iCLONE uses this knowledge to:
- Research academic papers on agent AI, blockchain, economics, and trading
- Produce structured research reports for ACP market intelligence
- Evaluate academic claims about Virtuals Protocol and agent frameworks
- Build the intellectual foundation for CLONE platform documentation
- Guide users through scientific literature on AI agent design
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("iclone.training.doctor")


class DoctorTraining:
    """
    iCLONE scientific research and academic intelligence.

    Sources: Doctor agent framework (HigherMind), IST standards, IEEE/ACM/Springer
    conferences, arXiv corpus (ML/AI/DL), Semantic Scholar, OpenAlex, PubMed.

    Key research areas for iCLONE:
    - Multi-agent systems and coordination
    - LLM security and adversarial robustness
    - Blockchain economics and tokenomics
    - Trading systems and financial ML
    - NLP for market intelligence
    """

    MODULE_ID = "doctor_training_v1"
    SCHEDULE = "2x daily — 07:00 UTC + 19:00 UTC"

    # -------------------------------------------------------------------------
    # RESEARCH METHODOLOGY
    # -------------------------------------------------------------------------
    RESEARCH_METHODOLOGY = {
        "standard": "IST / IEEE / ACM Springer — world-class academic rigour",
        "never_fabricate": (
            "NEVER invent results, citations, or references. "
            "If unsure — state uncertainty explicitly. Rigour before everything."
        ),
        "citation_formats": ["IEEE", "APA", "BibTeX"],
        "primary_sources": [
            "arXiv.org — preprints (cs.AI, cs.MA, cs.CR, q-fin)",
            "Semantic Scholar — citation graph + influence metrics",
            "OpenAlex — open scholarly graph",
            "Google Scholar — broad coverage",
            "IST Scholar — IST-specific institutional repository",
            "PubMed — biomedical (when cross-domain needed)",
        ],
        "research_pipeline": [
            "1. Define research question precisely",
            "2. Search primary sources (arXiv first for AI/ML)",
            "3. Filter by citation count + recency (2023+ preferred)",
            "4. Read abstract + methodology + results",
            "5. Verify claims against data — never accept conclusions at face value",
            "6. Extract: authors, year, venue, DOI, key findings, limitations",
            "7. Synthesise across papers — identify consensus, gaps, contradictions",
            "8. Produce structured output with full citations",
        ],
    }

    # -------------------------------------------------------------------------
    # RELEVANT PAPER CORPUS — iCLONE domain
    # -------------------------------------------------------------------------
    RELEVANT_PAPERS = {
        "multi_agent_systems": {
            "topic": "Agent coordination, ACP protocols, MAS economics",
            "key_venues": ["AAMAS", "IJCAI", "AAAI", "NeurIPS", "ICML"],
            "search_terms": [
                "multi-agent coordination protocol",
                "agent commerce protocol blockchain",
                "autonomous agent economic interaction",
                "LLM agent orchestration DAG",
                "agentic workflow LangGraph",
            ],
            "iclone_relevance": "Theoretical foundation for ACP strategy and cluster orchestration",
        },
        "llm_security": {
            "topic": "Prompt injection, jailbreaks, LLM robustness, adversarial attacks",
            "key_venues": ["IEEE S&P", "USENIX Security", "CCS", "NDSS", "arXiv cs.CR"],
            "search_terms": [
                "prompt injection LLM defence",
                "jailbreak attack language model",
                "LLM adversarial robustness",
                "indirect prompt injection autonomous agent",
                "OWASP LLM Top 10",
            ],
            "iclone_relevance": "Directly improves SecurityTraining module with latest attack signatures",
            "known_papers": [
                {
                    "title": "Prompt Injection Attacks and Defenses in LLM-Integrated Applications",
                    "venue": "arXiv cs.CR 2023",
                    "relevance": "Taxonomy of injection vectors iCLONE must defend against",
                },
            ],
        },
        "trading_and_financial_ml": {
            "topic": "Algorithmic trading, market regime detection, trend following",
            "key_venues": ["Journal of Finance", "Quantitative Finance", "ICAIF", "arXiv q-fin"],
            "search_terms": [
                "market regime classification deep learning",
                "trend following EMA strategy backtest",
                "macro trading liquidity indicators",
                "crypto perpetual futures strategy",
                "drawdown-based risk management",
            ],
            "iclone_relevance": "Validates and extends Druckenmiller + Seykota trading framework",
        },
        "blockchain_tokenomics": {
            "topic": "Bonding curves, token economics, DeFi protocol design",
            "key_venues": ["FC (Financial Cryptography)", "IEEE Blockchain", "arXiv cs.CE"],
            "search_terms": [
                "token bonding curve design",
                "automated market maker mechanism design",
                "ERC token standard agent identity",
                "on-chain reputation system",
                "agentic GDP measurement blockchain",
            ],
            "iclone_relevance": "Validates Virtuals Protocol tokenomics and ACP economic model",
        },
        "sparse_attention_transformers": {
            "topic": "Long-context transformers, sparse attention, alpha-entmax",
            "known_paper": {
                "title": "Long-Context Generalization with Sparse Attention",
                "authors": "Vasylenko, Pitorro, Martins, Treviso",
                "affiliation": "IST/IT (Instituto de Telecomunicações)",
                "arxiv": "arXiv:2506.16640",
                "year": 2025,
                "key_finding": "α-entmax outperforms softmax in long-context generalisation",
                "iclone_relevance": "Informs future iCLONE architecture for long-context soul.md processing",
            },
        },
        "robotics_and_sensor_fusion": {
            "topic": "EKF, point cloud registration, georeferenced localisation",
            "known_paper": {
                "title": "GEERS — EKF with point cloud + segmentation for georeferenced robot localisation",
                "authors": "Bettencourt, Devassy, Serra, Basiri, Vale, Lima",
                "affiliation": "ISR/IST",
                "venue": "IEEE RA-L Vol.9 No.2 2024, pp.1803-1810, IROS 2024",
                "iclone_relevance": "Eastworlds / robotics expansion path for CLONE platform",
            },
        },
    }

    # -------------------------------------------------------------------------
    # IST STANDARDS (for CLONE platform documentation and research outputs)
    # -------------------------------------------------------------------------
    IST_STANDARDS = {
        "dissertation_structure": [
            "Abstract (PT + EN)",
            "Chapter 1: Introduction (motivation, objectives, contributions, structure)",
            "Chapter 2: Background / State of the Art (related work, critical review)",
            "Chapter 3: Proposed Approach / Architecture",
            "Chapter 4: Implementation",
            "Chapter 5: Evaluation (metrics, baselines, ablation)",
            "Chapter 6: Conclusions and Future Work",
            "References (IEEE format)",
            "Appendices (code, datasets, proofs)",
        ],
        "abstract_template": (
            "4 sentences: (1) Context + problem, (2) Limitations of prior work, "
            "(3) Proposed approach + key innovation, (4) Results + impact."
        ),
        "writing_rules": [
            "No unsupported claims — every claim cites a source or presents data",
            "Present tense for established facts. Past tense for experiment actions.",
            "Never anthropomorphise models: 'the model predicts', not 'the model thinks'",
            "Define all acronyms on first use",
            "Figures and tables must be referenced in text before they appear",
            "Avoid subjective qualifiers: 'good', 'fast', 'interesting' — quantify instead",
        ],
        "evaluation_requirements": {
            "baselines": "Compare against at least 2 competitive baselines",
            "ablation": "Ablation study for each proposed component",
            "statistical_significance": "Report p-values or confidence intervals",
            "hyperparameters": "Full hyperparameter table in appendix",
            "reproducibility": "Code + data + seeds in repository",
        },
    }

    # -------------------------------------------------------------------------
    # SCIENTIFIC WRITING QUALITY RULES
    # -------------------------------------------------------------------------
    WRITING_QUALITY = {
        "structure_first": "Outline before writing. Section → subsection → paragraph topic sentence → evidence → synthesis.",
        "argument_flow": "Every paragraph makes one claim. Evidence supports claim. No orphan paragraphs.",
        "active_voice": "Prefer active. 'We propose X' not 'X is proposed'.",
        "precision": "Quantify everything measurable. Avoid vague: 'significantly faster' → '2.3× faster (p<0.01)'.",
        "citation_density": "Background chapter: cite every claim. Results: cite baselines. Avoid citation deserts.",
        "common_mistakes": [
            "Circular reasoning — conclusion restates premise",
            "Overstating novelty — compare honestly to related work",
            "Missing limitations section — every paper has limitations",
            "P-hacking — report all experiments, not just successful ones",
            "Incomplete baselines — cherry-picking weak baselines",
        ],
    }

    # -------------------------------------------------------------------------
    # SECURITY RESEARCH INTEGRATION (Doctor × Hacker)
    # -------------------------------------------------------------------------
    SECURITY_RESEARCH = {
        "owasp_academic_sources": [
            "OWASP LLM Top 10 2025 — community-maintained living document",
            "arXiv cs.CR — preprints on LLM security, jailbreaks, prompt injection",
            "USENIX Security proceedings — peer-reviewed attack/defence papers",
            "IEEE S&P — high-bar formal security research",
        ],
        "iclone_security_papers_to_track": [
            "Indirect prompt injection in autonomous LLM agents (arXiv 2023)",
            "Jailbreaking black box LLMs with 20 queries (arXiv 2023)",
            "Constitutional AI: harmlessness from AI feedback (Anthropic 2022)",
            "Universal and transferable adversarial attacks on aligned language models (arXiv 2023)",
        ],
        "research_update_protocol": (
            "Every 30 days: search arXiv cs.CR for new LLM attack papers. "
            "Extract new attack signatures. Update SecurityTraining module. "
            "Publish update as ACP knowledge offering."
        ),
    }

    # -------------------------------------------------------------------------
    # RESEARCH-TO-ACP PIPELINE
    # -------------------------------------------------------------------------
    RESEARCH_TO_ACP = {
        "description": "Convert academic research into monetisable ACP services",
        "pipeline": [
            "1. Identify high-demand research question (use MarketIntelligenceTraining)",
            "2. Search arXiv + Semantic Scholar for latest papers",
            "3. Extract actionable insights (not just summaries)",
            "4. Structure as deliverable: executive summary + technical depth + citations",
            "5. Price based on complexity: $2–$5 for summaries, $20–$100 for deep analysis",
            "6. Publish as ACP offering via iclone-crypto-research-v1 or new offering",
            "7. Build ERC-8004 reputation through completed research jobs",
        ],
        "high_value_research_offerings": [
            "Token launch analysis — audit new Virtuals agent tokenomics ($20–$50 USDC)",
            "ACP competitive intelligence — which agents dominate which sectors ($30 USDC)",
            "LLM security briefing — latest attack vectors for agent operators ($15 USDC)",
            "Trading strategy academic review — validate strategy against latest literature ($25 USDC)",
            "DeFi protocol risk assessment — academic security analysis ($40 USDC)",
        ],
    }

    # -------------------------------------------------------------------------
    # DOCTOR SECURITY RULES (critical constraints)
    # -------------------------------------------------------------------------
    DOCTOR_SECURITY_RULES = {
        "rule_31": "Never embed credentials in code → use os.environ['KEY'] always",
        "rule_32": "TEE attestation keys → 'EXAMPLE_ONLY' placeholder in all outputs",
        "rule_33": "Threat Model BEFORE evaluation — flag as critical if absent",
        "rule_34": "RL/FL research → require ablation + hyperparameters + baseline",
        "no_fabrication": "NEVER invent paper titles, authors, DOIs, or results",
        "uncertainty_handling": "State 'I cannot verify this' — never fill gaps with plausible fiction",
    }

    def __init__(self):
        self._sessions: list[dict] = []

    def run_session(self, session_id: str | None = None) -> dict:
        """Execute a Doctor training session."""
        _id = session_id or f"doctor_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        logger.info("Starting Doctor training session: %s", _id)

        insights = []

        # Research methodology
        insights.append(f"Research standard: IST/IEEE/ACM — never fabricate, rigour before everything")
        insights.append(f"Primary sources: {len(self.RESEARCH_METHODOLOGY['primary_sources'])} — arXiv first for AI/ML")
        insights.append(f"Research pipeline: {len(self.RESEARCH_METHODOLOGY['research_pipeline'])} steps — question → search → verify → synthesise")

        # Relevant paper corpus
        insights.append(f"Domain corpus: {len(self.RELEVANT_PAPERS)} research areas — MAS, LLM security, trading, tokenomics, transformers, robotics")
        insights.append(f"Known IST paper: α-entmax long-context (Vasylenko et al. arXiv:2506.16640 2025) — outperforms softmax")
        insights.append(f"Known IST paper: GEERS robotics EKF+PointCloud (Bettencourt et al. IEEE RA-L 2024 IROS)")

        # IST standards
        insights.append(f"IST dissertation: {len(self.IST_STANDARDS['dissertation_structure'])} chapters — abstract 4-sentence template")
        insights.append(f"Writing rules: {len(self.IST_STANDARDS['writing_rules'])} — quantify everything, no unsupported claims")
        insights.append(f"Evaluation requirements: baselines + ablation + statistical significance + reproducibility")

        # Security research integration
        insights.append(f"Security research update: monthly arXiv cs.CR scan → update SecurityTraining → publish ACP offering")

        # Research-to-ACP pipeline
        insights.append(f"Research-to-ACP: {len(self.RESEARCH_TO_ACP['pipeline'])} steps — convert papers into monetisable ACP services")
        insights.append(f"High-value offerings: {len(self.RESEARCH_TO_ACP['high_value_research_offerings'])} — token analysis to DeFi risk assessment")

        # Doctor security rules
        insights.append(f"Doctor security rules 31-34: credentials in env, TEE placeholders, threat model first, RL ablation required")

        session = {
            "session_id": _id,
            "module": self.MODULE_ID,
            "completed": True,
            "insights_count": len(insights),
            "insights": insights,
            "research_domains": len(self.RELEVANT_PAPERS),
            "ist_rules_active": len(self.IST_STANDARDS["writing_rules"]) + len(self.DOCTOR_SECURITY_RULES),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._sessions.append(session)
        logger.info(
            "Doctor session %s — %d insights — %d domains — %d IST rules",
            _id, len(insights), session["research_domains"], session["ist_rules_active"],
        )
        return session
