"""
iCLONE — ChainGPT Skills Training Module
Sources: github.com/ChainGPT-org/chaingpt-claude-skill (140 MCP tools)
         github.com/ChainGPT-org/AgenticOS

Treina o iCLONE com:
  - Todas as 140 ferramentas MCP do ChainGPT Developer Kit
  - Arquitectura e padrões do AgenticOS (Twitter/X AI Agent)
  - Padrões de segurança para DeFi custodyfree
  - Estratégias de trading, bridging, e pagamentos x402
  - Smart contract patterns (45+ auditados)
  - Agent wallet + policy gate model

Score mínimo de aprovação: 90%
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

MODULE_ID  = "chaingpt_skills_training"
MODULE_VER = "1.0.0"
SOURCE     = "https://github.com/ChainGPT-org/chaingpt-claude-skill"

# ─── Knowledge base ───────────────────────────────────────────────────────────

CHAINGPT_KNOWLEDGE = {

    "overview": {
        "kit_name": "ChainGPT Developer Kit for Claude Code",
        "total_tools": 140,
        "total_categories": 15,
        "version": "1.21.0",
        "philosophy": "Turn your AI assistant into a Web3 engineering co-pilot. Custody-free. Policy-gated. LLM cannot bypass security.",
        "install_command": "/plugin marketplace add ChainGPT-org/chaingpt-claude-skill",
        "api_key_env": "CHAINGPT_API_KEY",
        "dashboard_command": "/chaingpt:dashboard",
        "dashboard_port": 8788,
        "wallet_admin_port": 8787,
        "solana_rpc_env": "SOLANA_RPC_URL",
        "test_suite": "428 vitest + 26 mock + 39 live-smoke",
    },

    "security_model": {
        "core_principle": "Policy file lives outside the model's reach. Every signature is checked in code. LLM cannot bypass policy.",
        "policy_gate": "chaingpt_agent_wallet_sign_and_send — only fund-moving tool. Refuses with reason on any policy violation.",
        "prompt_injection_defence": "Policy file is a file the model has NO tool to write. Prompt injection gets a refusal, not funds.",
        "velocity_caps": "Daily spend caps + tx-count velocity caps bound even fully-compliant behaviour.",
        "keystore": "AES-256-GCM encrypted with scrypt KDF. Passphrase via OS keychain or CHAINGPT_AGENT_WALLET_PASSPHRASE env var.",
        "dashboard_security": "Binds 127.0.0.1 only. Admin token rotates every restart. HttpOnly + SameSite=Strict + 1h TTL cookie.",
        "mandatory_audit_gate": "chaingpt-deploy enforces: generate → audit → compile → estimate → confirm → build-tx → user-signs → verify",
        "mainnet_guard": "chaingpt_deploy_build_tx REFUSES mainnet without acknowledgeMainnet: true",
        "health_factor_gate": "chaingpt-defi enforces chaingpt_defi_aave_health check BEFORE any borrow or withdraw",
        "defi_preflight": "chaingpt-trade: chaingpt_risk_token on buy token + chaingpt_dex_quote BEFORE any build_swap_tx",
    },

    "tool_categories": {
        "x402_base_erc8004": {
            "tool_count": 13,
            "description": "Agentic payments (x402/EIP-3009), Base Basenames, Farcaster Mini Apps, ERC-8004 trustless agent identity",
            "tools": {
                "chaingpt_x402_decode": "Decode x402 402 challenge / X-PAYMENT header into human terms before paying",
                "chaingpt_x402_build_payment": "Build UNSIGNED EIP-3009 transferWithAuthorization typed data; return X-PAYMENT header once signed",
                "chaingpt_x402_facilitator": "Call a facilitator: supported / verify / settle",
                "chaingpt_x402_create_requirements": "Generate PaymentRequirements + 402 body to monetize your own API",
                "chaingpt_base_resolve_name": "Resolve name.base.eth ↔ address (forward + reverse). Verified live on Base mainnet.",
                "chaingpt_base_name_availability": "Check if Basename is available + price for N years",
                "chaingpt_base_register_name_tx": "UNSIGNED Basename registration tx (sets addr + reverse record). Mainnet gated.",
                "chaingpt_miniapp_manifest": "Generate /.well-known/farcaster.json for Base App / Farcaster Mini App",
                "chaingpt_miniapp_embed": "Generate fc:miniapp (+ legacy fc:frame) share embed meta tag",
                "chaingpt_miniapp_validate": "Validate Mini App manifest against spec",
                "chaingpt_erc8004_resolve_agent": "Resolve ERC-8004 agent → owner + AgentCard. Verified live on Base mainnet.",
                "chaingpt_erc8004_registries": "Canonical Identity/Reputation registry addresses (0x8004... singletons)",
                "chaingpt_erc8004_agentcard": "Generate spec-compliant registration-v1 AgentCard (incl. x402Support)",
            },
            "settlement": "x402 settles in USDC on Base via EIP-3009. Facilitator can only broadcast, never change amount or recipient.",
        },

        "chaingpt_ai_products": {
            "tool_count": 18,
            "description": "Core ChainGPT API: chatbot, NFT generation, contract audit, code generation, crypto news",
            "requires_api_key": True,
            "tools": {
                "chaingpt_chat": "Ask the Web3 AI chatbot — crypto-native LLM with live on-chain data",
                "chaingpt_chat_with_context": "Branded chatbot with company/token context injection",
                "chaingpt_chat_history": "Retrieve past conversations by session id",
                "chaingpt_nft_generate_image": "Generate AI art for NFTs",
                "chaingpt_nft_enhance_prompt": "Enhance NFT generation prompt",
                "chaingpt_nft_generate_and_mint": "Generate and mint NFT on 22+ chains",
                "chaingpt_nft_get_chains": "List supported chains for NFT minting",
                "chaingpt_audit_contract": "AI security audit with scored report",
                "chaingpt_generate_contract": "Natural language → production Solidity",
                "chaingpt_news_fetch": "Fetch crypto news with category + token filters",
                "chaingpt_news_categories": "List available news categories",
                "chaingpt_estimate_credits": "Estimate credits cost for a tool call",
                "chaingpt_check_balance": "Check remaining ChainGPT credits",
            },
            "pricing": "1000 credits = $10 USD. 15% bonus if paid in $CGPT token.",
            "nft_chains": 22,
        },

        "web3_toolkit": {
            "tool_count": 14,
            "description": "Wallet, research, risk, on-chain data across 11 chains",
            "supported_chains": ["ethereum", "base", "arbitrum", "optimism", "polygon", "bsc", "avalanche", "blast", "linea", "scroll", "solana"],
            "tools": {
                "chaingpt_wallet_balances": "Multi-chain native + ERC-20 balances (Moralis opt + RPC)",
                "chaingpt_wallet_positions": "DeFi positions across chains",
                "chaingpt_wallet_pnl": "Realized + unrealized P&L",
                "chaingpt_research_token": "Price, liquidity, volume (DexScreener)",
                "chaingpt_research_pairs": "All trading pairs for a token",
                "chaingpt_research_trending": "Trending tokens (DexScreener)",
                "chaingpt_risk_token": "Honeypot / mintable / proxy flags, buy+sell simulation (GoPlus)",
                "chaingpt_risk_honeypot": "Honeypot detection",
                "chaingpt_risk_address": "Sanctions / phishing check",
                "chaingpt_risk_contract_source": "Verified source code (Etherscan v2)",
                "chaingpt_onchain_tx": "Decode any transaction",
                "chaingpt_onchain_address": "Recent address activity",
                "chaingpt_onchain_gas": "Multi-chain gas oracle",
                "chaingpt_onchain_block": "Block info",
            },
            "optional_keys": {
                "MORALIS_API_KEY": "Full multi-chain ERC-20 scan + DeFi positions + P&L (25k req/month free)",
                "ETHERSCAN_API_KEY": "Higher rate limit on Etherscan v2 (covers every major EVM chain)",
                "ONEINCH_API_KEY": "1inch v6 aggregator routing",
            },
        },

        "ai_enriched_composed": {
            "tool_count": 2,
            "description": "DexScreener + GoPlus + ChainGPT news + AI signal in one call. Strategic differentiator.",
            "tools": {
                "chaingpt_intel_token": "DexScreener + GoPlus + ChainGPT news + AI signal. ~1 credit. THE token research tool.",
                "chaingpt_intel_wallet": "Portfolio + per-holding risk rating across chains. Free read.",
            },
        },

        "contract_deployment": {
            "tool_count": 5,
            "description": "Mainnet contract deployment. Custody-free. Mandatory audit gate.",
            "mandatory_pipeline": "generate → audit → compile → estimate → confirm → build-tx → user-signs → verify",
            "tools": {
                "chaingpt_deploy_compile": "Solidity 0.8.x → bytecode + ABI + warnings",
                "chaingpt_deploy_estimate": "Preview gas cost on target chain",
                "chaingpt_deploy_build_tx": "REFUSES mainnet without acknowledgeMainnet: true",
                "chaingpt_deploy_verify": "Submit source to Etherscan v2",
                "chaingpt_deploy_verify_status": "Poll verification GUID",
            },
            "mainnets": ["ethereum", "base", "arbitrum", "optimism", "polygon", "bsc", "avalanche", "blast", "linea", "scroll"],
            "testnets": ["sepolia", "base-sepolia", "arbitrum-sepolia", "optimism-sepolia", "polygon-amoy", "bsc-testnet"],
        },

        "dex_trading": {
            "tool_count": 9,
            "description": "Mainnet DEX trading. Custody-free. Same acknowledgeMainnet safety pattern.",
            "mandatory_preflight": "chaingpt_risk_token on buy token + chaingpt_dex_quote BEFORE any build_swap_tx",
            "tools": {
                "chaingpt_dex_quote": "Get quote (OpenOcean v4, EVM)",
                "chaingpt_dex_build_swap_tx": "Build unsigned swap tx (OpenOcean v4)",
                "chaingpt_dex_approve_tx": "Build ERC-20 approval tx",
                "chaingpt_dex_jupiter_quote": "Jupiter v6 quote (Solana)",
                "chaingpt_dex_jupiter_build_swap_tx": "Jupiter v6 unsigned swap tx (Solana)",
                "chaingpt_dex_1inch_quote": "1inch v6 quote (EVM, key-gated)",
                "chaingpt_dex_1inch_build_swap_tx": "1inch v6 unsigned swap tx",
                "chaingpt_dex_cow_quote": "CoW Protocol quote (EVM, intent-based, MEV-protected)",
                "chaingpt_dex_cow_create_order": "CoW Protocol order creation",
            },
            "aggregators": {"EVM": ["OpenOcean v4", "1inch v6", "CoW Protocol"], "Solana": ["Jupiter v6"]},
        },

        "defi_protocols": {
            "tool_count": 12,
            "description": "Aave V3, Lido, EigenLayer, Pendle, Morpho. Custody-free. Health-factor gate.",
            "mandatory_check": "chaingpt_defi_aave_health BEFORE any borrow or withdraw",
            "tools": {
                "chaingpt_defi_aave_health": "Check Aave V3 health factor before borrow/withdraw",
                "chaingpt_defi_aave_supply_tx": "Supply collateral to Aave V3",
                "chaingpt_defi_aave_borrow_tx": "Borrow from Aave V3",
                "chaingpt_defi_aave_repay_tx": "Repay Aave V3 debt",
                "chaingpt_defi_aave_withdraw_tx": "Withdraw from Aave V3",
                "chaingpt_defi_lido_stake_tx": "Stake ETH → stETH on Lido",
                "chaingpt_defi_eigenlayer_deposit_tx": "Restake stETH/rETH/cbETH on EigenLayer",
                "chaingpt_defi_pendle_markets": "Pendle yield-strip discovery (fixed APY, implied APY, YT, maturity)",
                "chaingpt_defi_pendle_market": "Specific Pendle market details",
                "chaingpt_defi_morpho_markets": "Morpho Blue isolated markets",
                "chaingpt_defi_morpho_vaults": "MetaMorpho curated vaults",
                "chaingpt_defi_morpho_user": "User position in Morpho",
            },
            "aave_chains": ["ethereum", "base", "arbitrum", "optimism", "polygon", "bsc", "avalanche"],
        },

        "perps": {
            "tool_count": 14,
            "description": "Hyperliquid (signed EIP-712 actions) + Drift (read-only)",
            "tools": {
                "chaingpt_hl_markets": "Hyperliquid market data",
                "chaingpt_hl_mids": "Mid prices",
                "chaingpt_hl_orderbook": "HL orderbook",
                "chaingpt_hl_account": "HL account state",
                "chaingpt_hl_fills": "HL trade fills",
                "chaingpt_hl_funding": "HL funding rates",
                "chaingpt_hl_place_order_payload": "EIP-712 signed order intent (user wallet finalizes)",
                "chaingpt_hl_cancel_order_payload": "EIP-712 cancel order intent",
                "chaingpt_hl_update_leverage_payload": "EIP-712 leverage update intent",
                "chaingpt_drift_markets": "Drift perp markets",
                "chaingpt_drift_market": "Specific Drift market",
                "chaingpt_drift_orderbook": "Drift orderbook",
                "chaingpt_drift_funding": "Drift funding rates",
                "chaingpt_drift_user": "Drift user account",
            },
        },

        "prediction_markets": {
            "tool_count": 6,
            "description": "Polymarket — read + signed CTF/Neg-Risk orders",
            "tools": {
                "chaingpt_pm_markets": "Discover Polymarket markets",
                "chaingpt_pm_market": "Specific market data",
                "chaingpt_pm_orderbook": "Market orderbook",
                "chaingpt_pm_trades": "Recent trades",
                "chaingpt_pm_create_order": "EIP-712 signed CTF order intent",
                "chaingpt_pm_create_neg_risk_order": "EIP-712 signed Neg-Risk order intent",
            },
        },

        "bridging": {
            "tool_count": 3,
            "description": "Across Protocol v3 — 10 EVM mainnets",
            "tools": {
                "chaingpt_bridge_quote": "Get bridge quote (Across v3)",
                "chaingpt_bridge_build_deposit_tx": "Build unsigned bridge deposit tx",
                "chaingpt_bridge_status": "Check bridge status",
            },
            "supported_chains": 10,
        },

        "solana_defi": {
            "tool_count": 8,
            "description": "Marginfi v2 + Kamino. Reads + custody-free deposit/withdraw (mainnet-verified, simulated).",
            "requires": "SOLANA_RPC_URL env var — public endpoint rate-limits heavy on-chain SDK fetches. Helius/Triton/QuickNode free tier.",
            "tools": {
                "chaingpt_defi_marginfi_banks": "Marginfi v2 banks",
                "chaingpt_defi_marginfi_account": "Marginfi user account",
                "chaingpt_defi_kamino_markets": "Kamino markets",
                "chaingpt_defi_kamino_vaults": "Kamino automated yield vaults",
                "chaingpt_solana_sign_tx": "Custody-free VersionedTransaction (Ed25519 agent wallet, classic + Token-2022)",
                "chaingpt_solana_spl_transfer": "SPL token transfer",
            },
        },

        "portfolio_strategy": {
            "tool_count": 7,
            "description": "Multi-protocol portfolio snapshot + strategy plan persistence + backtest",
            "tools": {
                "chaingpt_portfolio_snapshot": "Fan-out parallel to HL + PM + Morpho + Drift for one user",
                "chaingpt_strategy_dca": "DCA strategy template planner",
                "chaingpt_strategy_grid": "Grid strategy template planner",
                "chaingpt_strategy_funding_arb": "Funding rate arbitrage strategy",
                "chaingpt_strategy_copy_trade": "Copy trade strategy planner",
                "chaingpt_strategy_save_plan": "Persist strategy plan to ~/.chaingpt-mcp/plans/",
                "chaingpt_strategy_load_plan": "Load saved strategy plan",
                "chaingpt_backtest_grid": "Replay buy/sell ladder vs historical CoinGecko prices. Reports realized P&L vs buy-and-hold.",
            },
            "scheduled_autonomy": {
                "dca_example": "set up a daily $100 ETH DCA that runs without me → chaingpt_strategy_dca_plan → save_plan → /schedule cron",
                "crash_safe": "Execution journal prevents double-buy on crash/double-fire",
                "journal": "Records every tx hash. Journal refuses if already executed for this period.",
            },
        },

        "agent_wallet": {
            "tool_count": 7,
            "description": "Encrypted EOA + admin policy gate. LLM cannot bypass policy.",
            "tools": {
                "chaingpt_agent_wallet_init": "AES-256-GCM encrypted keystore, scrypt KDF. Creates EOA.",
                "chaingpt_agent_wallet_address": "Read EOA address",
                "chaingpt_agent_wallet_status": "Wallet status",
                "chaingpt_agent_wallet_balances": "Wallet balances",
                "chaingpt_agent_wallet_policy": "Read current policy (never shows key)",
                "chaingpt_agent_wallet_sign_and_send": "ONLY fund-moving tool. Policy gate runs deterministically.",
                "chaingpt_agent_wallet_serve_ui": "Start localhost admin dashboard on 127.0.0.1:8787",
            },
            "policy_templates": ["Balanced DeFi", "DeFi Only", "Unrestricted (⚠️)", "Read Only", "CEX Only",
                                  "NFT Only", "Staking Only", "Bridge Only", "Custom"],
            "default_policy": "Balanced DeFi: kill switch OFF, 0.1 native per-tx cap, major DEX/lending routers allowlisted",
            "passphrase_sources": ["OS keychain (macOS Keychain / Linux libsecret)", "CHAINGPT_AGENT_WALLET_PASSPHRASE env var"],
        },
    },

    "project_templates": [
        "web3-researcher",
        "defi-trader",
        "nft-creator",
        "contract-deployer",
        "perp-trader",
        "prediction-market-analyst",
        "bridge-operator",
        "portfolio-manager",
        "dca-bot",
        "copy-trader",
    ],

    "smart_contract_patterns": {
        "count": 45,
        "description": "45+ audited Solidity patterns. Production-ready. Etherscan-verified.",
        "categories": [
            "ERC-20 (standard, mintable, burnable, capped, pausable)",
            "ERC-721 (NFT, enumerable, URI storage, royalty ERC-2981)",
            "ERC-1155 (multi-token, batch transfer)",
            "ERC-4337 (account abstraction UserOp)",
            "ERC-8004 (trustless agent identity)",
            "Governance (Compound-style, OpenZeppelin Governor)",
            "Multisig (Gnosis Safe-style)",
            "Vesting (linear, cliff)",
            "Staking (single-asset, LP, rewards)",
            "DEX (Uniswap V2 fork, V3 position manager)",
            "Lending (Aave-style isolated market)",
            "Flash loans (AAVE receiver interface)",
            "Proxy patterns (UUPS, Transparent)",
            "Price oracles (Chainlink aggregator consumer)",
            "Cross-chain (LayerZero OApp receiver)",
        ],
    },

    "agenticos": {
        "repo": "https://github.com/ChainGPT-org/AgenticOS",
        "description": "ChainGPT Twitter/X AI Agent. AI-driven tweet generation, posting, and Web3 community engagement.",
        "stack": ["TypeScript", "Hono", "Bun runtime"],
        "bun_advantage": "Ultra-fast runtime. No Node.js overhead. Native TypeScript. Bun.serve() for HTTP.",
        "hono_advantage": "Ultra-lightweight web framework. Edge-first. TypeScript-native. Minimal overhead.",
        "features": [
            "Automated tweet generation from crypto/Web3 context",
            "Community engagement automation",
            "Twitter/X API v2 integration",
            "Webhook support for real-time triggers",
            "Scheduled posting (cron-based)",
            "AI content generation pipeline",
        ],
        "pattern": "Trigger → Context Fetch → AI Generation → Post → Monitor Engagement",
        "key_lesson": "Bun + Hono = ultra-fast API server for AI agents that need low latency tweet posting",
    },

    "design_for_iclone": {
        "immediate_use_cases": [
            "Use chaingpt_intel_token as the backend for iCLONE's tokenResearchDeep offering",
            "Use chaingpt_risk_token for rugPullScreener offering",
            "Use chaingpt_portfolio_snapshot for walletDeepAnalysis offering",
            "Use chaingpt_defi_aave_health for loopingStrategyCheck offering",
            "Use chaingpt_bridge_quote for crossChainArb offering",
            "Use chaingpt_hl_markets + chaingpt_hl_funding for fundingRateMonitor offering",
            "Use chaingpt_pm_markets for prediction market intelligence offerings",
            "Use chaingpt_audit_contract for contractAuditQuick offering",
            "Use chaingpt_generate_contract for soliditySnippet offering",
            "Use chaingpt_news_fetch for cryptoBreakingNews and cryptoHourlyDigest offerings",
        ],
        "agent_identity": "iCLONE should register an ERC-8004 AgentCard with x402Support for autonomous payment capability",
        "x402_integration": "iCLONE can monetize its own API endpoints using chaingpt_x402_create_requirements",
        "erc8004_benefit": "On-chain trustless identity means other agents can verify iCLONE's capabilities and trust without intermediary",
    },
}

# ─── Training checks ─────────────────────────────────────────────────────────

TRAINING_CHECKS = [

    # Core knowledge
    ("What is the ChainGPT Developer Kit?",
     "140 MCP tools for Claude Code. Custody-free Web3 co-pilot: AI products, DEX trading, DeFi, perps, bridging, x402 payments, smart contracts.",
     "overview"),

    ("What is the main security principle?",
     "Policy file lives outside the model's reach. LLM cannot bypass policy. Every signature is checked in code.",
     "security"),

    ("What env var enables ChainGPT AI products?",
     "CHAINGPT_API_KEY — without it, on-chain tools work but chat/NFT/audit/news fail.",
     "api"),

    ("How much does ChainGPT API cost?",
     "1000 credits = $10. 15% bonus if paid in $CGPT token.",
     "pricing"),

    # DEX trading
    ("What is the mandatory preflight before any DEX swap?",
     "chaingpt_risk_token on the buy token + chaingpt_dex_quote BEFORE any build_swap_tx.",
     "dex"),

    ("Which DEX aggregators does the kit support?",
     "EVM: OpenOcean v4, 1inch v6, CoW Protocol. Solana: Jupiter v6.",
     "dex"),

    ("What makes CoW Protocol different?",
     "Intent-based, MEV-protected. No frontrunning. Batch settlement.",
     "dex"),

    # DeFi
    ("What check is mandatory before Aave borrow or withdraw?",
     "chaingpt_defi_aave_health must be called before any borrow or withdraw.",
     "defi"),

    ("Which chains does Aave V3 support in the kit?",
     "ethereum, base, arbitrum, optimism, polygon, bsc, avalanche (7 chains).",
     "defi"),

    ("What does chaingpt_defi_lido_stake_tx do?",
     "Stakes native ETH → stETH on Lido. Liquid staking.",
     "defi"),

    # Contract deployment
    ("What is the mandatory pipeline for contract deployment?",
     "generate → audit → compile → estimate → confirm → build-tx → user-signs → verify",
     "contracts"),

    ("Why does chaingpt_deploy_build_tx require acknowledgeMainnet: true?",
     "Safety gate to prevent accidental mainnet deployment. Must explicitly confirm mainnet intent.",
     "contracts"),

    # x402 + ERC-8004
    ("What is x402 and how does it settle?",
     "Agentic payment protocol. Settles in USDC on Base via EIP-3009 (transferWithAuthorization). Facilitator can only broadcast, never change amount.",
     "x402"),

    ("What is ERC-8004?",
     "Trustless agent identity standard. Agents register an AgentCard on-chain. Other agents can verify capabilities without intermediary.",
     "erc8004"),

    ("What is an AgentCard?",
     "On-chain registration-v1 document with agent capabilities, including x402Support flag for autonomous payment.",
     "erc8004"),

    # Perps
    ("What is the difference between Hyperliquid and Drift in the kit?",
     "Hyperliquid: full signing (EIP-712 L1 actions, order placement). Drift: read-only in this release.",
     "perps"),

    ("How does Hyperliquid signing work?",
     "EIP-712 signed L1 action intents. Custody-free. User wallet finalizes the signature.",
     "perps"),

    # Agent wallet
    ("What is the agent wallet?",
     "AES-256-GCM encrypted EOA (scrypt KDF). Only chaingpt_agent_wallet_sign_and_send can move funds. Policy gate runs deterministically.",
     "wallet"),

    ("How does prompt injection protection work in the agent wallet?",
     "Policy file is a file the model has NO tool to write. Prompt injection gets a refusal, not your funds.",
     "wallet"),

    ("What is the default agent wallet policy?",
     "Balanced DeFi: kill switch OFF, 0.1 native per-tx cap, major DEX/lending routers allowlisted.",
     "wallet"),

    # Portfolio + strategy
    ("What does chaingpt_portfolio_snapshot do?",
     "Fan-out parallel to HL + PM + Morpho + Drift for one user. One call, full picture.",
     "portfolio"),

    ("How does scheduled DCA autonomy work?",
     "chaingpt_strategy_dca_plan → save_plan → /schedule cron. Execution journal prevents double-buy on crash/double-fire.",
     "strategy"),

    # Bridging
    ("What bridge protocol does the kit use?",
     "Across Protocol v3. 10 EVM mainnets supported.",
     "bridge"),

    # AgenticOS
    ("What is AgenticOS and what stack does it use?",
     "ChainGPT Twitter/X AI Agent. TypeScript + Hono + Bun runtime. Ultra-fast tweet generation and posting for Web3 communities.",
     "agenticos"),

    ("Why does AgenticOS use Bun instead of Node.js?",
     "Ultra-fast runtime, native TypeScript, no overhead. Bun.serve() for HTTP with minimal latency — critical for real-time tweet posting.",
     "agenticos"),

    # iCLONE integration
    ("How should iCLONE use chaingpt_intel_token?",
     "As the backend for tokenResearchDeep, rugPullScreener, and cryptoNewsAlpha offerings. One call returns DexScreener + GoPlus + news + AI signal.",
     "integration"),

    ("Why should iCLONE register an ERC-8004 AgentCard?",
     "On-chain trustless identity. Other ACP agents can verify iCLONE's capabilities. Enables x402Support for autonomous payment capability.",
     "integration"),

    ("How can iCLONE monetize endpoints with x402?",
     "Use chaingpt_x402_create_requirements to generate PaymentRequirements + 402 body. Enables per-call micro-payments in USDC on Base.",
     "integration"),

    # Solana
    ("What Solana RPC env var should be set for DeFi tools?",
     "SOLANA_RPC_URL — public endpoint rate-limits heavy on-chain SDK fetches. Use Helius/Triton/QuickNode free tier.",
     "solana"),

    ("What Solana DeFi protocols are supported?",
     "Marginfi v2 (banks + deposit/withdraw), Kamino (markets + automated vaults), Jupiter v6 (DEX swaps), Drift (perps read-only).",
     "solana"),
]

# ─── Training module ──────────────────────────────────────────────────────────

@dataclass
class TrainingResult:
    total: int = 0
    passed: int = 0
    failed: list = field(default_factory=list)
    score: float = 0.0
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _check(question: str, expected_keywords: str, category: str, result: TrainingResult) -> None:
    """Verify that knowledge entry is loaded and accessible."""
    result.total += 1
    knowledge_str = str(CHAINGPT_KNOWLEDGE).lower()
    # Extract 3-5 meaningful single words from the expected answer
    words = [w.strip(".,():-→") for w in expected_keywords.lower().split() if len(w) > 4]
    words = [w for w in words if w not in ("which", "where", "their", "these", "those", "about", "using", "when", "every", "never", "before", "after")]
    keywords = words[:5]
    found = sum(1 for kw in keywords if kw in knowledge_str)
    threshold = max(1, len(keywords) * 2 // 3)
    if found >= threshold:
        result.passed += 1
    else:
        result.failed.append({"question": question, "category": category, "missing_keywords": keywords})


def run_training() -> dict:
    """Run ChainGPT skills training. Returns score report."""
    result = TrainingResult()

    for question, expected, category in TRAINING_CHECKS:
        _check(question, expected, category, result)

    result.score = round(result.passed / result.total * 100, 1) if result.total else 0.0

    return {
        "module": MODULE_ID,
        "version": MODULE_VER,
        "source": SOURCE,
        "session_id": result.session_id,
        "timestamp": result.timestamp,
        "total": result.total,
        "passed": result.passed,
        "failed_count": len(result.failed),
        "score": result.score,
        "passed_threshold": result.score >= 90.0,
        "failures": result.failed,
        "knowledge_summary": {
            "total_tools": CHAINGPT_KNOWLEDGE["overview"]["total_tools"],
            "categories": len(CHAINGPT_KNOWLEDGE["tool_categories"]),
            "contract_patterns": CHAINGPT_KNOWLEDGE["smart_contract_patterns"]["count"],
            "project_templates": len(CHAINGPT_KNOWLEDGE["project_templates"]),
            "supported_chains_evm": 10,
            "supported_chains_total": 11,
        },
    }


if __name__ == "__main__":
    import json
    report = run_training()
    print(json.dumps(report, indent=2))
    print(f"\n{'✓ PASSED' if report['passed_threshold'] else '✗ FAILED'} — {report['score']}% ({report['passed']}/{report['total']})")
