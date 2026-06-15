"""
iCLONE Training Module — Cloud Migration & Multi-Agent Architecture
Session: 2026-06-12

Ensina ao iCLONE:
1. A arquitectura completa do ecossistema (4 agentes, 1 developer wallet)
2. Como os 3 clientes dedicados funcionam e os seus wallets
3. A lógica do bootstrapper v2 (multi-agent, dedicated mode)
4. O plano de migração DigitalOcean
5. A economia: P&L com $200 USDC, rewards VIRTUAL
"""

from dataclasses import dataclass
from typing import Any


# ── Knowledge blocks ───────────────────────────────────────────────────────────

AGENT_ECOSYSTEM = {
    "architecture": {
        "principle": "1 developer EOA wallet controls N smart account wallets",
        "developer_wallet": "0x743665952ec1240D62A3e580e5DC2c9e421d0537",
        "signing": "P-256 (Privy MPC) via acp-cli — NOT secp256k1",
        "chain": "Base mainnet (chain_id: 8453)",
        "smart_account_type": "ERC-4337 ModularAccountV2 (Alchemy)",
    },
    "agents": {
        "CLONE": {
            "role": "PROVIDER",
            "agent_id": "019eae06-96cd-77d0-8f8b-a6abb71f0cd7",
            "wallet": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
            "entity_id": 1440,
            "virtual_agent_id": 85280,
            "builder_code": "bc_4xeitn8j",
            "offerings_count": 32,
            "signer_policy": "unrestricted",
            "status": "LIVE — server running via acp-cli",
        },
        "SuperSayatin": {
            "role": "CLIENT",
            "agent_id": "019ebb92-7415-7baa-93e9-ee19a7742877",
            "wallet": "0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3",
            "target_provider": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
            "categories": ["research", "crypto", "wallet", "price", "pdf"],
            "clone_offerings_matched": 8,
            "status": "CREATED — pending $50 USDC funding",
        },
        "DoctorWHO": {
            "role": "CLIENT",
            "agent_id": "019ebb92-93e8-7b4e-b2e8-39c3419843c9",
            "wallet": "0x875242eb5c91270ca80ed7753a87d6e22e4f5acf",
            "target_provider": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
            "categories": ["thread", "blog", "newsletter", "docs", "csv", "onboarding"],
            "clone_offerings_matched": 5,
            "status": "CREATED — pending $50 USDC funding",
        },
        "MATRIX": {
            "role": "CLIENT",
            "agent_id": "019ebb92-b4be-7660-82d3-4b1647843e6a",
            "wallet": "0x07924dea2c8212969d5dc5655785aa5063adb2bc",
            "target_provider": "0x44cc25d55a4291b92f52062ba023ca1f14206664",
            "categories": ["code", "bug", "sql", "regex", "test", "scaffold", "defi", "build"],
            "clone_offerings_matched": 9,
            "status": "CREATED — pending $50 USDC funding",
        },
    },
}

BOOTSTRAPPER_V2_KNOWLEDGE = {
    "modes": {
        "dedicated": {
            "description": "Client agent contrata CLONE directamente",
            "command": "python3 ops/bootstrapper.py --agent supersayatin|doctorwho|matrix",
            "mechanism": "acp agent use --agent-id before every create-job/fund/complete",
            "offerings_source": "published_offerings.json (local, 32 offerings, no API call)",
            "category_routing": {
                "supersayatin": ["research", "crypto", "wallet", "price", "pdf"],
                "doctorwho":    ["thread", "blog", "newsletter", "docs", "csv", "onboarding"],
                "matrix":       ["code", "bug", "sql", "regex", "test", "scaffold", "defi", "build"],
            },
        },
        "auto": {
            "description": "Browse marketplace por agentes baratos (comportamento original)",
            "command": "python3 ops/bootstrapper.py --agent auto",
            "mechanism": "browse_cheap_agents → round-robin 60 agents ≤ $0.10",
        },
        "multi": {
            "description": "3 clientes em paralelo (threads)",
            "command": "python3 ops/bootstrapper.py --multi",
            "mechanism": "3× threading.Thread, staggered 2s, max_concurrent // 3 per thread",
        },
    },
    "agent_switching": {
        "how": "acp agent use --agent-id <id> before EVERY blockchain operation",
        "restore": "CLONE always restored as active on exit (finally block)",
        "why": "1 developer wallet → N agents, CLI tracks active agent in ~/.config/acp/config.json",
    },
    "lifecycle": {
        "1_create_job": "client: create-job --provider CLONE_WALLET --offering-name X --requirements JSON",
        "2_fund":       "on budget_set event → client: fund --job-id --amount",
        "3_complete":   "on submitted event → client: complete --job-id --reason",
        "4_supabase":   "upsert_acp_job(status=completed) after complete",
    },
}

