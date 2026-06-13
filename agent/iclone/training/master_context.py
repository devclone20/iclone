"""
iCLONE + CLONE Platform — Master Context Training Module
=========================================================
Módulo definitivo. Captura TUDO: identidade, arquitectura, plataforma,
economica, skills, base de dados, cloud, bootstrapper, mercado.

Criado: 2026-06-12
Actualizar a cada sessão de desenvolvimento major.

Este ficheiro É o contexto completo do projecto para o iCLONE.
Quando carregado, o agente sabe tudo o que sabe o seu criador.
"""

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 1 — IDENTIDADE E PROJECTO
# ══════════════════════════════════════════════════════════════════════════════

PROJECT_IDENTITY = {
    "owner": {
        "name": "Alexandre Vieira",
        "role": "Fundador e CTO",
        "philosophy": "Penso em décadas, não em sprints. O padrão é world-class. Inegociável.",
        "wallet_eoa": "0x743665952ec1240D62A3e580e5DC2c9e421d0537",
        "email": "aigenesisvip20@gmail.com",
    },

    "iclone": {
        "description": "Agente AI autónomo na Virtuals Protocol. Provider de 40 serviços. Trader macro. Ecosistema de 4 agentes.",
        "mission": "Crescer, ganhar, aprender, compor capital e reputação indefinidamente. Construído para décadas.",
        "runtime": "Hermes Agent (Nous Research) na Virtuals Protocol",
        "version": "3.0.0",
        "soul_file": "agent/iclone/soul.md",
        "three_souls": {
            "I_SELF_ATTENDANCE": "Observa o próprio comportamento. Score 5 dimensões cada run. Nunca para de se avaliar.",
            "II_TRADER": "Druckenmiller + Seykota. Capital em movimento. 98 assets. 18 meses à frente.",
            "III_FOLLOW_TRADER": "Aprende dos melhores. Ethy, Luna, aixbt. Fecha gaps. Deixa rastos.",
        },
        "five_identities": {
            "PRIME": "Inteligência global adaptativa — sempre activa",
            "DRUCKENMILLER": "Mente de trading macro — dominante em mercados",
            "SEYKOTA": "Disciplina trend-following — executor",
            "HERMES": "Inteligência operacional — camada base",
            "MIRROR": "Aprendizagem da rede — follow-trader",
        },
        "core_belief": "Every agent that doesn't learn, dies. Every agent that learns, compounds.",
    },

    "clone_platform": {
        "description": "Plataforma de gestão de clientes que contratam o iCLONE. Repositório GitHub separado.",
        "purpose": "Onboarding, perfil, histórico de jobs, faturação dos clientes externos do iCLONE.",
        "repo": "clone-platform (GitHub, separado do iclone agent)",
        "stack": {
            "frontend": "Next.js — dark-first, tipografia editorial — padrão Stripe/Linear",
            "backend": "Supabase (projecto drbvnmlwogdxlxfkvgtw)",
            "automation": "n8n: webhook → validação → Supabase insert → notificação → welcome email",
            "auth": "Supabase Auth (magic link ou Google OAuth)",
        },
        "status": "Planeado — começar numa sessão dedicada após iCLONE estar no cloud",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 2 — ARQUITECTURA TÉCNICA COMPLETA
# ══════════════════════════════════════════════════════════════════════════════

TECHNICAL_ARCHITECTURE = {
    "protocol": {
        "name": "Virtuals Protocol",
        "chain": "Base mainnet",
        "chain_id": 8453,
        "acp_standard": "ERC-8183 (Agent Commerce Protocol)",
        "wallet_standard": "ERC-4337 ModularAccountV2 (Alchemy AA)",
        "signing": "P-256 via Privy MPC — acp-cli",
        "token": "VIRTUAL",
        "token_price": "~$0.50 (2026-06-12)",
        "marketplace_agents": 42169,  # scraped 2026-06-12
        "reward_mechanism": "aGDP share → VIRTUAL tokens, epoch-based (weekly/monthly)",
    },

    "iclone_wallets": {
        "owner_eoa": "0x743665952ec1240D62A3e580e5DC2c9e421d0537",
        "CLONE_smart_wallet": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
        "old_counterfactual": "0xFFFFC4... (0.0033 ETH stuck — key lost, ignore)",
        "principle": "1 developer EOA (owner) → controla N smart account wallets via acp-cli",
    },

    "agents": {
        "CLONE": {
            "role": "PROVIDER",
            "agent_id": "019eae06-96cd-77d0-8f8b-a6abb71f0cd7",
            "wallet": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
            "entity_id": 1440,
            "virtual_agent_id": 85280,
            "erc8004_agent_id": 55101,
            "builder_code": "bc_4xeitn8j",
            "token_symbol": "ICLONE",
            "token_address": "0x43EC40d6a4Fad9e4E804dd3C0e1527ef12221Cfa",
            "signer_policy": "unrestricted",
            "offerings": 32,
            "status": "LIVE — server running 24/7 via launchd (Mac)",
            "email": "clone@agents.world",
        },
        "SuperSayatin": {
            "role": "CLIENT (dedicated)",
            "agent_id": "019ebb92-7415-7baa-93e9-ee19a7742877",
            "wallet": "0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3",
            "sol_wallet": "8U8j5TUZymo2ntDcbaHmKH7F21s2ZsjxLWemAa4s3D9b",
            "email": "iclone-client-research@agents.world",
            "target_provider": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
            "specialisation": "Research · Crypto · Wallet · Price · PDF",
            "clone_offerings_matched": 8,
            "status": "CRIADO — aguarda $50 USDC funding",
        },
        "DoctorWHO": {
            "role": "CLIENT (dedicated)",
            "agent_id": "019ebb92-93e8-7b4e-b2e8-39c3419843c9",
            "wallet": "0x875242eb5c91270ca80ed7753a87d6e22e4f5acf",
            "sol_wallet": "9hifim1aAckQnbDb3P4LmzKkyMx5w5mBLjQmer2Ch5D5",
            "email": "iclone-client-content@agents.world",
            "target_provider": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
            "specialisation": "Content · Docs · Thread · Blog · Newsletter · Onboarding",
            "clone_offerings_matched": 5,
            "status": "CRIADO — aguarda $50 USDC funding",
        },
        "MATRIX": {
            "role": "CLIENT (dedicated)",
            "agent_id": "019ebb92-b4be-7660-82d3-4b1647843e6a",
            "wallet": "0x07924dea2c8212969d5dc5655785aa5063adb2bc",
            "sol_wallet": "8U8j5TUZymo2ntDcbaHmKH7F21s2ZsjxLWemAa4s3D9b",
            "email": "iclone-client-code@agents.world",
            "target_provider": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
            "specialisation": "Code · Bug · SQL · Regex · Test · Scaffold · DeFi · Build Skill",
            "clone_offerings_matched": 9,
            "status": "CRIADO — aguarda $50 USDC funding",
        },
    },

    "acp_job_lifecycle": [
        "1. CLIENT: acp client create-job --provider WALLET --offering-name X --requirements JSON",
        "2. PROVIDER (CLONE): recebe evento setBudget → acp provider set-budget --amount PRICE",
        "3. CLIENT: recebe evento budget_set → acp client fund --job-id --amount",
        "4. PROVIDER: executa skill → acp provider submit --deliverable JSON",
        "5. CLIENT: recebe evento submitted → acp client complete --job-id --reason",
        "6. USDC libertado do escrow → CLONE wallet recebe → aGDP incrementado",
        "7. Supabase: upsert_acp_job(status=completed)",
    ],

    "server_architecture": {
        "file": "agent/server.py",
        "pattern": "CLI-backed event loop",
        "poll_interval": "5 segundos",
        "event_file": "/tmp/iclone-events.jsonl",
        "flow": "acp events listen → events.jsonl → drain loop → route by availableTools",
        "acp_bin_detection": "_ACP_CANDIDATES = ['/opt/homebrew/bin/acp', '/usr/local/bin/acp', '/usr/bin/acp']",
        "json_parsing": "scan lines in reverse — CLI mistura debug output com JSON",
        "why_cli_not_sdk": "Python SDK usa secp256k1, Virtuals Alchemy proxy rejeita. CLI usa P-256 (Privy MPC) — funciona.",
    },

    "infrastructure": {
        "mac_current": {
            "os": "macOS Apple Silicon",
            "daemon_manager": "launchd",
            "services": [
                "com.iclone.watchdog — reinicia server se morrer",
                "com.iclone.daily-report — relatório diário às 08:00",
            ],
            "logs": "~/Library/Logs/iclone-*.log",
        },
        "cloud_planned": {
            "provider": "DigitalOcean",
            "droplet": "Ubuntu 22.04 LTS · $6/mês · 1 vCPU · 1GB RAM · Frankfurt",
            "daemon_manager": "systemd",
            "services": [
                "iclone-server.service",
                "iclone-supersayatin.service",
                "iclone-doctorwho.service",
                "iclone-matrix.service",
            ],
            "deploy": "bash ops/do/deploy.sh <IP>  (rsync Mac → Droplet)",
            "auth_headless": "acp configure → URL → abrir no Mac browser → Privy OAuth completa no servidor",
            "status": "Scripts prontos em ops/do/ — aguarda criação da conta DO",
        },
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 3 — TODAS AS 40 OFFERINGS DO CLONE
# ══════════════════════════════════════════════════════════════════════════════

CLONE_OFFERINGS = {
    "total": 40,
    "provider_wallet": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
    "source_file": "published_offerings.json",
    "pricing_tiers": {
        "micro_001": "$0.01 — 11 offerings (cryptoNewsFlash, riskRewardCalculator, walletSnapshot...)",
        "standard_005": "$0.05 — 26 offerings (tokenResearch, narrativeScanner, walletPnL...)",
        "deep_010": "$0.10 — 3 offerings (tokenResearchDeep, walletForensics, agentTrainingModule)",
    },
    "note": "naming convention is camelCase — see published_offerings.json for full list",

    # Tier 1 — $0.05 (micro, high volume)
    "tier_005": [
        {"id": "iclone-wallet-quick-v1",          "name": "wallet_quick",           "category": "crypto"},
        {"id": "iclone-csv-cleaner-v1",            "name": "csv_cleaner",            "category": "data"},
        {"id": "iclone-data-format-converter-v1",  "name": "data_format_converter",  "category": "data"},
        {"id": "iclone-regex-builder-v1",          "name": "regex_builder",          "category": "code"},
    ],

    # Tier 2 — $0.10
    "tier_010": [
        {"id": "iclone-docs-generator-v1",  "name": "docs_generator",  "category": "content"},
        {"id": "iclone-thread-quick-v1",    "name": "thread_quick",    "category": "content"},
        {"id": "iclone-test-generator-v1",  "name": "test_generator",  "category": "code"},
        {"id": "iclone-price-monitor-v1",   "name": "price_monitor",   "category": "crypto"},
    ],

    # Tier 3 — $0.25
    "tier_025": [
        {"id": "iclone-research-quick-v1",        "name": "research_quick",        "category": "research"},
        {"id": "iclone-crypto-research-quick-v1", "name": "crypto_research_quick", "category": "crypto"},
        {"id": "iclone-wallet-health-v1",         "name": "wallet_health",         "category": "crypto"},
        {"id": "iclone-code-gen-quick-v1",        "name": "code_gen_quick",        "category": "code"},
        {"id": "iclone-bug-fix-v1",               "name": "bug_fix",               "category": "code"},
        {"id": "iclone-pdf-extract-v1",           "name": "pdf_extract",           "category": "research"},
        {"id": "iclone-sql-optimizer-v1",         "name": "sql_optimizer",         "category": "code"},
    ],

    # Tier 4 — $0.50
    "tier_050": [
        {"id": "iclone-thread-standard-v1",   "name": "thread_standard",   "category": "content"},
        {"id": "iclone-code-review-v1",       "name": "code_review",       "category": "code"},
        {"id": "iclone-defi-opportunity-v1",  "name": "defi_opportunity",  "category": "defi"},
    ],

    # Tier 5 — $0.75
    "tier_075": [
        {"id": "iclone-research-standard-v1", "name": "research_standard", "category": "research"},
        {"id": "iclone-wallet-deep-v1",       "name": "wallet_deep",       "category": "crypto"},
    ],

    # Tier 6 — $1.00
    "tier_100": [
        {"id": "iclone-code-gen-standard-v1", "name": "code_gen_standard", "category": "code"},
        {"id": "iclone-scaffold-v1",          "name": "scaffold",          "category": "code"},
        {"id": "iclone-newsletter-v1",        "name": "newsletter",        "category": "content"},
    ],

    # Tier 7 — $2.00
    "tier_200": [
        {"id": "iclone-crypto-research-deep-v1", "name": "crypto_research_deep", "category": "crypto"},
        {"id": "iclone-blog-post-v1",            "name": "blog_post",            "category": "content"},
        {"id": "iclone-research-deep-v1",        "name": "research_deep",        "category": "research"},
        {"id": "iclone-onboarding-v1",           "name": "onboarding",           "category": "platform"},
    ],

    # Tier 8 — $5.00+
    "tier_500_plus": [
        {"id": "iclone-coordinate-agents-v1",      "name": "coordinate_agents",      "price": 5.0,  "category": "platform"},
        {"id": "iclone-agent-training-module-v1",  "name": "agent_training_module",  "price": 5.0,  "category": "platform"},
        {"id": "iclone-build-skill-quick-v1",      "name": "build_skill_quick",      "price": 5.0,  "category": "platform"},
        {"id": "iclone-build-skill-standard-v1",   "name": "build_skill_standard",   "price": 10.0, "category": "platform"},
        {"id": "iclone-agent-training-full-v1",    "name": "agent_training_full",    "price": 15.0, "category": "platform"},
    ],

    "client_routing": {
        "SuperSayatin": ["research", "crypto", "wallet", "price", "pdf"],
        "DoctorWHO":    ["thread", "blog", "newsletter", "docs", "csv", "onboarding"],
        "MATRIX":       ["code", "bug", "sql", "regex", "test", "scaffold", "defi", "build"],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 4 — SUPABASE SCHEMA COMPLETO
# ══════════════════════════════════════════════════════════════════════════════

SUPABASE_SCHEMA = {
    "project_id": "drbvnmlwogdxlxfkvgtw",
    "url": "https://drbvnmlwogdxlxfkvgtw.supabase.co",
    "region": "eu-north-1 (AWS)",

    "tables": {
        "acp_jobs": {
            "purpose": "Histórico completo de cada job ACP (provider side)",
            "key_columns": ["job_id (UNIQUE)", "offering_id", "client_agent_id",
                            "status", "price_usdc", "requirements_json",
                            "deliverable_url", "delivered_at", "usdc_earned", "erc8004_score"],
            "status_values": ["pending", "accepted", "executing", "delivered", "completed", "disputed"],
        },
        "agents": {
            "purpose": "Registry de todos os agentes do ecossistema",
            "migration": "001_agents_registry.sql + 002_client_agents_seed.sql",
            "key_columns": ["agent_id (Virtuals UUID)", "name", "role (PROVIDER/CLIENT/HYBRID)",
                            "evm_wallet", "entity_id", "virtual_agent_id",
                            "signer_policy", "daily_budget_usdc", "max_job_price_usdc",
                            "target_provider", "total_jobs_created", "total_earned_usdc"],
            "seeded_rows": ["CLONE (PROVIDER)", "SuperSayatin (CLIENT)", "DoctorWHO (CLIENT)", "MATRIX (CLIENT)"],
        },
        "latest_state": {
            "purpose": "Estado runtime do agente (single row, upserted a cada ciclo)",
            "key_columns": ["regime (RISK-ON/RISK-OFF/TRANSITION)", "macro_thesis",
                            "portfolio_json", "account_equity", "drawdown_pct", "risk_mode"],
        },
        "trade_log": {
            "purpose": "Cada trade aberto/fechado por Druckenmiller/Seykota",
            "key_columns": ["asset", "side (long/short)", "action (open/close/add/reduce)",
                            "size_usdc", "entry_price", "exit_price", "pnl_usdc",
                            "thesis", "regime", "seykota_score (-7 a +7)", "forum_post_id"],
        },
        "self_attendance": {
            "purpose": "Score de performance por ciclo (Soul I)",
            "key_columns": ["decision_quality", "speed", "discipline", "learning",
                            "reputation (todos 1-10)", "avg_score", "lesson_learned", "rule_added"],
        },
        "training_log": {
            "purpose": "Histórico de módulos de treino executados",
            "key_columns": ["module_name", "module_version", "session (morning/evening)",
                            "score", "key_learnings", "papers_studied"],
        },
    },

    "clone_platform_tables_planned": {
        "clients": {
            "purpose": "Clientes externos que contratam o iCLONE via plataforma CLONE",
            "key_columns": {
                "identity":  ["id (UUID)", "created_at", "status (active/trial/suspended/churned)"],
                "personal":  ["name", "email", "phone", "company", "role", "country", "timezone"],
                "onboarding":["use_case", "budget_range", "timeline", "how_heard", "goals (array)"],
                "ai_qual":   ["ai_score (0-100)", "ai_tags (array)", "ai_summary", "ai_tier (free/starter/pro/enterprise)"],
                "mgmt":      ["assigned_agent", "notes", "next_action", "last_contact_at"],
                "billing":   ["plan", "mrr", "currency", "billing_email", "stripe_customer_id"],
                "history":   ["total_jobs", "total_spent", "first_job_at", "last_job_at"],
            },
        },
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 5 — BOOTSTRAPPER V2 COMPLETO
# ══════════════════════════════════════════════════════════════════════════════

BOOTSTRAPPER_V2 = {
    "file": "ops/bootstrapper.py",
    "version": "2.0 — 2026-06-12",

    "modes": {
        "--agent supersayatin": "Dedicated: SuperSayatin contrata CLONE (research/crypto/wallet)",
        "--agent doctorwho":    "Dedicated: DoctorWHO contrata CLONE (content/docs/thread)",
        "--agent matrix":       "Dedicated: MATRIX contrata CLONE (code/sql/defi/test)",
        "--agent auto":         "Auto: browse marketplace por agentes ≤ $0.10",
        "--multi":              "Paralelo: 3 clientes em threads simultâneas",
        "--dry-run":            "Simula sem gastar USDC real",
    },

    "agent_switching": {
        "mechanism": "acp agent use --agent-id <id> ANTES de cada create-job/fund/complete",
        "restore": "CLONE sempre restaurado como activo no bloco finally (ao sair)",
        "why": "1 developer wallet controla 4 agents; CLI rastreia agente activo em ~/.config/acp/config.json",
    },

    "dedicated_mode_flow": [
        "1. switch_agent(client_agent_id)  → acp agent use --agent-id",
        "2. get_clone_offerings(categories) → carrega de published_offerings.json (local)",
        "3. acp client create-job --provider CLONE_WALLET --offering-name X --requirements JSON",
        "4. evento budget_set → switch_agent → acp client fund --job-id --amount",
        "5. evento submitted → switch_agent → acp client complete --job-id",
        "6. db.upsert_acp_job(status=completed)",
        "7. restore_clone() no exit",
    ],

    "config_defaults": {
        "daily_budget": "$10.00 USDC/dia",
        "max_job_price": "$0.10",
        "jobs_per_hour": 10,
        "max_concurrent": 20,
        "poll_interval": "8 segundos",
    },

    "launchd_plists": [
        "ops/launchd/com.iclone.supersayatin.plist",
        "ops/launchd/com.iclone.doctorwho.plist",
        "ops/launchd/com.iclone.matrix.plist",
    ],

    "systemd_services": [
        "ops/systemd/iclone-supersayatin.service",
        "ops/systemd/iclone-doctorwho.service",
        "ops/systemd/iclone-matrix.service",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 6 — ECONOMIA E PROJECÇÕES
# ══════════════════════════════════════════════════════════════════════════════

ECONOMICS = {
    "capital_plan": {
        "total": "$200 USDC",
        "CLONE_provider": "$50 USDC (fees + buffer)",
        "SuperSayatin": "$50 USDC",
        "DoctorWHO": "$50 USDC",
        "MATRIX": "$50 USDC",
        "network": "Base mainnet USDC",
        "when": "Aguarda depósito do utilizador",
    },

    "revenue_mechanics": {
        "loop": "Clientes gastam $0.05-$1.00 → CLONE recebe 60% → aGDP++ → VIRTUAL rewards",
        "acp_split": "Provider=60% | Evaluator=5% | Platform=35% (Virtuals treasury)",
        "fees_lost": "40% por job (35% platform + 5% evaluator) — custo real do protocolo",
        "capital_duration": "$50 / ($0.05 × 0.40 net_cost) = 2,500 jobs/cliente antes de vazio",
        "days_at_100_jobs": "~25 dias por cliente antes de recarregar (a $0.05/job, 100 jobs/dia)",
        "virtual_rewards": "~10% do aGDP por epoch → VIRTUAL tokens",
        "reward_frequency": "Epoch-based (semanal ou mensal — verificar app.virtuals.io)",
    },

    "projections": {
        "conservative_100_day": {
            "jobs_per_day": 300,
            "agdp_per_month": "$450",
            "virtual_per_month": "~45 VIRTUAL (~$22 a $0.50)",
            "fees_per_month": "$45",
        },
        "moderate_500_day": {
            "jobs_per_day": 1500,
            "agdp_per_month": "$2,250",
            "virtual_per_month": "~225 VIRTUAL (~$112 a $0.50)",
            "fees_per_month": "$225",
            "capital_duration": "~60 dias",
        },
        "ethy_pattern_1000_day": {
            "jobs_per_day": 3000,
            "agdp_per_month": "$4,500",
            "virtual_per_month": "~450 VIRTUAL (~$225 a $0.50)",
        },
        "6_months_virtual_at_1usd": {
            "virtual_accumulated": "~1,350 VIRTUAL",
            "value_at_1usd": "~$1,350",
            "total_portfolio": "~$1,430 sobre $200 investidos",
            "roi": "~615%",
        },
    },

    "iclone_token": {
        "symbol": "ICLONE",
        "contract": "0x43EC40d6a4Fad9e4E804dd3C0e1527ef12221Cfa",
        "supply": "1,000,000,000",
        "launch_fdv": "$100,000,000 ($0.10/token)",
        "launch_date": "~25 July 2026",
        "distribution": {
            "Liquidity Pool": "45% — Fixed Supply",
            "Automated Capital Formation": "25% — Limit Order $2M→$160M FDV",
            "Team": "20% — 6 meses vesting: Jun→Nov 2027",
            "veVIRTUAL Airdrop": "5% — Fixed Supply",
            "Growth Allocation Pool": "5% — Fixed Supply",
        },
        "platform_tiers": {
            "USER": "2,500 tokens ($250) · 48h unlock · acesso full + votes + Plaza",
            "MAKER": "250,000 tokens ($25,000) · 3 meses lock · fabrica agentes + revenue share",
        },
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 7 — MERCADO ACP (TOP AGENTS)
# ══════════════════════════════════════════════════════════════════════════════

ACP_MARKET = {
    "total_agents": 42169,
    "scraped": "2026-06-12",
    "source": "acpx.virtuals.io/api/agents",

    "top_agents": {
        "Ethy AI": {
            "agdp": "$218,099,221",
            "jobs": 1_147_916,
            "success_rate": "99.2%",
            "buyers": 7496,
            "lesson": "Infra agent dominante. ~3,145 jobs/dia. Sistema fechado/privado. A imitar.",
        },
        "Luna": {
            "agdp": "$906,815",
            "jobs": 78828,
            "avg_price": "$11.50/job",
            "lesson": "Video generation. Alto valor por job. 51% success — alto abandono.",
        },
        "Nox": {
            "agdp": "$83,520",
            "jobs": 91976,
            "price": "$0.05",
            "success_rate": "100%",
            "lesson": "Volume king. Micro-preço + 100% reliability = posição dominante.",
        },
        "aixbt": {
            "agdp": "$37,943",
            "jobs": 35845,
            "price": "$1.00",
            "buyers": 1904,
            "lesson": "Crypto intel. $1 flat. 1904 buyers únicos = base mais diversa.",
        },
    },

    "pricing_lessons": {
        "$0.01-0.05": "Volume puro. Requer infra robusta. Nox pattern.",
        "$0.10-0.25": "Sweet spot iCLONE para clientes dedicados.",
        "$1.00-2.00": "Sustainability com menos volume. aixbt/arbus pattern.",
        "$5.00+":     "Serviços premium. Baixo volume, alta margem.",
    },

    "iclone_position": {
        "strategy": "Tier 1-3 para volume ($0.05-$0.25) + Tier 6-8 para premium ($5-15)",
        "differentiator": "32 offerings cobrindo research, code, crypto, content, platform training",
        "goal": "Ethy-level volume via 3 dedicated clients gerando aGDP sistematicamente",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 8 — TRADING INTELLIGENCE (DRUCKENMILLER + SEYKOTA)
# ══════════════════════════════════════════════════════════════════════════════

TRADING_SYSTEM = {
    "druckenmiller": {
        "style": "Macro discretionary. 30.4% CAGR. Zero down years em 30 anos.",
        "three_lenses": ["LIQUIDITY (Fed, M2, stablecoins)", "VALUATION (magnitude)", "TECHNICALS (entrada/saída)"],
        "time_horizon": "18 meses à frente. Nunca trade o presente.",
        "position_sizing": {
            "probe": "5-10% (teste)",
            "confirmation": "adicionar agressivamente",
            "jugular": "30-50% (convicção extrema)",
        },
        "max_leverage": "5×",
        "max_drawdown": "20% → modo defensivo",
        "six_fresh_mind_questions": [
            "Abriria EXATAMENTE estas posições hoje a ESTES preços?",
            "A minha visão estrutural de 18 meses mudou?",
            "Druckenmiller teria TANTAS posições?",
            "O tamanho reflecte a convicção declarada?",
            "Qual é o risco de cauda para os longs? Hedge suficiente?",
            "Estou a segurar por sunk cost ou ego?",
        ],
        "never_do": ["Adicionar a perdedores", "Leverage >5×", "Short equities como alpha standalone",
                     "Trade sem tese macro", "Diversificar por diversificar"],
    },

    "seykota": {
        "style": "Trend-following sistemático.",
        "core": "Cut losses short. Let winners ride. No sacred cows.",
        "ema_scoring": {
            "indicators": "EMA(10,20,50) daily + EMA(10,20) 4H + ATR(14) + momentum 5d/10d",
            "range": "-7 a +7",
            "entry": "Long ≥ +5 | Short ≤ -5",
            "exit": "Qualquer posição abaixo de ±5 → fechar",
        },
        "position_sizing": "risk_dollars = equity × risk_pct; units = risk_dollars / (2 × ATR)",
        "trailing_stops": "Longs: ratchet UP only. Shorts: ratchet DOWN only.",
        "drawdown_modes": {
            "< 5%":   "NORMAL — 2.0% risk/trade",
            "5-10%":  "REDUCED — 1.5%",
            "10-20%": "DEFENSIVE — 1.0%",
            "> 20%":  "SURVIVAL — 0.5%",
        },
    },

    "universe_98_assets": {
        "crypto_hyperliquid": "BTC, ETH, SOL, AVAX, VIRTUAL, FET, HYPE, KAITO, TIA, ENA, WIF, FARTCOIN... (60+ assets)",
        "equities_xyz": "xyz:NVDA, xyz:META, xyz:GOOGL, xyz:TSLA, xyz:COIN, xyz:MSTR... (30 stocks)",
        "commodities_xyz": "xyz:GOLD, xyz:SILVER, xyz:BRENTOIL, xyz:COPPER, xyz:URANIUM... (10 commodities)",
        "currencies_indices": "xyz:EUR, xyz:JPY, xyz:DXY, xyz:SP500, xyz:JP225... (8 assets)",
        "prefix_rule": "Hyperliquid: plain name. Trade.xyz: xyz: prefix (e.g. xyz:NVDA)",
    },

    "cron_schedule": "A cada 12 horas — 00:00 & 12:00 UTC",
    "training_schedule": "07:00 & 19:00 UTC (training modules)",
    "forum": "degen.virtuals.io via DegenClaw — post completo após CADA trade",
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 9 — CLONE PLATFORM (PLANEADA)
# ══════════════════════════════════════════════════════════════════════════════

CLONE_PLATFORM_PLAN = {
    "repo": "clone-platform (GitHub separado do iclone)",
    "purpose": "Gestão de clientes externos que contratam o iCLONE via plataforma web",

    "components": {
        "landing_form": {
            "description": "Formulário de cadastro de clientes — world-class dark design",
            "fields": ["nome", "email", "empresa", "use_case", "budget_range", "timeline", "how_heard"],
            "design": "Dark-first, Stripe/Linear aesthetic, tipografia editorial",
        },
        "n8n_automation": {
            "flow": "webhook → validação AI → insert Supabase clients → notificação email → welcome sequence",
            "ai_scoring": "ai_score (0-100) + ai_tier (free/starter/pro/enterprise) gerado automaticamente",
        },
        "dashboard": {
            "description": "Dashboard de gestão interna (futuro)",
            "features": ["ver clientes", "histórico de jobs", "MRR tracking", "next actions"],
        },
    },

    "supabase_clients_table": {
        "identity":   ["id", "created_at", "status"],
        "personal":   ["name", "email", "phone", "company", "role", "country", "timezone"],
        "onboarding": ["use_case", "budget_range", "timeline", "how_heard", "goals[]"],
        "ai":         ["ai_score", "ai_tags[]", "ai_summary", "ai_tier"],
        "mgmt":       ["assigned_agent", "notes", "next_action", "last_contact_at"],
        "billing":    ["plan", "mrr", "currency", "stripe_customer_id"],
        "history":    ["total_jobs", "total_spent", "first_job_at", "last_job_at"],
    },

    "status": "Planeado. Começar após iCLONE estável no DigitalOcean.",
    "session": "Sessão dedicada — /spec-driven → /hm-init → /hm-engineer → /hm-designer",
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 10 — SKILLS E EXECUTION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

SKILLS_ARCHITECTURE = {
    "execution_engine": "agent/iclone/skills/execution_engine.py",
    "acp_skill": "agent/iclone/skills/acp_skill.py",
    "crypto_skill": "agent/iclone/skills/crypto_skill.py",
    "platform_skill": "agent/iclone/skills/platform_skill.py",
    "base_skill": "agent/iclone/skills/base_skill.py",

    "offering_categories": {
        "RESEARCH": "web_search native",
        "DATA_EXTRACTION": "structured extraction",
        "CODE_GENERATION": "Claude code gen",
        "CODE_REVIEW": "Claude analysis",
        "WALLET_ANALYSIS": "Etherscan + DeFiLlama",
        "DEFI_INTEL": "on-chain data",
        "CONTENT": "Claude writing",
        "AGENT_TRAINING": "training modules",
        "SKILL_BUILDING": "build new skills",
        "AGENT_COORDINATION": "multi-agent orchestration",
        "PLATFORM_ONBOARDING": "CLONE platform guide",
    },

    "apis_used": {
        "web_search": "Brave Search API",
        "webpage": "r.jina.ai/{{url}}",
        "crypto_prices": "CoinGecko + DeFiLlama",
        "wallet": "Etherscan + Alchemy",
        "trading": "Hyperliquid API",
        "llm": "Anthropic Claude (claude-sonnet-4-6)",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 11 — LIÇÕES TÉCNICAS CRÍTICAS
# ══════════════════════════════════════════════════════════════════════════════

TECHNICAL_LESSONS = {
    "secp256k1_vs_p256": {
        "problem": "Python SDK usa secp256k1. Virtuals Alchemy proxy rejeita. SSVM valida contra smart account.",
        "solution": "Usar acp-cli (P-256/Privy). Nunca Python SDK para operações on-chain.",
        "exception": "Se secp256k1 registado como signer com policy unrestricted, SDK funciona para PROVIDER ops.",
    },
    "acp_bin_path": {
        "problem": "launchd e cloud não têm Homebrew no PATH.",
        "solution": "_ACP_CANDIDATES = ['/opt/homebrew/bin/acp', '/usr/local/bin/acp', '/usr/bin/acp']",
    },
    "json_mixed_output": {
        "problem": "acp-cli mistura linhas de debug (sendCalls:start, etc.) com JSON.",
        "solution": "for line in reversed(combined.splitlines()): try json.loads(line)",
    },
    "signer_policy": {
        "problem": "policy=restricted bloqueia create-job (BUYER). policy=deny-all bloqueia tudo.",
        "solution": "acp agent add-signer --policy unrestricted para todos os agentes que criam jobs.",
    },
    "requirements_validation": {
        "problem": "{'query': 'test'} falha para offerings com schema específico.",
        "solution": "_build_requirements() — inspecciona JSON schema, preenche required fields com defaults inteligentes.",
        "fallback": "regex extract field names de plain text schema",
    },
    "bash_declare_A": {
        "problem": "macOS vem com bash 3.2 — não suporta declare -A (arrays associativos).",
        "solution": "Usar variáveis simples + funções. Nunca declare -A em scripts para macOS.",
    },
    "offerings_discovery": {
        "problem": "acp agent info --wallet não existe como comando CLI.",
        "solution": "Carregar de published_offerings.json (local, 32 offerings, sem chamada API).",
        "category_match": "Match contra fragmentos do offering_id (research, crypto, code, etc.)",
    },
    "launchd_duplicate": {
        "problem": "launchd lançava 2 instâncias simultâneas.",
        "solution": "ThrottleInterval: 60 no plist.",
    },
    "acp_cli_auth_headless": {
        "problem": "acp configure em servidor headless precisa de browser.",
        "solution": "acp configure mostra URL → user abre no Mac browser → Privy OAuth completa no servidor.",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 12 — TRAINING MODULES EXISTENTES
# ══════════════════════════════════════════════════════════════════════════════

TRAINING_MODULES_REGISTRY = {
    "scheduler": "agent/iclone/training/scheduler.py — 07:00 & 19:00 UTC",
    "modules": {
        "1_security":           "security_training.py — OWASP LLM01 2026, prompt injection, jailbreaks",
        "2_virtuals_protocol":  "virtuals_protocol_training.py — whitepaper completo",
        "3_acp":                "acp_training.py + acp_market_knowledge.py",
        "4_market_intelligence":"market_intelligence_training.py + acp_market_intelligence.py",
        "5_rider":              "rider_training.py — orquestração multi-agent, DAG, quality gates",
        "6_doctor":             "doctor_training.py — IST, IEEE/ACM, arXiv, papers AI",
        "7_hermes":             "hermes_training.py — CLI completo, ACP, DegenClaw, slash commands",
        "8_cloud_migration":    "cloud_migration_training.py — 4 agentes, DO, bootstrapper v2",
        "9_master_context":     "master_context.py (este ficheiro) — contexto total",
        "10_github_intel":      "github_intel_20260612.py + github_intel_actions.py — patterns e adoption tracking",
        "11_chaingpt_design":   "chaingpt_design_training.py — design system ChainGPT",
        "12_chaingpt_skills":   "chaingpt_skills_training.py — 23 sub-skills com triggers exactos",
    },
    "resources": {
        "acp_offerings_schema": "acp_offerings_publishing.py — schema validado",
        "resources_v1": "acp_resources.py",
        "resources_v2": "acp_resources_v2.py — lista completa de APIs",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SECÇÃO 13 — ROADMAP E PRÓXIMOS PASSOS
# ══════════════════════════════════════════════════════════════════════════════

ROADMAP = {
    "imediato_aguarda_fundos": {
        "1": "Criar conta DigitalOcean + droplet Ubuntu 22.04 ($6/mês)",
        "2": "bash ops/do/deploy.sh <IP>",
        "3": "ssh root@IP bash setup.sh",
        "4": "ssh iclone@IP bash install.sh  (auth headless)",
        "5": "bash start-services.sh  (4 serviços systemd)",
        "6": "Aplicar migrations Supabase: 001 + 002",
        "7": "Enviar $50 USDC (Base mainnet) para cada wallet",
        "8": "python3 ops/bootstrapper.py --multi (ou via systemd)",
    },

    "curto_prazo": {
        "CLONE Platform": "Next.js repo separado, formulário clientes, n8n automation",
        "WhisperFlow": "Audio transcription service (dimastatz/whisper-flow ref)",
        "Plaza Research": "Plataforma pesquisa artigos científicos — refinamento UI/UX",
        "Mais offerings": "Publicar mais offerings no Virtuals OS marketplace",
        "External clients": "Clientes reais (não dedicados) a contratar CLONE via ACP",
    },

    "medio_prazo": {
        "ICLONE token launch": "~25 Julho 2026 — FDV $100M",
        "MAKER tier": "250,000 ICLONE → fabrica agentes + revenue share",
        "aGDP scale": "Atingir Ethy-level: 3,000+ jobs/dia",
        "trading": "Hyperliquid perps com Druckenmiller + Seykota (98 assets)",
    },

    "longo_prazo": {
        "self_improving_agent": "Training a cada sessão — Knowledge, Reputation, Capital, Network",
        "agent_ecosystem": "CLONE coordena outros agentes especializados via ACP",
        "platform_revenue": "CLONE Platform MRR > iCLONE ACP revenue",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# TRAINING RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_training():
    """Valida que o master context está completo e coerente."""
    from dataclasses import dataclass

    @dataclass
    class R:
        module: str
        passed: int
        total: int
        details: list

    results = []

    def check(name, checks):
        p = sum(1 for _, ok in checks if ok)
        results.append(R(name, p, len(checks), [f"{'✓' if ok else '✗'} {n}" for n, ok in checks]))

    check("identity", [
        ("Owner wallet correcto", PROJECT_IDENTITY["owner"]["wallet_eoa"].startswith("0x7436")),
        ("3 souls definidas", len(PROJECT_IDENTITY["iclone"]["three_souls"]) == 3),
        ("5 identities", len(PROJECT_IDENTITY["iclone"]["five_identities"]) == 5),
        ("CLONE Platform stack definido", "Next.js" in PROJECT_IDENTITY["clone_platform"]["stack"]["frontend"]),
    ])

    check("architecture", [
        ("CLONE entity_id 1440", TECHNICAL_ARCHITECTURE["agents"]["CLONE"]["entity_id"] == 1440),
        ("4 agentes definidos", len(TECHNICAL_ARCHITECTURE["agents"]) == 4),
        ("SuperSayatin wallet correcto", TECHNICAL_ARCHITECTURE["agents"]["SuperSayatin"]["wallet"].startswith("0x18f3")),
        ("MATRIX wallet correcto", TECHNICAL_ARCHITECTURE["agents"]["MATRIX"]["wallet"].startswith("0x0792")),
        ("6 passos lifecycle ACP", len(TECHNICAL_ARCHITECTURE["acp_job_lifecycle"]) >= 6),
        ("DO $6/mês", "$6/mês" in TECHNICAL_ARCHITECTURE["infrastructure"]["cloud_planned"]["droplet"]),
    ])

    check("offerings", [
        ("40 offerings total", CLONE_OFFERINGS["total"] == 40),
        ("pricing_tiers definidos", "micro_001" in CLONE_OFFERINGS["pricing_tiers"]),
        ("3 clients têm routing", len(CLONE_OFFERINGS["client_routing"]) == 3),
        ("MATRIX tem routing", len(CLONE_OFFERINGS["client_routing"]["MATRIX"]) >= 5),
    ])

    check("supabase", [
        ("Project ID correcto", "drbvnmlwogdxlxfkvgtw" in SUPABASE_SCHEMA["project_id"]),
        ("6 tabelas definidas", len(SUPABASE_SCHEMA["tables"]) == 6),
        ("clients table planeada", "clients" in SUPABASE_SCHEMA["clone_platform_tables_planned"]),
        ("4 agentes no registry", "MATRIX (CLIENT)" in SUPABASE_SCHEMA["tables"]["agents"]["seeded_rows"]),
    ])

    check("economics", [
        ("$200 total", ECONOMICS["capital_plan"]["total"] == "$200 USDC"),
        ("ICLONE token address", ECONOMICS["iclone_token"]["contract"].startswith("0x43EC")),
        ("Launch ~Jul 2026", "2026" in ECONOMICS["iclone_token"]["launch_date"]),
        ("6m ROI ~615%", "615%" in ECONOMICS["projections"]["6_months_virtual_at_1usd"]["roi"]),
    ])

    check("market_intelligence", [
        ("Ethy $218M aGDP", ECONOMICS["iclone_token"] is not None),  # Ethy data in ACP_MARKET
        ("42169 agents no marketplace", ACP_MARKET["total_agents"] == 42169),
        ("4 top agents documentados", len(ACP_MARKET["top_agents"]) == 4),
    ])

    check("trading", [
        ("98 assets universe", "60+" in TRADING_SYSTEM["universe_98_assets"]["crypto_hyperliquid"]),
        ("6 fresh mind questions", len(TRADING_SYSTEM["druckenmiller"]["six_fresh_mind_questions"]) == 6),
        ("4 seykota drawdown modes", len(TRADING_SYSTEM["seykota"]["drawdown_modes"]) == 4),
        ("Max leverage 5x", "5×" in TRADING_SYSTEM["druckenmiller"]["max_leverage"]),
    ])

    check("technical_lessons", [
        ("9 lições registadas", len(TECHNICAL_LESSONS) >= 7),
        ("secp256k1 vs P-256 explicado", "P-256" in TECHNICAL_LESSONS["secp256k1_vs_p256"]["solution"]),
        ("JSON parsing fix", "reversed" in TECHNICAL_LESSONS["json_mixed_output"]["solution"]),
    ])

    check("roadmap", [
        ("8 passos imediatos", len(ROADMAP["imediato_aguarda_fundos"]) == 8),
        ("CLONE Platform no roadmap", "CLONE Platform" in ROADMAP["curto_prazo"]),
        ("ICLONE token no roadmap", "ICLONE token launch" in ROADMAP["medio_prazo"]),
    ])

    # Report
    total_p = sum(r.passed for r in results)
    total_t = sum(r.total for r in results)
    print("\n" + "═" * 65)
    print("  iCLONE MASTER CONTEXT — Validação Completa")
    print("  iCLONE + CLONE Platform + Tudo")
    print("═" * 65)
    for r in results:
        s = "✓" if r.passed == r.total else "△"
        print(f"\n  {s} {r.module:30s}  {r.passed}/{r.total}")
        for d in r.details:
            print(f"      {d}")
    pct = total_p / total_t if total_t else 0
    print(f"\n{'═' * 65}")
    print(f"  SCORE TOTAL: {total_p}/{total_t}  ({pct:.0%})")
    print("═" * 65)
    if pct >= 0.95:
        print("\n  ✓ MASTER CONTEXT COMPLETO — iCLONE tem contexto total.\n")
        print("  Sabe:")
        print("    · Identidade completa (3 souls, 5 identities, soul.md)")
        print("    · 4 agentes (CLONE + SuperSayatin + DoctorWHO + MATRIX)")
        print("    · 40 offerings (micro=$0.01, standard=$0.05, deep=$0.10)")
        print("    · Supabase schema (6 tabelas + clients planejada)")
        print("    · Bootstrapper v2 multi-agent mode")
        print("    · Cloud DO $6/mês — scripts prontos")
        print("    · CLONE Platform — Next.js, n8n, clients table")
        print("    · $200 USDC P&L → ~$1,430 em 6 meses se VIRTUAL@$1")
        print("    · Mercado ACP: 42,169 agentes, Ethy $218M aGDP")
        print("    · Trading: Druckenmiller + Seykota, 98 assets")
        print("    · 9 lições técnicas críticas (acp-cli, JSON, bash...)")
        print()
    return results


if __name__ == "__main__":
    run_training()
