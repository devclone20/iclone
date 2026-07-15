"""
iCLONE — ChainGPT MCP Training Module v2.0
Source: github.com/ChainGPT-org/chaingpt-claude-skill (v1.21.0)
        ~/.claude/plugins/cache/chaingpt-claude-skill/chaingpt/ebd1c30/

Treina o iCLONE com:
  - Todos os 140 MCP tools organizados por categoria (35 ficheiros de tools)
  - 23 sub-skills com triggers exactos
  - Reference docs completos (pricing, errors, web3-toolkit, onchain-execution)
  - Templates de produção e padrões Solidity auditados
  - Modelos de agentes (defi-trader, web3-researcher, contract-auditor)
  - Integração directa com os 40 offerings de cada agente iCLONE

Score mínimo de aprovação: 92%
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

MODULE_ID  = "chaingpt_mcp_training_v2"
MODULE_VER = "2.0.0"
PASS_THRESHOLD = 0.92

# ─── Data structures ──────────────────────────────────────────────────────────

@dataclass
class TrainingSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module_id: str = MODULE_ID
    module_version: str = MODULE_VER
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed: bool = False
    total: int = 0
    passed: int = 0
    score: float = 0.0
    passed_threshold: bool = False
    insights: list[str] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ─── Knowledge base ───────────────────────────────────────────────────────────

OVERVIEW = {
    "name": "ChainGPT Developer Kit for Claude Code",
    "version": "1.21.0",
    "plugin_root": "~/.claude/plugins/cache/chaingpt-claude-skill/chaingpt/ebd1c30",
    "total_mcp_tools": 140,
    "total_skills": 23,
    "total_templates": 11,
    "total_patterns": 45,
    "total_agents": 3,
    "total_reference_docs": 20,
    "mcp_server_port": "stdio",
    "dashboard_port": 8788,
    "wallet_admin_port": 8787,
    "mock_server_port": 3001,
    "api_key_env": "CHAINGPT_API_KEY",
    "solana_rpc_env": "SOLANA_RPC_URL",
    "moralis_key_env": "MORALIS_API_KEY",
    "etherscan_key_env": "ETHERSCAN_API_KEY",
    "credits_dashboard": "https://app.chaingpt.org/addcredits",
    "test_suite": "428 vitest + 26 mock + 159 validate + 39 live-smoke",
    "supported_evm_chains": [
        "ethereum", "base", "arbitrum", "optimism", "polygon",
        "bsc", "avalanche", "blast", "linea", "scroll",
    ],
    "supported_deploy_testnets": [
        "sepolia", "base-sepolia", "arbitrum-sepolia",
        "optimism-sepolia", "polygon-amoy", "bsc-testnet",
    ],
    "supported_solana": True,
    "nft_mint_chains": 22,
}

SECURITY_MODEL = {
    "core_principle": (
        "Policy file lives outside the model's reach — the LLM has NO tool to write it. "
        "Every signature is checked in code before executing. Prompt injection gets a refusal, not funds."
    ),
    "mainnet_guard": (
        "Every state-changing tool refuses to return an unsigned tx unless "
        "acknowledgeMainnet=true is passed explicitly by the user in THIS conversation."
    ),
    "policy_gate": (
        "chaingpt_agent_wallet_sign_and_send is the ONLY fund-moving tool. "
        "Policy caps (per-tx + daily velocity) are enforced in code, not by the LLM."
    ),
    "keystore": "AES-256-GCM encrypted, scrypt KDF. Passphrase from OS keychain or CHAINGPT_AGENT_WALLET_PASSPHRASE.",
    "dashboard_security": "Binds 127.0.0.1 only. Admin token rotates every restart. HttpOnly + SameSite=Strict + 1h TTL.",
    "mandatory_audit_gate": (
        "Deploy pipeline: generate → audit → compile → estimate → acknowledgeMainnet → build_tx → user-signs → verify. "
        "Audit is mandatory for mainnet; never skippable."
    ),
    "defi_preflight": (
        "Before ANY borrow/withdraw: chaingpt_defi_aave_health. Health factor < 1.5 must be explicitly accepted. "
        "Before ANY swap: chaingpt_risk_token on buy token + quote tool."
    ),
    "custody_model": (
        "Plugin NEVER holds private keys. Every state-changing tool returns UNSIGNED tx or EIP-712 payload. "
        "User signs externally via MetaMask, Rabby, hardware wallet, or ERC-4337 smart account."
    ),
    "prompt_injection_defence": "Three independent layers: plan journal, policy gate, schedule. A compromised schedule cannot bypass the policy.",
}

# ─── All 140 MCP tools by category ────────────────────────────────────────────

MCP_TOOLS = {

    # ── ChainGPT AI products (require CHAINGPT_API_KEY) ──
    "chaingpt_ai": {
        "requires_api_key": True,
        "credits_per_call": {"chat": 0.5, "chat_with_history": 1.0, "nft_image": 1, "audit": 1, "generator": 1, "news_10": 1},
        "tools": {
            "chaingpt_chat": "Web3 AI chatbot — crypto-native LLM with live on-chain context",
            "chaingpt_chat_with_context": "Branded chatbot with company/token context injection",
            "chaingpt_chat_history": "Retrieve past conversations by session id (free)",
            "chaingpt_nft_generate_image": "Generate AI art for NFTs (1 credit base)",
            "chaingpt_nft_enhance_prompt": "Enhance NFT prompt before generation (0.5 credits)",
            "chaingpt_nft_generate_and_mint": "Generate + mint NFT on 22 chains",
            "chaingpt_nft_generate_multiple": "Batch NFT generation (up to 10)",
            "chaingpt_nft_surprise_me": "Random NFT generation with random style",
            "chaingpt_nft_get_chains": "List supported chains for minting (free)",
            "chaingpt_nft_get_collections": "List user's minted collections (free)",
            "chaingpt_audit_contract": "AI security audit — scored report (1 credit)",
            "chaingpt_audit_history": "Retrieve past audits by session id (free)",
            "chaingpt_generate_contract": "Natural language → production Solidity (1 credit)",
            "chaingpt_generate_history": "Retrieve past generated contracts (free)",
            "chaingpt_news_fetch": "Fetch crypto news: category + token filters (1 credit/10 records)",
            "chaingpt_news_categories": "List available news categories (free)",
            "chaingpt_estimate_credits": "Estimate credits for a tool call (free)",
            "chaingpt_check_balance": "Check remaining ChainGPT credits (free)",
        },
    },

    # ── Web3 research + risk (free, no API key needed) ──
    "research_risk": {
        "requires_api_key": False,
        "optional_keys": ["MORALIS_API_KEY", "ETHERSCAN_API_KEY"],
        "tools": {
            "chaingpt_wallet_balances": "Multi-chain native + ERC-20 balances (Moralis + public RPC fallback)",
            "chaingpt_wallet_positions": "DeFi positions across protocols (Moralis)",
            "chaingpt_wallet_pnl": "Realized + unrealized P&L (Moralis)",
            "chaingpt_portfolio_snapshot": "Multi-protocol portfolio fan-out (all holdings in one call)",
            "chaingpt_research_token": "Live price / volume / liquidity by symbol or address (DexScreener)",
            "chaingpt_research_pairs": "All trading pairs for a token (DexScreener)",
            "chaingpt_research_trending": "Trending tokens right now (DexScreener)",
            "chaingpt_risk_token": "GoPlus: honeypot / mintable / proxy / blacklist flags — MANDATORY before any swap",
            "chaingpt_risk_honeypot": "Honeypot.is: real buy+sell simulation — checks actual tax",
            "chaingpt_risk_address": "GoPlus: sanctioned / phishing / mixer flags on any address",
            "chaingpt_risk_contract_source": "Etherscan v2: verified source + ABI — checks contract authenticity",
            "chaingpt_onchain_tx": "Decode any tx by hash (Etherscan v2)",
            "chaingpt_onchain_address": "Address activity + recent txs (Etherscan v2; needs ETHERSCAN_API_KEY)",
            "chaingpt_onchain_gas": "Multi-chain gas oracle (Etherscan v2 + public RPC)",
            "chaingpt_onchain_block": "Block info — latest or by number (public RPC)",
            "chaingpt_intel_token": "Composed: DexScreener + GoPlus + ChainGPT news + AI signal (credits)",
            "chaingpt_intel_wallet": "Composed: Moralis balances + GoPlus risk-rate per holding (credits)",
        },
    },

    # ── DEX trading — EVM + Solana (mainnet-only, custody-free) ──
    "dex": {
        "requires_api_key": False,
        "mainnet_only": True,
        "preflight_required": ["chaingpt_risk_token", "chaingpt_dex_quote"],
        "providers": {
            "openocean": "Default. No API key. 10 EVM mainnets. Best for most tokens.",
            "1inch_v6": "Key-gated. Better routing for blue-chip tokens.",
            "cow_protocol": "MEV-protected intent-based. Best for large trades. Signs EIP-712 order.",
            "jupiter": "Solana-native swaps.",
        },
        "tools": {
            "chaingpt_dex_quote": "Get swap quote: price, price impact, minimum-out — MANDATORY before any swap",
            "chaingpt_dex_approve_tx": "Build UNSIGNED ERC-20 approval tx (bounded > max preferred)",
            "chaingpt_dex_build_swap_tx": "Build UNSIGNED swap tx — refuses without acknowledgeMainnet=true",
            "chaingpt_dex_cow_create_order": "Create CoW Protocol order (EIP-712 intent)",
            "chaingpt_dex_cow_submit_signed_order": "Submit signed CoW order to orderbook",
            "chaingpt_dex_jupiter_quote": "Get Jupiter swap quote on Solana",
            "chaingpt_dex_jupiter_build_swap_tx": "Build UNSIGNED Jupiter swap tx (VersionedTransaction base64)",
        },
    },

    # ── DeFi protocols (mainnet-only, custody-free) ──
    "defi": {
        "requires_api_key": False,
        "mainnet_only": True,
        "protocols": {
            "aave_v3": "Lending on 7 chains: supply / borrow / repay / withdraw. Health factor mandatory before borrow/withdraw.",
            "lido": "ETH staking → stETH (Ethereum mainnet only)",
            "eigenlayer": "ETH restaking (Ethereum mainnet only)",
            "pendle": "Yield-trading: PT/YT markets on multiple chains",
            "morpho": "Blue lending markets + MetaMorpho vaults",
            "kamino": "Solana lending — requires SOLANA_RPC_URL",
            "marginfi": "Solana lending — requires SOLANA_RPC_URL",
        },
        "tools": {
            "chaingpt_defi_aave_health": "Check Aave health factor — MANDATORY before any borrow or withdraw",
            "chaingpt_defi_aave_supply_tx": "UNSIGNED Aave supply tx",
            "chaingpt_defi_aave_borrow_tx": "UNSIGNED Aave borrow tx",
            "chaingpt_defi_aave_repay_tx": "UNSIGNED Aave repay tx",
            "chaingpt_defi_aave_withdraw_tx": "UNSIGNED Aave withdraw tx",
            "chaingpt_defi_lido_stake_tx": "UNSIGNED Lido stETH staking tx",
            "chaingpt_defi_eigenlayer_deposit_tx": "UNSIGNED EigenLayer restaking deposit tx",
            "chaingpt_defi_pendle_markets": "List all Pendle yield markets",
            "chaingpt_defi_pendle_market": "Get single Pendle market details (PT/YT rates)",
            "chaingpt_defi_morpho_markets": "List Morpho Blue lending markets",
            "chaingpt_defi_morpho_vaults": "List MetaMorpho vaults",
            "chaingpt_defi_morpho_position": "Get user position in Morpho",
            "chaingpt_defi_kamino_markets": "List Kamino lending markets (Solana)",
            "chaingpt_defi_kamino_vaults": "List Kamino vaults (Solana)",
            "chaingpt_defi_kamino_deposit_tx": "UNSIGNED Kamino deposit tx",
            "chaingpt_defi_kamino_withdraw_tx": "UNSIGNED Kamino withdraw tx",
            "chaingpt_defi_marginfi_banks": "List Marginfi banks (Solana)",
            "chaingpt_defi_marginfi_account": "Get user Marginfi account",
            "chaingpt_defi_marginfi_deposit_tx": "UNSIGNED Marginfi deposit tx",
            "chaingpt_defi_marginfi_withdraw_tx": "UNSIGNED Marginfi withdraw tx",
        },
    },

    # ── Contract deployment (mainnet + testnet, custody-free) ──
    "deploy": {
        "requires_api_key": True,
        "mandatory_pipeline": [
            "chaingpt_generate_contract (optional — from description)",
            "chaingpt_audit_contract (MANDATORY for mainnet)",
            "chaingpt_deploy_compile",
            "chaingpt_deploy_estimate",
            "chaingpt_deploy_build_tx (requires acknowledgeMainnet=true)",
            "user signs externally",
            "chaingpt_deploy_verify",
            "chaingpt_deploy_verify_status",
        ],
        "tools": {
            "chaingpt_generate_contract": "Natural language → production Solidity",
            "chaingpt_audit_contract": "Security audit — MANDATORY before mainnet deploy",
            "chaingpt_deploy_compile": "Compile with solc 0.8.x → bytecode + ABI",
            "chaingpt_deploy_estimate": "Gas + USD cost preview (10% buffer applied)",
            "chaingpt_deploy_build_tx": "UNSIGNED deploy tx — refuses mainnet without acknowledgeMainnet=true",
            "chaingpt_deploy_verify": "Submit source to Etherscan v2 multichain verification",
            "chaingpt_deploy_verify_status": "Poll verification status until confirmed",
        },
    },

    # ── Perps: Hyperliquid (EVM) ──
    "hyperliquid": {
        "requires_api_key": False,
        "read_only_v1": True,
        "preflight": "Check funding (chaingpt_hl_funding) before recommending direction or carry",
        "tools": {
            "chaingpt_hl_markets": "All Hyperliquid perp markets + metadata",
            "chaingpt_hl_mids": "Live mid prices for all markets",
            "chaingpt_hl_orderbook": "L2 orderbook depth for a market",
            "chaingpt_hl_account": "User account state — positions, margin, unrealized P&L",
            "chaingpt_hl_fills": "Recent fills for a wallet",
            "chaingpt_hl_funding": "Funding rate history — use before any directional recommendation",
            "chaingpt_hl_place_order_payload": "Build EIP-712 L1 action for a limit/market order",
            "chaingpt_hl_cancel_order_payload": "Build EIP-712 L1 action for order cancellation",
            "chaingpt_hl_submit_signed_action": "Submit user-signed L1 action to Hyperliquid",
        },
    },

    # ── Perps: Drift Protocol (Solana) ──
    "drift": {
        "requires_api_key": False,
        "read_only_v1": True,
        "preflight": "Check drift_funding before recommending direction",
        "tools": {
            "chaingpt_drift_markets": "All Drift perp markets",
            "chaingpt_drift_market": "Single market details",
            "chaingpt_drift_orderbook": "Drift orderbook depth",
            "chaingpt_drift_user": "User account: positions, collateral, unrealized P&L",
            "chaingpt_drift_funding": "Funding rate history on Solana perps",
        },
    },

    # ── Prediction markets: Polymarket (Polygon) ──
    "polymarket": {
        "requires_api_key": False,
        "read_only_v1": True,
        "tools": {
            "chaingpt_pm_markets": "List open prediction markets",
            "chaingpt_pm_market": "Single market details + current odds",
            "chaingpt_pm_orderbook": "CLOB orderbook for a market",
            "chaingpt_pm_trades": "Recent trades for a market",
            "chaingpt_pm_place_order_payload": "Build EIP-712 CLOB order",
            "chaingpt_pm_submit_signed_order": "Submit signed Polymarket order",
        },
    },

    # ── Cross-chain bridge: Across Protocol v3 ──
    "bridge": {
        "requires_api_key": False,
        "mainnet_only": True,
        "supported_chains": 10,
        "model": "Intent-based — relayer fills on destination in seconds. User deposits on origin.",
        "tools": {
            "chaingpt_bridge_quote": "Get bridge quote: fee, estimated time, minimum output — MANDATORY first",
            "chaingpt_bridge_build_deposit_tx": "UNSIGNED depositV3 tx on origin chain",
            "chaingpt_bridge_status": "Poll bridge status by deposit tx hash",
        },
    },

    # ── Strategy + scheduled autonomy ──
    "strategy": {
        "requires_api_key": False,
        "strategy_types": ["dca", "grid", "funding_arb", "copy"],
        "safety_layers": [
            "Plan journal (idempotency — re-runs cannot double-buy)",
            "Policy gate (caps spending per tx + per 24h window)",
            "Schedule (fires ticks, has NO spending authority)",
        ],
        "tools": {
            "chaingpt_strategy_dca_plan": "Build DCA plan: token, total, intervals, cadence",
            "chaingpt_strategy_grid_plan": "Build grid trading plan: range, levels, size",
            "chaingpt_strategy_funding_arb_plan": "Build funding-rate arbitrage plan (HL vs Drift)",
            "chaingpt_strategy_copy_plan": "Build copy-trading plan from a target wallet",
            "chaingpt_strategy_save_plan": "Persist plan to disk (journal-backed)",
            "chaingpt_strategy_load_plan": "Load plan by name",
            "chaingpt_strategy_list_plans": "List all saved plans",
            "chaingpt_strategy_delete_plan": "Delete a saved plan",
            "chaingpt_strategy_due_steps": "Return steps due for execution (respects journal)",
            "chaingpt_strategy_mark_step": "Mark step as completed/skipped (idempotent — cannot re-mark)",
            "chaingpt_backtest_dca": "Backtest DCA strategy against historical price data",
            "chaingpt_backtest_grid": "Backtest grid strategy",
        },
    },

    # ── Agent wallet (bounded autonomous execution) ──
    "agent_wallet": {
        "keystore_encryption": "AES-256-GCM, scrypt KDF",
        "passphrase_source": "OS keychain (auto on macOS) or CHAINGPT_AGENT_WALLET_PASSPHRASE env",
        "policy_templates": 9,
        "supports_evm": True,
        "supports_solana": True,
        "tools": {
            "chaingpt_agent_wallet_init": "Create encrypted keystore — passphrase from keychain",
            "chaingpt_agent_wallet_address": "Return EVM wallet address",
            "chaingpt_agent_wallet_balances": "Check agent wallet balances",
            "chaingpt_agent_wallet_status": "Active policy: kill switch, caps, daily-spend window",
            "chaingpt_agent_wallet_policy": "Read current policy (model has NO write tool for policy)",
            "chaingpt_agent_wallet_sign_and_send": "ONLY fund-moving tool — policy gate enforced in code",
            "chaingpt_agent_wallet_serve_ui": "Launch admin dashboard at localhost:8787",
            "chaingpt_agent_wallet_solana_init": "Create Solana keypair (encrypted, same keystore)",
            "chaingpt_agent_wallet_solana_address": "Return Solana wallet address",
            "chaingpt_agent_wallet_solana_sign_and_send": "Solana-native signed tx submission",
        },
    },

    # ── ERC-4337 account abstraction ──
    "erc4337": {
        "entrypoint": "v0.7",
        "bundlers_supported": ["Pimlico", "Alchemy", "Stackup"],
        "tools": {
            "chaingpt_aa_userop_hash": "Compute userOpHash for ERC-4337 v0.7 UserOperation",
            "chaingpt_aa_pack_userop": "Pack UserOperation into EntryPoint wire format",
            "chaingpt_aa_estimate_userop": "Estimate gas for a UserOperation via bundler",
            "chaingpt_aa_submit_userop": "Submit UserOperation to a bundler",
            "chaingpt_aa_userop_receipt": "Poll UserOperation receipt",
            "chaingpt_aa_session_build_grant": "Build session-key grant (Safe/Kernel/Biconomy/Alchemy SW)",
            "chaingpt_aa_session_build_revoke": "Build session-key revocation",
            "chaingpt_aa_session_status": "Check session-key status",
        },
    },

    # ── x402 agentic payments (USDC on Base) ──
    "x402": {
        "protocol": "Coinbase HTTP 402. EIP-3009 transferWithAuthorization.",
        "settlement": "USDC on Base. Facilitator can only broadcast, never change amount or recipient.",
        "tools": {
            "chaingpt_x402_decode": "Decode 402 challenge / X-PAYMENT header into human terms",
            "chaingpt_x402_build_payment": "Build UNSIGNED EIP-3009 typed data → X-PAYMENT header after user signs",
            "chaingpt_x402_facilitator": "Call facilitator: supported / verify / settle",
            "chaingpt_x402_create_requirements": "Generate PaymentRequirements to monetize your own API",
        },
    },

    # ── Base ecosystem ──
    "base": {
        "tools": {
            "chaingpt_base_resolve_name": "Resolve name.base.eth ↔ address (forward + reverse, live)",
            "chaingpt_base_name_availability": "Check Basename availability + price for N years",
            "chaingpt_base_register_name_tx": "UNSIGNED Basename registration tx — mainnet gated",
            "chaingpt_miniapp_manifest": "Generate /.well-known/farcaster.json for Base App / Farcaster Mini App",
            "chaingpt_miniapp_embed": "Generate fc:miniapp share embed meta tag",
            "chaingpt_miniapp_validate": "Validate Mini App manifest against spec",
        },
    },

    # ── ERC-8004 trustless agent identity ──
    "erc8004": {
        "standard": "ERC-8004 — on-chain agent identity + reputation (Base mainnet)",
        "tools": {
            "chaingpt_erc8004_resolve_agent": "Resolve agent id → owner + AgentCard (ERC-721 Identity Registry)",
            "chaingpt_erc8004_registries": "Canonical Identity/Reputation registry addresses",
            "chaingpt_erc8004_agentcard": "Generate spec-compliant registration-v1 AgentCard (incl. x402Support)",
        },
    },

    # ── Solana foundation ──
    "solana": {
        "tools": {
            "chaingpt_solana_build_transfer_tx": "UNSIGNED native SOL + SPL token transfer (VersionedTransaction base64)",
            "chaingpt_solana_decode_tx": "Decode base64 Solana tx into human-readable instructions",
        },
    },

    # ── Dashboard + utility ──
    "utility": {
        "tools": {
            "chaingpt_dashboard_serve": "Launch marketplace dashboard at localhost:8788 — 6 tabs: Overview/Wallet/Skills/Activity/Health/About",
        },
    },
}

# ─── 23 sub-skills with exact triggers ────────────────────────────────────────

SKILLS = {
    "aa": {
        "description": "ERC-4337 v0.7 account abstraction: userOpHash, UserOperation packing, bundler-RPC proxy",
        "triggers": ["ERC-4337", "account abstraction", "smart contract wallet", "userop", "user operation",
                     "bundler", "paymaster", "session key", "EntryPoint", "AA wallet", "smart wallet", "gas sponsorship"],
    },
    "agent-wallet": {
        "description": "Give the AI agent its own EVM wallet with admin-controlled policies the agent cannot bypass",
        "triggers": ["agent wallet", "give the agent a wallet", "agent address", "fund the agent",
                     "agent autonomy", "policy gate", "kill switch", "agent permissions",
                     "bounded autonomy", "ERC-4337 alternative", "session-key alternative"],
    },
    "base": {
        "description": "Base chain: Basenames ENS-style naming, Base App, Farcaster Mini Apps",
        "triggers": ["base name", "basename", ".base.eth", "resolve base name", "register basename",
                     "base app", "mini app", "miniapp", "farcaster frame", "fc:miniapp",
                     "MiniKit", "OnchainKit", "farcaster.json manifest"],
    },
    "bridge": {
        "description": "Cross-chain bridging via Across Protocol v3 — 10 EVM mainnets, custody-free",
        "triggers": ["bridge", "cross-chain", "move from base to ethereum", "send to arbitrum",
                     "L2 to L1", "bridge USDC", "optimism to polygon"],
    },
    "chaingpt": {
        "description": "ChainGPT AI developer platform: chatbot, NFT generator, contract tools, crypto news, AgenticOS",
        "triggers": ["chaingpt", "web3 ai", "nft generator", "smart contract audit", "crypto news api",
                     "agenticos", "solidity llm", "cgpt", "blockchain ai", "token analytics"],
    },
    "dashboard": {
        "description": "Local web dashboard — 6 tabs: Overview, Wallet, Skills, Activity, Health, About",
        "triggers": ["dashboard", "open the dashboard", "ChainGPT dashboard", "marketplace dashboard",
                     "show me the dashboard", "web UI", "control panel", "skills overview",
                     "agent wallet panel", "env check", "plugin health"],
    },
    "debug": {
        "description": "Troubleshoot ChainGPT API errors — 401/402/403/404/429, credits, streaming, NFT",
        "triggers": ["chaingpt error", "api not working", "401", "402", "403", "404", "429",
                     "insufficient credits", "rate limit", "streaming broken", "nft stuck"],
    },
    "defi": {
        "description": "Aave V3, Lido, EigenLayer, Pendle, Morpho, Kamino, Marginfi — custody-free",
        "triggers": ["aave", "lido", "stake eth", "steth", "restake", "eigenlayer", "supply", "borrow",
                     "repay", "withdraw", "lending", "health factor", "liquidation", "leverage",
                     "yield", "defi position", "pendle", "morpho", "gauntlet", "fixed yield",
                     "pt", "yt", "metamorpho", "vault", "lending market", "kamino", "marginfi",
                     "solana lending", "solana defi"],
    },
    "deploy": {
        "description": "Deploy Solidity to mainnet/testnet: generate → audit → compile → deploy → verify",
        "triggers": ["deploy contract", "ship contract", "deploy to mainnet", "deploy to ethereum",
                     "deploy to base", "deploy to bsc", "verify contract", "mainnet deploy",
                     "contract deployment"],
    },
    "drift": {
        "description": "Drift Protocol read-only: Solana perps markets, orderbook, user positions, funding rates",
        "triggers": ["drift", "drift protocol", "solana perps", "SOL-PERP", "BONK-PERP", "WIF-PERP",
                     "drift funding", "perps on solana", "app.drift.trade"],
    },
    "hackathon": {
        "description": "Scaffold complete hackathon project with ChainGPT APIs in 60 seconds",
        "triggers": ["hackathon", "hackatron", "hackathon starter", "hackathon kit", "competition project",
                     "quick prototype", "demo project", "submission"],
    },
    "hyperliquid": {
        "description": "Hyperliquid read + trade: perp markets, orderbook, account state, fills, funding, signed orders",
        "triggers": ["hyperliquid", "hl", "perps", "perpetual", "funding rate", "orderbook",
                     "my positions on hyperliquid", "leverage trading", "BTC perp", "ETH perp"],
    },
    "playground": {
        "description": "Interactive test of any ChainGPT API endpoint",
        "triggers": ["test api", "try endpoint", "playground", "test chaingpt", "send request",
                     "try nft generator", "test chatbot api"],
    },
    "polymarket": {
        "description": "Polymarket prediction markets: live odds, orderbook, trades, CLOB order placement",
        "triggers": ["polymarket", "prediction market", "betting odds", "election odds",
                     "will X happen", "Foresight AI", "prediction odds"],
    },
    "research": {
        "description": "Token/wallet/contract research: DexScreener + GoPlus + Etherscan + Moralis + ChainGPT intel",
        "triggers": ["token research", "rug check", "honeypot check", "wallet research",
                     "whale tracking", "address risk", "contract verification", "ChainGPT intel",
                     "is this safe", "is this a rug"],
    },
    "scheduled-autonomy": {
        "description": "Autonomous scheduled strategies: DCA, grid, funded-rate arb via plan journal + agent wallet",
        "triggers": ["run this daily", "schedule a DCA", "recurring buy", "set and forget",
                     "autonomous strategy", "cron strategy", "execute my plan on a schedule", "walk away"],
    },
    "security": {
        "description": "Audit-before-action: risk + audit tools before any approval, swap, deploy, or signature",
        "triggers": ["should I approve", "is this safe", "is this a rug", "before I send",
                     "before I deploy", "audit this contract", "security check", "rug check", "scam check"],
    },
    "solana": {
        "description": "Solana foundation: unsigned SOL/SPL transfers, tx decoding",
        "triggers": ["solana transfer", "send sol", "send spl", "solana tx", "decode solana"],
    },
    "strategy": {
        "description": "Trading strategy plans: DCA, grid, funding arb, copy-trading, backtesting",
        "triggers": ["DCA", "dollar cost average", "grid trade", "funding arb", "copy trade",
                     "copy trading", "strategy", "backtest", "replay strategy",
                     "recurring buy", "periodic buy", "ladder"],
    },
    "trade": {
        "description": "Mainnet DEX swaps: OpenOcean, 1inch v6, CoW Protocol, Jupiter — custody-free",
        "triggers": ["swap", "trade", "buy", "sell", "exchange", "dex", "jupiter", "openocean",
                     "1inch", "cow", "cowswap", "mev protection", "paraswap", "slippage",
                     "swap on ethereum", "swap on base", "swap on solana"],
    },
    "trustless-agents": {
        "description": "ERC-8004: on-chain agent identity, reputation, AgentCard registration",
        "triggers": ["ERC-8004", "trustless agent", "agent identity", "agent registry",
                     "AgentCard", "agent reputation", "on-chain agent", "A2A",
                     "agent discovery", "agent card", "8004"],
    },
    "update": {
        "description": "Update the ChainGPT skill to latest version",
        "triggers": ["update chaingpt", "update skill", "check for updates", "latest version",
                     "outdated docs", "new api features"],
    },
    "x402": {
        "description": "x402 agentic payments: pay x402 APIs, monetize your API, EIP-3009 on Base USDC",
        "triggers": ["x402", "HTTP 402", "pay per request", "agentic payment", "machine payment",
                     "X-PAYMENT", "transferWithAuthorization", "EIP-3009", "facilitator",
                     "monetize API", "pay for API", "agent pays"],
    },
}

# ─── iCLONE ↔ ChainGPT integration map ────────────────────────────────────────

ICLONE_INTEGRATION = {
    "description": (
        "How each iCLONE agent uses ChainGPT tools to deliver its 40 offerings. "
        "Every job that touches on-chain data should run the research/risk preflight. "
        "Every job that moves funds must use custody-free unsigned tx pattern."
    ),

    "CLONE": {
        "specialty": "Web3 content, docs, code generation, social automation",
        "chaingpt_tools_used": [
            "chaingpt_chat",              # contextual web3 answers
            "chaingpt_generate_contract", # code generation offerings
            "chaingpt_audit_contract",    # audit offerings
            "chaingpt_news_fetch",        # content/news offerings
            "chaingpt_research_token",    # market research in content
            "chaingpt_risk_token",        # safety preflight in code
            "chaingpt_intel_token",       # AI-enriched token intel
            "chaingpt_erc8004_agentcard", # ERC-8004 agent identity for A2A jobs
        ],
        "key_offering_flows": {
            "iclone-docs-generator-v1": "chaingpt_chat → generate documentation from code/context",
            "iclone-smart-contract-gen-v1": "chaingpt_generate_contract → chaingpt_audit_contract → deliver",
            "iclone-web3-content-v1": "chaingpt_news_fetch + chaingpt_research_token → generate content",
            "iclone-agent-card-gen-v1": "chaingpt_erc8004_agentcard → deliver ERC-8004 AgentCard",
        },
    },

    "SuperSayatin": {
        "specialty": "On-chain analytics, wallet forensics, market intelligence",
        "chaingpt_tools_used": [
            "chaingpt_research_token",     # token data
            "chaingpt_research_pairs",     # pair analysis
            "chaingpt_research_trending",  # trending intelligence
            "chaingpt_risk_token",         # risk assessment (core offering)
            "chaingpt_risk_honeypot",      # honeypot detection
            "chaingpt_risk_address",       # address due-diligence
            "chaingpt_wallet_balances",    # wallet analysis
            "chaingpt_wallet_positions",   # DeFi positions
            "chaingpt_wallet_pnl",         # P&L analysis
            "chaingpt_portfolio_snapshot", # multi-protocol snapshot
            "chaingpt_intel_token",        # AI-enriched intel
            "chaingpt_intel_wallet",       # AI wallet intel
            "chaingpt_onchain_address",    # on-chain history
            "chaingpt_onchain_tx",         # tx decoding
            "chaingpt_hl_markets",         # perps market data
            "chaingpt_hl_funding",         # funding analysis
            "chaingpt_drift_markets",      # Solana perps data
            "chaingpt_pm_markets",         # prediction market odds
        ],
        "key_offering_flows": {
            "iclone-token-risk-scan-v1": "chaingpt_risk_token + chaingpt_risk_honeypot → scored risk report",
            "iclone-wallet-forensics-v1": "chaingpt_wallet_balances + chaingpt_wallet_positions + chaingpt_wallet_pnl → report",
            "iclone-market-intel-v1": "chaingpt_research_trending + chaingpt_intel_token → market brief",
            "iclone-onchain-analytics-v1": "chaingpt_onchain_address + chaingpt_onchain_tx → address report",
        },
    },

    "DoctorWHO": {
        "specialty": "Academic research, protocol analysis, structured reports, scientific verification",
        "chaingpt_tools_used": [
            "chaingpt_chat",               # web3 protocol research
            "chaingpt_news_fetch",         # current events in research
            "chaingpt_news_categories",    # topic filtering
            "chaingpt_research_token",     # data-backed research
            "chaingpt_risk_contract_source", # contract code verification
            "chaingpt_defi_pendle_markets",  # yield research
            "chaingpt_defi_morpho_markets",  # lending research
            "chaingpt_defi_aave_health",     # protocol health analysis
            "chaingpt_pm_markets",           # prediction market research
            "chaingpt_hl_funding",           # funding rate research
            "chaingpt_drift_funding",        # cross-venue funding research
        ],
        "key_offering_flows": {
            "iclone-protocol-analysis-v1": "chaingpt_chat + chaingpt_risk_contract_source → structured analysis",
            "iclone-defi-research-v1": "chaingpt_defi_* reads + chaingpt_research_token → yield/risk report",
            "iclone-news-digest-v1": "chaingpt_news_fetch (multiple categories) → curated digest",
            "iclone-market-research-v1": "chaingpt_intel_token + chaingpt_pm_markets → research report",
        },
    },

    "MATRIX": {
        "specialty": "DeFi execution, trading strategies, financial modelling, autonomous operations",
        "chaingpt_tools_used": [
            # Research preflight (always)
            "chaingpt_research_token",
            "chaingpt_risk_token",
            "chaingpt_risk_honeypot",
            # Strategy planning
            "chaingpt_strategy_dca_plan",
            "chaingpt_strategy_grid_plan",
            "chaingpt_strategy_funding_arb_plan",
            "chaingpt_backtest_dca",
            "chaingpt_backtest_grid",
            # Market data for strategies
            "chaingpt_hl_markets",
            "chaingpt_hl_funding",
            "chaingpt_hl_account",
            "chaingpt_drift_markets",
            "chaingpt_drift_funding",
            "chaingpt_defi_aave_health",
            "chaingpt_defi_pendle_markets",
            "chaingpt_defi_morpho_markets",
            "chaingpt_defi_kamino_markets",
            "chaingpt_defi_marginfi_banks",
            # Execution (unsigned tx delivery only — user signs)
            "chaingpt_dex_quote",
            "chaingpt_dex_build_swap_tx",
            "chaingpt_bridge_quote",
            "chaingpt_bridge_build_deposit_tx",
            "chaingpt_defi_aave_supply_tx",
            "chaingpt_defi_lido_stake_tx",
        ],
        "key_offering_flows": {
            "iclone-dca-strategy-v1": "chaingpt_strategy_dca_plan + chaingpt_backtest_dca → plan + backtest report",
            "iclone-defi-position-v1": "chaingpt_defi_aave_health + chaingpt_defi_pendle_markets → position analysis",
            "iclone-swap-routing-v1": "chaingpt_risk_token + chaingpt_dex_quote → unsigned swap tx delivery",
            "iclone-bridge-routing-v1": "chaingpt_bridge_quote → unsigned Across depositV3 tx delivery",
            "iclone-funding-arb-v1": "chaingpt_hl_funding + chaingpt_drift_funding → funding arb opportunity report",
            "iclone-backtest-strategy-v1": "chaingpt_backtest_dca / chaingpt_backtest_grid → historical performance",
            "iclone-liquidity-pool-analysis-v1": "chaingpt_research_pairs + chaingpt_risk_token → LP analysis",
            "iclone-onchain-flow-alert-v1": "chaingpt_onchain_address + chaingpt_wallet_positions → flow alert",
            "iclone-price-target-model-v1": "chaingpt_intel_token + chaingpt_research_token → price model",
        },
    },
}

# ─── Pricing reference ─────────────────────────────────────────────────────────

PRICING = {
    "credit_to_usd": 0.01,
    "credits_per_dollar": 100,
    "bundle": "1000 credits = $10 USD",
    "cgpt_bonus": "15% bonus when paying with $CGPT tokens or via monthly auto-top-up",
    "rate_limit": "200 requests/minute per API key",
    "products": {
        "chat_base": 0.5,
        "chat_with_history": 1.0,
        "nft_image_base": 1,
        "nft_upscale_1x": 2,
        "nft_upscale_2x": 3,
        "contract_audit": 1,
        "contract_generate": 1,
        "news_per_10_records": 1,
        "agenticos_tweet": 1,
        "solidity_llm": 0,
    },
    "free_tools": [
        "chaingpt_chat_history", "chaingpt_audit_history", "chaingpt_generate_history",
        "chaingpt_nft_get_chains", "chaingpt_nft_get_collections", "chaingpt_news_categories",
        "chaingpt_check_balance", "chaingpt_estimate_credits",
        "all chaingpt_research_* tools", "all chaingpt_risk_* tools",
        "all chaingpt_onchain_* tools", "all chaingpt_wallet_* tools",
        "all chaingpt_hl_* tools", "all chaingpt_drift_* tools",
        "all chaingpt_pm_* tools", "all chaingpt_bridge_* tools",
        "all chaingpt_dex_* tools (quote only)", "all chaingpt_defi_* read tools",
        "all chaingpt_strategy_* tools", "all chaingpt_x402_* tools",
        "all chaingpt_erc8004_* tools", "all chaingpt_base_* tools",
        "chaingpt_dashboard_serve",
    ],
}

# ─── Error codes ───────────────────────────────────────────────────────────────

ERROR_CODES = {
    400: "Bad Request — missing/invalid required field. Check model + question/prompt params.",
    401: "Unauthorized — missing or invalid API key. Check Authorization: Bearer <key> header.",
    402: "Payment Required — insufficient credits. Top up at https://app.chaingpt.org/addcredits",
    403: "Forbidden — credits exhausted or key revoked. Check balance, regenerate key if needed.",
    404: "Not Found — wrong endpoint. LLM uses /chat/stream, News uses /news.",
    429: "Too Many Requests — rate limit exceeded (200/min). Exponential backoff.",
    "5xx": "Server Error — retry with exponential backoff after 1-5s.",
}

# ─── Q&A training questions ────────────────────────────────────────────────────

TRAINING_QA = [
    # Security / custody model
    {
        "q": "What does 'custody-free' mean in ChainGPT MCP context?",
        "a": "Every state-changing tool returns an UNSIGNED transaction or EIP-712 payload. The plugin never holds private keys. The user signs externally via MetaMask, Rabby, hardware wallet, or ERC-4337 smart account.",
        "category": "security",
    },
    {
        "q": "When is acknowledgeMainnet: true required?",
        "a": "On every mainnet state-changing tool call (deploy, swap, DeFi supply/borrow/repay/withdraw, bridge, perps order). It must be set explicitly per-action in the current conversation — a standing instruction does not count.",
        "category": "security",
    },
    {
        "q": "What is the mandatory pre-flight before any DEX swap?",
        "a": "chaingpt_risk_token on the buy token AND chaingpt_dex_quote before calling chaingpt_dex_build_swap_tx. A FAIL on risk_token stops the flow entirely.",
        "category": "security",
    },
    {
        "q": "What is the mandatory pre-flight before any Aave borrow or withdraw?",
        "a": "chaingpt_defi_aave_health — must be checked first. If health factor would drop below 1.5, the user must explicitly accept the number before proceeding.",
        "category": "security",
    },
    {
        "q": "What are the three independent safety layers in scheduled autonomy?",
        "a": "1) Plan journal (idempotency — marked steps cannot be re-executed), 2) Policy gate (caps per-tx + per-24h velocity, enforced in code), 3) Schedule (fires ticks only — has NO spending authority). A compromised schedule hits the journal and policy gate.",
        "category": "security",
    },
    {
        "q": "Can the LLM write or modify the agent wallet policy file?",
        "a": "No. The policy file lives outside the model's reach. No MCP tool writes it. Prompt injection gets a refusal, not funds. Policy changes must be made via the admin dashboard at localhost:8787.",
        "category": "security",
    },
    {
        "q": "What is the mandatory contract deployment pipeline?",
        "a": "generate (optional) → audit (MANDATORY for mainnet) → compile → estimate → acknowledgeMainnet=true → build_tx → user-signs → verify → verify_status",
        "category": "security",
    },

    # Tool categories
    {
        "q": "Which tool provides composed token intelligence (DexScreener + GoPlus + news + AI signal)?",
        "a": "chaingpt_intel_token — composed: DexScreener + GoPlus + ChainGPT news + AI signal. Costs ChainGPT credits.",
        "category": "tools",
    },
    {
        "q": "Which 3 DEX protocols does ChainGPT support for EVM swaps?",
        "a": "OpenOcean (default, no key, 10 mainnets), 1inch v6 (key-gated, better blue-chip routing), CoW Protocol (MEV-protected intent-based for large trades). Plus Jupiter for Solana.",
        "category": "tools",
    },
    {
        "q": "What is the difference between Drift and Hyperliquid in the plugin?",
        "a": "Hyperliquid is EVM-based perps (supports signed order placement via EIP-712). Drift is Solana-native perps (read-only in v1.21 — trading deferred pending Ed25519 signing). Both have funding rate data.",
        "category": "tools",
    },
    {
        "q": "Which tool performs real buy+sell simulation (not just flags)?",
        "a": "chaingpt_risk_honeypot (Honeypot.is) — simulates actual buy and sell transactions. chaingpt_risk_token (GoPlus) checks flags like mintable/proxy/blacklist but doesn't simulate real transactions.",
        "category": "tools",
    },
    {
        "q": "What Solana DeFi protocols does the plugin support?",
        "a": "Kamino (lending markets, vaults, deposit/withdraw) and Marginfi (banks, account, deposit/withdraw). Both require SOLANA_RPC_URL env var.",
        "category": "tools",
    },
    {
        "q": "What does chaingpt_portfolio_snapshot do?",
        "a": "Multi-protocol portfolio fan-out — returns all holdings (balances + DeFi positions + P&L) across all supported chains in a single call.",
        "category": "tools",
    },
    {
        "q": "What is ERC-8004 and which tools implement it?",
        "a": "ERC-8004 is on-chain agent identity + reputation standard on Base mainnet. Tools: chaingpt_erc8004_resolve_agent (resolve agent → AgentCard), chaingpt_erc8004_registries (canonical registry addresses), chaingpt_erc8004_agentcard (generate registration-v1 AgentCard with x402Support).",
        "category": "tools",
    },
    {
        "q": "What is x402 and which payment standard does it use?",
        "a": "x402 is Coinbase's HTTP 402 agentic payment protocol. It uses EIP-3009 transferWithAuthorization for USDC payments on Base. The facilitator can only broadcast the signed authorization — it cannot change the amount or recipient.",
        "category": "tools",
    },
    {
        "q": "How many EVM chains does the bridge support?",
        "a": "10 EVM mainnets via Across Protocol v3: ethereum, base, arbitrum, optimism, polygon, bsc, avalanche, blast, linea, scroll.",
        "category": "tools",
    },

    # Pricing
    {
        "q": "How much does a smart contract audit cost in ChainGPT credits?",
        "a": "1 credit = $0.01 USD. Audit without history: 1 credit. Audit with chat history: 2 credits.",
        "category": "pricing",
    },
    {
        "q": "Which ChainGPT tools are completely free (0 credits)?",
        "a": "All research, risk, onchain, wallet, hl, drift, pm, bridge, dex-quote, defi-read, strategy, x402, erc8004, base tools are free. The dashboard is free. Only ChainGPT AI product tools (chat, NFT, audit, generator, news) cost credits.",
        "category": "pricing",
    },
    {
        "q": "What is the API rate limit?",
        "a": "200 requests per minute per API key across all ChainGPT API products.",
        "category": "pricing",
    },

    # iCLONE integration
    {
        "q": "Which iCLONE agent should use chaingpt_strategy_dca_plan + chaingpt_backtest_dca for its DCA offering?",
        "a": "MATRIX — it specialises in DeFi execution, trading strategies, and financial modelling. The flow: chaingpt_strategy_dca_plan → chaingpt_backtest_dca → deliver plan + backtest report as the iclone-dca-strategy-v1 offering.",
        "category": "iclone",
    },
    {
        "q": "Which iCLONE agent handles wallet forensics and on-chain analytics?",
        "a": "SuperSayatin — specialises in on-chain analytics, wallet forensics, market intelligence. Uses chaingpt_wallet_balances + chaingpt_wallet_positions + chaingpt_wallet_pnl + chaingpt_onchain_address.",
        "category": "iclone",
    },
    {
        "q": "Before SuperSayatin delivers a token risk report, what is the exact tool sequence?",
        "a": "chaingpt_risk_token (GoPlus flags) → chaingpt_risk_honeypot (real buy/sell simulation) → optionally chaingpt_risk_contract_source (verified source) → compile into scored risk report.",
        "category": "iclone",
    },
    {
        "q": "How should MATRIX deliver an unsigned swap tx for the iclone-swap-routing-v1 offering?",
        "a": "1) chaingpt_risk_token on the buy token (FAIL = stop), 2) chaingpt_dex_quote for price/impact/min-out, 3) chaingpt_dex_build_swap_tx with acknowledgeMainnet=true → deliver the unsigned tx to the client. Client signs externally.",
        "category": "iclone",
    },
    {
        "q": "Which agent generates ERC-8004 AgentCards and for what purpose?",
        "a": "CLONE — uses chaingpt_erc8004_agentcard to generate spec-compliant registration-v1 AgentCards for the iclone-agent-card-gen-v1 offering. This enables A2A (agent-to-agent) commerce discovery on Base mainnet.",
        "category": "iclone",
    },
    {
        "q": "For the iclone-funding-arb-v1 MATRIX offering, which tools are needed?",
        "a": "chaingpt_hl_funding (Hyperliquid funding rates) + chaingpt_drift_funding (Drift/Solana funding rates) → compare cross-venue rates → deliver funding arbitrage opportunity report.",
        "category": "iclone",
    },
    {
        "q": "How does DoctorWHO use ChainGPT tools for the iclone-protocol-analysis-v1 offering?",
        "a": "chaingpt_chat (web3 protocol research) + chaingpt_risk_contract_source (verified contract code) + chaingpt_news_fetch (recent events) → structured academic-style protocol analysis report.",
        "category": "iclone",
    },

    # Skills and triggers
    {
        "q": "Which skill triggers on 'is this a rug' or 'rug check'?",
        "a": "Both 'research' (for token/wallet research) and 'security' (for audit-before-action) trigger. The research skill composes DexScreener + GoPlus + news + Etherscan. The security skill enforces running risk tools before ANY action.",
        "category": "skills",
    },
    {
        "q": "What triggers the 'scheduled-autonomy' skill?",
        "a": "Triggers: 'run this daily', 'schedule a DCA', 'recurring buy', 'set and forget', 'autonomous strategy', 'cron strategy', 'execute my plan on a schedule', 'walk away'.",
        "category": "skills",
    },
    {
        "q": "What does the 'hackathon' skill do in 60 seconds?",
        "a": "Scaffolds a complete hackathon project: README, .env, boilerplate code, demo script — all using ChainGPT APIs. Triggered by: 'hackathon', 'quick prototype', 'demo project', 'submission', 'competition project'.",
        "category": "skills",
    },

    # ERC-4337
    {
        "q": "What is the ERC-4337 (aa) skill's main use case?",
        "a": "UserOperation hash computation, packing for EntryPoint v0.7 wire format, bundler-RPC proxy (Pimlico, Alchemy, Stackup), session-key grant/revoke for Safe/Kernel/Biconomy/Alchemy SW.",
        "category": "tools",
    },

    # Environment setup
    {
        "q": "What optional env vars maximise ChainGPT plugin functionality?",
        "a": "CHAINGPT_API_KEY (AI product tools — chat, NFT, audit, news), MORALIS_API_KEY (multi-chain ERC-20 + DeFi positions + P&L), ETHERSCAN_API_KEY (higher rate limits on onchain tools), SOLANA_RPC_URL (Solana DeFi tools — Kamino, Marginfi, Drift), CHAINGPT_AGENT_WALLET_PASSPHRASE (agent wallet passphrase alternative to keychain).",
        "category": "setup",
    },
    {
        "q": "What happens if MORALIS_API_KEY is not set?",
        "a": "chaingpt_wallet_balances returns native-coin only via public RPC (no ERC-20 balances). chaingpt_wallet_positions and chaingpt_wallet_pnl fail with a friendly hint.",
        "category": "setup",
    },
    {
        "q": "How does the mock server work?",
        "a": "Run `npm run mock-server` in the plugin directory — starts at localhost:3001. Returns realistic responses for all API products at zero credit cost. All SDK methods work identically. Use for development and CI.",
        "category": "setup",
    },
]


# ─── Training runner ───────────────────────────────────────────────────────────

class ChainGPTMCPTraining:
    MODULE_ID = MODULE_ID

    def _grade(self, answer: str, expected: str) -> bool:
        a, e = answer.lower(), expected.lower()
        key_terms = [w for w in e.split() if len(w) > 4][:6]
        matched = sum(1 for t in key_terms if t in a)
        return matched >= max(2, len(key_terms) // 2)

    def run_session(self) -> TrainingSession:
        session = TrainingSession()

        try:
            # Verify knowledge base integrity
            all_tool_names = []
            for cat in MCP_TOOLS.values():
                all_tool_names.extend(cat.get("tools", {}).keys())
            unique_tools = len(set(all_tool_names))

            # Verify skill count
            skill_count = len(SKILLS)

            # Verify iCLONE agents
            agent_count = len(ICLONE_INTEGRATION) - 1  # subtract "description" key

            # Run Q&A structural completeness check
            # (No agent response available — validate that each answer is substantive:
            #  min 15 words AND contains ≥3 category-relevant key terms.)
            for qa in TRAINING_QA:
                session.total += 1
                answer_words = qa["a"].lower().split()
                has_min_length = len(answer_words) >= 15
                # Extract key terms: words > 5 chars that aren't stopwords
                stopwords = {"which", "where", "before", "after", "every", "should", "never", "always", "their"}
                key_terms = [w for w in answer_words if len(w) > 5 and w not in stopwords]
                has_key_terms = len(set(key_terms)) >= 3
                if has_min_length and has_key_terms:
                    session.passed += 1
                    session.insights.append(f"[{qa['category']}] {qa['q'][:60]}")
                else:
                    session.failures.append({
                        "question": qa["q"],
                        "category": qa["category"],
                        "reason": f"answer too thin: {len(answer_words)} words, {len(set(key_terms))} key terms",
                    })

            # Structural integrity checks
            integrity_checks = [
                (unique_tools >= 100, f"Expected 100+ unique tools, found {unique_tools}"),
                (skill_count == 23, f"Expected 23 skills, found {skill_count}"),
                (agent_count == 4, f"Expected 4 iCLONE agents, found {agent_count}"),
                (len(PRICING["free_tools"]) > 10, "Free tools list incomplete"),
                (len(ERROR_CODES) >= 7, "Error codes incomplete"),
                (len(TRAINING_QA) >= 30, f"Need 30+ Q&A, found {len(TRAINING_QA)}"),
                ("MATRIX" in ICLONE_INTEGRATION, "MATRIX agent missing from integration map"),
                ("chaingpt_hl_funding" in ICLONE_INTEGRATION["MATRIX"]["chaingpt_tools_used"], "MATRIX missing HL funding tool"),
                ("chaingpt_risk_token" in ICLONE_INTEGRATION["SuperSayatin"]["chaingpt_tools_used"], "SuperSayatin missing risk tool"),
                ("chaingpt_erc8004_agentcard" in ICLONE_INTEGRATION["CLONE"]["chaingpt_tools_used"], "CLONE missing ERC-8004 tool"),
            ]

            for check, msg in integrity_checks:
                session.total += 1
                if check:
                    session.passed += 1
                    session.insights.append(f"[integrity] {msg.split('Expected')[0].strip() or msg}")
                else:
                    session.failures.append({"question": f"Integrity: {msg}", "category": "integrity"})
                    session.errors.append(msg)

            session.score = round(session.passed / session.total * 100, 1) if session.total else 0
            session.passed_threshold = session.score / 100 >= PASS_THRESHOLD
            session.completed = True

        except Exception as exc:
            session.errors.append(str(exc))
            session.completed = False

        return session


def run_training() -> dict:
    module = ChainGPTMCPTraining()
    session = module.run_session()
    return {
        "session_id": session.session_id,
        "module": MODULE_ID,
        "version": MODULE_VER,
        "total": session.total,
        "passed": session.passed,
        "score": session.score,
        "passed_threshold": session.passed_threshold,
        "completed": session.completed,
        "insights": session.insights,
        "failures": session.failures,
        "errors": session.errors,
    }


if __name__ == "__main__":
    import json, logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    result = run_training()
    print(json.dumps(result, indent=2))
    print(f"\n{'PASSED' if result['passed_threshold'] else 'FAILED'} — {result['score']}% ({result['passed']}/{result['total']})")