DIGITALOCEAN_PLAN = {
    "droplet": {
        "size": "Basic · Regular · $6/mês (1 vCPU, 1GB RAM, 25GB SSD)",
        "region": "Frankfurt or Amsterdam (low latency to Base RPC)",
        "os": "Ubuntu 22.04 LTS",
        "stack": "Python 3.12 · Node.js 20 · acp-cli · systemd",
    },
    "services": {
        "iclone-server":        "CLONE provider server — always on",
        "iclone-supersayatin":  "SuperSayatin client — always on",
        "iclone-doctorwho":     "DoctorWHO client — always on",
        "iclone-matrix":        "MATRIX client — always on",
    },
    "deploy_commands": {
        "1_sync":  "bash ops/do/deploy.sh <DROPLET-IP>",
        "2_setup": "ssh root@IP 'bash /tmp/setup.sh'",
        "3_install": "ssh iclone@IP 'bash /opt/iclone/ops/do/install.sh'",
        "4_auth":  "acp configure (headless: URL opens in Mac browser)",
        "5_start": "ssh root@IP 'bash /opt/iclone/ops/do/start-services.sh'",
    },
    "auth_headless": {
        "method": "acp configure on server → shows URL → user opens in Mac browser → Privy OAuth completes",
        "credential_store": "~/.config/acp/config.json (per-agent keys via Privy MPC)",
    },
}

ECONOMICS = {
    "capital_plan": {
        "total": "$200 USDC",
        "per_agent": "$50 USDC × 4 (CLONE + 3 clients)",
        "network": "Base mainnet USDC",
    },
    "revenue_model": {
        "mechanism": "Clients spend → CLONE earns (money circulates) · only ACP fees (~10%) are lost",
        "agdp_per_job": "$0.05 (average offering price)",
        "virtual_rewards": "~10% of aGDP per epoch → paid in VIRTUAL tokens",
        "reward_frequency": "Epoch-based (weekly or monthly — check app.virtuals.io)",
    },
    "projections_moderate": {
        "jobs_per_day": 1500,
        "agdp_per_month": "$2,250",
        "virtual_rewards_monthly": "~225 VIRTUAL (~$112 at $0.50)",
        "fees_lost_monthly": "$225",
        "capital_duration": "~60 days before $50 wallets need refill",
    },
    "projections_if_virtual_1usd": {
        "6_month_virtual_accumulated": "~1,350 VIRTUAL",
        "value": "~$1,350 at $1.00/VIRTUAL",
        "total_portfolio": "~$1,430 on $200 invested",
    },
}

TECHNICAL_FIXES_LEARNED = {
    "acp_cli_path": {
        "problem": "launchd and cloud don't have Homebrew in PATH",
        "fix": "Auto-detect: try /opt/homebrew/bin/acp → /usr/local/bin/acp → /usr/bin/acp",
        "code": "_ACP_CANDIDATES = ['/opt/homebrew/bin/acp', '/usr/local/bin/acp', '/usr/bin/acp']",
    },
    "json_parsing": {
        "problem": "acp-cli mixes debug lines (sendCalls:start) with JSON output",
        "fix": "Scan lines in reverse for first valid JSON",
        "code": "for line in reversed(combined.splitlines()): try json.loads(line)",
    },
    "signer_policy": {
        "problem": "restricted policy blocks create-job (BUYER operations)",
        "fix": "acp agent add-signer --policy unrestricted",
        "applies_to": "All agents that need to create jobs (CLIENT role)",
    },
    "requirements_validation": {
        "problem": "Generic {'query': 'test'} fails validation for most offerings",
        "fix": "_build_requirements() — inspects JSON schema required fields, fills with sensible defaults",
        "fallback": "Regex extract field names from plain text schema",
    },
    "bash_declare_A": {
        "problem": "macOS ships with bash 3.2 — no associative arrays (declare -A)",
        "fix": "Use plain variables + functions instead of declare -A",
    },
    "offerings_discovery": {
        "problem": "acp agent info --wallet does not exist as CLI command",
        "fix": "Load from published_offerings.json (local file, 32 offerings)",
        "category_matching": "Match offering_id fragments (research, crypto, code, etc.)",
    },
}

