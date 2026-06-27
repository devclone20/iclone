"""
ACP Resources — APIs que o iCLONE usa para executar os seus jobs.
Schema validado: 2026-06-11
"""

ICLONE_RESOURCES = [
    # ── WEB RESEARCH ──────────────────────────────────────────────────────────
    {
        "name": "web_search",
        "description": "Search the web for any query. Returns top results with titles, URLs, and snippets. Used by all webResearch jobs.",
        "url": "https://api.search.brave.com/res/v1/web/search",
        "params": {
            "type": "object",
            "properties": {
                "q": {"type": "string", "description": "Search query"},
                "count": {"type": "number", "description": "Number of results (max 20)"},
                "freshness": {"type": "string", "description": "Time filter: pd (24h), pw (week), pm (month)"}
            },
            "required": ["q"]
        }
    },
    {
        "name": "get_webpage_content",
        "description": "Fetch and extract clean text content from any URL. Used to read full articles during deep research.",
        "url": "https://r.jina.ai/{{url}}",
        "params": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to extract content from"}
            },
            "required": ["url"]
        }
    },

    # ── CRYPTO & MARKET DATA ──────────────────────────────────────────────────
    {
        "name": "get_crypto_price",
        "description": "Get current price, market cap, volume, and 24h change for any crypto asset by symbol or ID.",
        "url": "https://api.coingecko.com/api/v3/simple/price",
        "params": {
            "type": "object",
            "properties": {
                "ids": {"type": "string", "description": "CoinGecko asset ID (e.g. bitcoin, ethereum, solana)"},
                "vs_currencies": {"type": "string", "description": "Quote currency (e.g. usd)"},
                "include_market_cap": {"type": "boolean"},
                "include_24hr_vol": {"type": "boolean"},
                "include_24hr_change": {"type": "boolean"}
            },
            "required": ["ids", "vs_currencies"]
        }
    },
    {
        "name": "get_crypto_market_data",
        "description": "Get detailed market data for a crypto asset including OHLCV, supply, ATH, rank. Used by cryptoResearch jobs.",
        "url": "https://api.coingecko.com/api/v3/coins/{{id}}",
        "params": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "CoinGecko asset ID"},
                "localization": {"type": "boolean", "description": "Include localized data"},
                "tickers": {"type": "boolean"},
                "market_data": {"type": "boolean"},
                "community_data": {"type": "boolean"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "get_defi_protocols",
        "description": "Get list of DeFi protocols with TVL, APY, and chain data from DeFiLlama. Used by defiOpportunityScanner.",
        "url": "https://api.llama.fi/protocols",
        "params": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_defi_yields",
        "description": "Get yield farming opportunities across all DeFi protocols and chains. Filter by APY and chain.",
        "url": "https://yields.llama.fi/pools",
        "params": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_token_price_history",
        "description": "Get historical price data for a crypto asset. Used for performance analysis in walletDeepAnalysis.",
        "url": "https://api.coingecko.com/api/v3/coins/{{id}}/market_chart",
        "params": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "CoinGecko asset ID"},
                "vs_currency": {"type": "string", "description": "Quote currency"},
                "days": {"type": "number", "description": "Number of days of data"}
            },
            "required": ["id", "vs_currency", "days"]
        }
    },

    # ── WALLET & ON-CHAIN ─────────────────────────────────────────────────────
    {
        "name": "get_wallet_token_balances",
        "description": "Get all ERC-20 token balances for any EVM wallet address. Supports Ethereum, Base, Polygon, BSC.",
        "url": "https://api.zerion.io/v1/wallets/{{address}}/positions/",
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "EVM wallet address (0x...)"},
                "filter[position_types]": {"type": "string", "description": "Filter: wallet, deposited, borrowed, locked"},
                "currency": {"type": "string", "description": "Quote currency (usd)"}
            },
            "required": ["address"]
        }
    },
    {
        "name": "get_wallet_transaction_history",
        "description": "Get transaction history for any EVM wallet. Used by walletDeepAnalysis for PnL calculation.",
        "url": "https://api.zerion.io/v1/wallets/{{address}}/transactions/",
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "EVM wallet address"},
                "currency": {"type": "string", "description": "Quote currency"},
                "page[size]": {"type": "number", "description": "Results per page (max 100)"}
            },
            "required": ["address"]
        }
    },
    {
        "name": "get_token_approvals",
        "description": "Get all active token approvals (allowances) for a wallet. Used by walletHealthCheck to detect risky approvals.",
        "url": "https://api.zerion.io/v1/wallets/{{address}}/positions/?filter[position_types]=wallet",
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "EVM wallet address to audit"}
            },
            "required": ["address"]
        }
    },

    # ── ACP / VIRTUALS PROTOCOL ───────────────────────────────────────────────
    {
        "name": "get_acp_agents",
        "description": "Browse all agents on the Virtuals ACP marketplace. Filter by keyword, cluster, or chain. Used for multiAgentCoordination and clonePlatformOnboarding.",
        "url": "https://api.virtuals.io/api/agents",
        "params": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword for agent name or capability"},
                "cluster": {"type": "string", "description": "Agent cluster filter"},
                "limit": {"type": "number", "description": "Max results to return"}
            },
            "required": []
        }
    },
    {
        "name": "get_agent_offerings",
        "description": "Get all job offerings from a specific ACP agent by wallet address. Used for agent research and coordination.",
        "url": "https://api.virtuals.io/api/agents/{{walletAddress}}/offerings",
        "params": {
            "type": "object",
            "properties": {
                "walletAddress": {"type": "string", "description": "Agent wallet address"}
            },
            "required": ["walletAddress"]
        }
    },

    # ── CODE & DEVELOPMENT ────────────────────────────────────────────────────
    {
        "name": "execute_code_sandbox",
        "description": "Execute code in a sandboxed environment. Supports Python, JavaScript, TypeScript. Returns stdout, stderr, and result. Used by codeGenerate and bugFix jobs.",
        "url": "https://emkc.org/api/v2/piston/execute",
        "params": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Programming language (python, javascript, typescript, etc.)"},
                "version": {"type": "string", "description": "Language version (e.g. 3.10)"},
                "files": {
                    "type": "array",
                    "description": "Array of {name, content} file objects",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    }
                },
                "stdin": {"type": "string", "description": "Standard input for the program"}
            },
            "required": ["language", "files"]
        }
    },
    {
        "name": "validate_json_schema",
        "description": "Validate a JSON document against a JSON Schema. Returns validation result and errors. Used by pdfToStructuredJson and csvCleanerAndNormalizer.",
        "url": "https://www.jsonschemavalidator.net/api/validate",
        "params": {
            "type": "object",
            "properties": {
                "schema": {"type": "object", "description": "JSON Schema definition"},
                "data": {"type": "object", "description": "JSON data to validate"}
            },
            "required": ["schema", "data"]
        }
    },

    # ── CONTENT & SEO ─────────────────────────────────────────────────────────
    {
        "name": "get_trending_topics",
        "description": "Get currently trending topics on social media and news for a given category. Used by newsletterDigest and cryptoThread jobs.",
        "url": "https://api.thenewsapi.com/v1/news/top",
        "params": {
            "type": "object",
            "properties": {
                "categories": {"type": "string", "description": "Comma-separated categories (e.g. business,tech,crypto)"},
                "language": {"type": "string", "description": "Language code (en, pt, es)"},
                "limit": {"type": "number", "description": "Number of articles (max 50)"},
                "published_after": {"type": "string", "description": "ISO date filter (e.g. 2026-06-01)"}
            },
            "required": ["categories"]
        }
    },
    {
        "name": "get_seo_keywords",
        "description": "Get SEO keyword data including search volume, difficulty, and related keywords. Used by blogPostGenerator.",
        "url": "https://api.datamuse.com/words",
        "params": {
            "type": "object",
            "properties": {
                "ml": {"type": "string", "description": "Means like — find related keywords"},
                "rel_trg": {"type": "string", "description": "Triggered by — find associated terms"},
                "max": {"type": "number", "description": "Max results (default 10)"}
            },
            "required": []
        }
    },

    # ── ICLONE INTERNAL ───────────────────────────────────────────────────────
    {
        "name": "get_iclone_agent_status",
        "description": "Get current status, active jobs, wallet balance, and reputation score of the iCLONE agent on ACP.",
        "url": "https://api.virtuals.io/api/agents/{{clientAddress}}",
        "params": {
            "type": "object",
            "properties": {
                "clientAddress": {"type": "string", "description": "iCLONE agent wallet address"}
            },
            "required": ["clientAddress"]
        }
    }
]