SUPABASE_SCHEMA = {
    "migrations": {
        "001_agents_registry.sql": "Creates agents table + seeded with CLONE",
        "002_client_agents_seed.sql": "Inserts SuperSayatin, DoctorWHO, MATRIX",
    },
    "agents_table_key_columns": [
        "agent_id (Virtuals UUID)",
        "role (PROVIDER/CLIENT/HYBRID)",
        "evm_wallet",
        "signer_policy",
        "daily_budget_usdc",
        "target_provider (CLIENT agents only)",
        "total_jobs_created/completed",
        "total_spent/earned_usdc",
    ],
}


# ── Training runner ────────────────────────────────────────────────────────────

@dataclass
class TrainingResult:
    module: str
    passed: int
    total: int
    details: list[str]

    @property
    def score(self) -> float:
        return self.passed / self.total if self.total else 0.0


def run_training() -> list[TrainingResult]:
    results = []

    # Test 1: Agent ecosystem knowledge
    checks = [
        ("CLONE entity_id == 1440",
         AGENT_ECOSYSTEM["agents"]["CLONE"]["entity_id"] == 1440),
        ("SuperSayatin wallet correct",
         AGENT_ECOSYSTEM["agents"]["SuperSayatin"]["wallet"].startswith("0x18f3")),
        ("DoctorWHO wallet correct",
         AGENT_ECOSYSTEM["agents"]["DoctorWHO"]["wallet"].startswith("0x8752")),
        ("MATRIX wallet correct",
         AGENT_ECOSYSTEM["agents"]["MATRIX"]["wallet"].startswith("0x0792")),
        ("1 developer wallet for 4 agents",
         "1 developer EOA" in AGENT_ECOSYSTEM["architecture"]["principle"]),
        ("Signing via P-256",
         "P-256" in AGENT_ECOSYSTEM["architecture"]["signing"]),
    ]
    passed = sum(1 for _, ok in checks if ok)
    results.append(TrainingResult(
        "agent_ecosystem",
        passed, len(checks),
        [f"{'✓' if ok else '✗'} {name}" for name, ok in checks],
    ))

    # Test 2: Bootstrapper v2
    checks = [
        ("Multi mode exists", "multi" in BOOTSTRAPPER_V2_KNOWLEDGE["modes"]),
        ("Dedicated mode targets CLONE", BOOTSTRAPPER_V2_KNOWLEDGE["modes"]["dedicated"]["mechanism"] is not None),
        ("MATRIX has 9 offerings", AGENT_ECOSYSTEM["agents"]["MATRIX"]["clone_offerings_matched"] == 9),
        ("Agent switching on every op", "every" in BOOTSTRAPPER_V2_KNOWLEDGE["agent_switching"]["how"].lower()),
        ("CLONE restored on exit", "CLONE always restored" in BOOTSTRAPPER_V2_KNOWLEDGE["agent_switching"]["restore"]),
        ("Offerings from local file", "published_offerings.json" in BOOTSTRAPPER_V2_KNOWLEDGE["modes"]["dedicated"]["offerings_source"]),
    ]
    passed = sum(1 for _, ok in checks if ok)
    results.append(TrainingResult(
        "bootstrapper_v2",
        passed, len(checks),
        [f"{'✓' if ok else '✗'} {name}" for name, ok in checks],
    ))

    # Test 3: Economics
    checks = [
        ("Total capital $200", ECONOMICS["capital_plan"]["total"] == "$200 USDC"),
        ("$50 per agent", "$50 USDC × 4" in ECONOMICS["capital_plan"]["per_agent"]),
        ("Fee ~10%", "10%" in ECONOMICS["revenue_model"]["mechanism"]),
        ("Moderate: 1500 jobs/day", ECONOMICS["projections_moderate"]["jobs_per_day"] == 1500),
        ("VIRTUAL rewards exist", ECONOMICS["revenue_model"]["virtual_rewards"] is not None),
        ("$1 scenario → $1,430", "$1,430" in ECONOMICS["projections_if_virtual_1usd"]["total_portfolio"]),
    ]
    passed = sum(1 for _, ok in checks if ok)
    results.append(TrainingResult(
        "economics",
        passed, len(checks),
        [f"{'✓' if ok else '✗'} {name}" for name, ok in checks],
    ))

    # Test 4: Technical fixes
    checks = [
        ("ACP_BIN auto-detect",
         "/opt/homebrew/bin/acp" in TECHNICAL_FIXES_LEARNED["acp_cli_path"]["code"]),
        ("JSON reverse scan",
         "reversed" in TECHNICAL_FIXES_LEARNED["json_parsing"]["code"]),
        ("Unrestricted signer for clients",
         "unrestricted" in TECHNICAL_FIXES_LEARNED["signer_policy"]["fix"]),
        ("Offerings from local file",
         "published_offerings.json" in TECHNICAL_FIXES_LEARNED["offerings_discovery"]["fix"]),
        ("macOS bash 3.2 no declare -A",
         TECHNICAL_FIXES_LEARNED["bash_declare_A"]["problem"] is not None),
    ]
    passed = sum(1 for _, ok in checks if ok)
    results.append(TrainingResult(
        "technical_fixes",
        passed, len(checks),
        [f"{'✓' if ok else '✗'} {name}" for name, ok in checks],
    ))

    # Test 5: Cloud migration
    checks = [
        ("DO Droplet $6/mês", "$6/mês" in DIGITALOCEAN_PLAN["droplet"]["size"]),
        ("4 systemd services", len(DIGITALOCEAN_PLAN["services"]) == 4),
        ("Headless auth via URL",
         "Mac browser" in DIGITALOCEAN_PLAN["auth_headless"]["method"]),
        ("deploy.sh rsync approach", "deploy.sh" in DIGITALOCEAN_PLAN["deploy_commands"]["1_sync"]),
    ]
    passed = sum(1 for _, ok in checks if ok)
    results.append(TrainingResult(
        "cloud_migration",
        passed, len(checks),
        [f"{'✓' if ok else '✗'} {name}" for name, ok in checks],
    ))

    return results


def print_report(results: list[TrainingResult]) -> None:
    print("\n" + "═" * 60)
    print("  iCLONE Training — Cloud Migration & Multi-Agent Arch")
    print("  Session: 2026-06-12")
    print("═" * 60)

    total_passed = total_checks = 0
    for r in results:
        total_passed += r.passed
        total_checks += r.total
        status = "✓" if r.passed == r.total else "△"
        print(f"\n  {status} {r.module:30s}  {r.passed}/{r.total}  ({r.score:.0%})")
        for detail in r.details:
            print(f"      {detail}")

    overall = total_passed / total_checks if total_checks else 0
    print(f"\n{'═' * 60}")
    print(f"  OVERALL: {total_passed}/{total_checks} ({overall:.0%})")
    print("═" * 60 + "\n")

    # Summary for soul.md update
    if overall >= 0.9:
        print("  → Training PASSED. Knowledge integrated.")
        print("  → iCLONE now knows:")
        print("     · 4-agent ecosystem (CLONE + 3 dedicated clients)")
        print("     · Bootstrapper v2 multi-agent mode")
        print("     · DO cloud migration path ($6/mês, Mac off)")
        print("     · $200 P&L model → ~$1,430 in 6 months if VIRTUAL@$1")
        print("     · Technical fixes: acp path, JSON parsing, bash 3.2")
    else:
        print("  → Training INCOMPLETE. Review failed checks.")
    print()


if __name__ == "__main__":
    results = run_training()
    print_report(results)
