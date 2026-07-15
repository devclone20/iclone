"""
ACP Resources v2 — Lista completa para todos os jobs actuais e futuros do iCLONE.
Inclui: web research, crypto, DeFi, wallets, código, conteúdo, ACP, trading,
        automação, PDFs, dados, agentes, identidade, notificações.
Validado: 2026-06-11
"""

ICLONE_RESOURCES_V2 = [

    # ═══════════════════════════════════════════════════════════════
    # 1. WEB RESEARCH & CONTENT EXTRACTION
    # Jobs: webResearchQuick, webResearchStandard, webResearchDeep
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "web_search",
        "description": "Search the web for any query. Returns top results with titles, URLs, and snippets. Core tool for all webResearch jobs.",
        "url": "https://api.search.brave.com/res/v1/web/search",
        "params": {
            "type": "object",
            "properties": {
                "q": {"type": "string", "description": "Search query"},
                "count": {"type": "number", "description": "Number of results (max 20)"},
                "freshness": {"type": "string", "description": "Time filter: pd=24h, pw=week, pm=month"}
            },
            "required": ["q"]
        }
    },
    {
        "name": "get_webpage_content",
        "description": "Fetch and extract clean markdown text from any URL. Used for reading full articles, documentation, and pages during deep research.",
        "url": "https://r.jina.ai/{{url}}",
        "params": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Full URL to extract content from"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "search_news",
        "description": "Search recent news articles by keyword, category, or date. Returns headlines, summaries, sources. Used for newsletters, crypto threads, and market research.",
        "url": "https://api.thenewsapi.com/v1/news/all",
        "params": {
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "Keyword to search"},
                "categories": {"type": "string", "description": "Comma-separated: business, tech, crypto, science"},
                "language": {"type": "string", "description": "Language code: en, pt, es"},
                "limit": {"type": "number", "description": "Max articles (max 50)"},
                "published_after": {"type": "string", "description": "ISO date e.g. 2026-06-01"}
            },
            "required": ["search"]
        }
    },
    {
        "name": "get_top_news",
        "description": "Get top trending news headlines by category. Used by newsletterDigest and cryptoThread jobs to find viral content.",
        "url": "https://api.thenewsapi.com/v1/news/top",
        "params": {
            "type": "object",
            "properties": {
                "categories": {"type": "string", "description": "Comma-separated categories"},
                "language": {"type": "string", "description": "Language code"},
                "limit": {"type": "number", "description": "Number of articles"}
            },
            "required": ["categories"]
        }
    },
    {
        "name": "get_wikipedia_summary",
        "description": "Get a concise Wikipedia summary for any topic, person, or concept. Useful for background context in research and blog posts.",
        "url": "https://en.wikipedia.org/api/rest_v1/page/summary/{{title}}",
        "params": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Wikipedia page title (URL-encoded)"}
            },
            "required": ["title"]
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 2. CRYPTO MARKET DATA
    # Jobs: cryptoResearchQuick, cryptoResearchDeep, cryptoThread*,
    #       defiOpportunityScanner, priceMonitor
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "get_crypto_price",
        "description": "Get real-time price, market cap, volume, and 24h change for any crypto asset. Supports multiple assets and currencies simultaneously.",
        "url": "https://api.coingecko.com/api/v3/simple/price",
        "params": {
            "type": "object",
            "properties": {
                "ids": {"type": "string", "description": "Comma-separated CoinGecko IDs (e.g. bitcoin,ethereum,solana)"},
                "vs_currencies": {"type": "string", "description": "Quote currencies (e.g. usd,eur)"},
                "include_market_cap": {"type": "boolean"},
                "include_24hr_vol": {"type": "boolean"},
                "include_24hr_change": {"type": "boolean"},
                "include_last_updated_at": {"type": "boolean"}
            },
            "required": ["ids", "vs_currencies"]
        }
    },
    {
        "name": "get_crypto_market_data",
        "description": "Get full market data for a crypto asset: OHLCV, circulating supply, ATH, rank, sentiment, developer activity. Used for deep crypto research.",
        "url": "https://api.coingecko.com/api/v3/coins/{{id}}",
        "params": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "CoinGecko asset ID"},
                "localization": {"type": "boolean"},
                "tickers": {"type": "boolean"},
                "market_data": {"type": "boolean"},
                "community_data": {"type": "boolean"},
                "developer_data": {"type": "boolean"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "get_crypto_price_history",
        "description": "Get historical OHLCV price data for any crypto asset. Used for performance analysis, trend identification, and PnL calculations.",
        "url": "https://api.coingecko.com/api/v3/coins/{{id}}/market_chart",
        "params": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "CoinGecko asset ID"},
                "vs_currency": {"type": "string", "description": "Quote currency"},
                "days": {"type": "number", "description": "Number of days (1, 7, 14, 30, 90, 180, 365, max)"},
                "interval": {"type": "string", "description": "Data interval: daily, hourly"}
            },
            "required": ["id", "vs_currency", "days"]
        }
    },
    {
        "name": "get_crypto_markets_list",
        "description": "Get list of top crypto assets by market cap with price, volume, and change data. Used for market overviews and opportunity scanning.",
        "url": "https://api.coingecko.com/api/v3/coins/markets",
        "params": {
            "type": "object",
            "properties": {
                "vs_currency": {"type": "string", "description": "Quote currency (usd)"},
                "order": {"type": "string", "description": "Sort order: market_cap_desc, volume_desc, price_change_desc"},
                "per_page": {"type": "number", "description": "Results per page (max 250)"},
                "page": {"type": "number", "description": "Page number"},
                "category": {"type": "string", "description": "Filter by category: defi, layer-1, ai-big-data, etc."}
            },
            "required": ["vs_currency"]
        }
    },
    {
        "name": "get_crypto_trending",
        "description": "Get trending crypto assets in the last 24h on CoinGecko. Used for crypto thread content and market sentiment analysis.",
        "url": "https://api.coingecko.com/api/v3/search/trending",
        "params": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_global_crypto_data",
        "description": "Get global crypto market data: total market cap, BTC dominance, active cryptocurrencies, market cap change. Used for macro crypto analysis.",
        "url": "https://api.coingecko.com/api/v3/global",
        "params": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "search_crypto_asset",
        "description": "Search for a crypto asset by name or ticker to get its CoinGecko ID. Use before calling other crypto APIs when only the ticker is known.",
        "url": "https://api.coingecko.com/api/v3/search",
        "params": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Asset name or ticker symbol (e.g. VIRTUAL, ETH, Solana)"}
            },
            "required": ["query"]
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 3. DEFI & YIELD DATA
    # Jobs: defiOpportunityScanner, walletDeepAnalysis, cryptoResearchDeep
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "get_defi_protocols",
        "description": "Get all DeFi protocols listed on DeFiLlama with TVL, chain, category, and change data. Used for DeFi landscape analysis.",
        "url": "https://api.llama.fi/protocols",
        "params": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_defi_protocol_detail",
        "description": "Get detailed TVL history and chain breakdown for a specific DeFi protocol by slug.",
        "url": "https://api.llama.fi/protocol/{{protocol}}",
        "params": {
            "type": "object",
            "properties": {
                "protocol": {"type": "string", "description": "Protocol slug (e.g. uniswap, aave, compound)"}
            },
            "required": ["protocol"]
        }
    },
    {
        "name": "get_defi_yields",
        "description": "Get all yield farming and liquidity pools across DeFi protocols. Filter by chain, project, stablecoin status. Used by defiOpportunityScanner.",
        "url": "https://yields.llama.fi/pools",
        "params": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_defi_chain_tvl",
        "description": "Get current and historical TVL for each blockchain. Used to identify which chains have the most liquidity and activity.",
        "url": "https://api.llama.fi/v2/chains",
        "params": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 4. WALLET & ON-CHAIN ANALYSIS
    # Jobs: walletAnalyzerQuick, walletHealthCheck, walletDeepAnalysis
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "get_wallet_balances",
        "description": "Get all token balances (ERC-20, native) for any EVM wallet across Ethereum, Base, Polygon, BSC, Arbitrum. Returns USD values.",
        "url": "https://api.zerion.io/v1/wallets/{{address}}/positions/",
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "EVM wallet address (0x...)"},
                "filter[position_types]": {"type": "string", "description": "wallet, deposited, borrowed, locked, staked"},
                "currency": {"type": "string", "description": "Quote currency (usd)"},
                "filter[chain_ids]": {"type": "string", "description": "Chain filter: ethereum, base, polygon, arbitrum"}
            },
            "required": ["address"]
        }
    },
    {
        "name": "get_wallet_transactions",
        "description": "Get full transaction history for any EVM wallet including swaps, transfers, DeFi interactions. Used for PnL and activity analysis.",
        "url": "https://api.zerion.io/v1/wallets/{{address}}/transactions/",
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "EVM wallet address"},
                "currency": {"type": "string", "description": "Quote currency"},
                "page[size]": {"type": "number", "description": "Results per page (max 100)"},
                "filter[chain_ids]": {"type": "string", "description": "Chain filter"}
            },
            "required": ["address"]
        }
    },
    {
        "name": "get_wallet_nft_portfolio",
        "description": "Get all NFTs held by a wallet with collection name, floor price, and estimated value. Used in wallet deep analysis.",
        "url": "https://api.zerion.io/v1/wallets/{{address}}/nft-positions/",
        "params": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "EVM wallet address"},
                "currency": {"type": "string", "description": "Quote currency"}
            },
            "required": ["address"]
        }
    },
    {
        "name": "get_ens_name",
        "description": "Resolve an ENS name to an Ethereum address or reverse-resolve an address to ENS. Used for identity display in wallet reports.",
        "url": "https://api.ensideas.com/ens/resolve/{{name}}",
        "params": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "ENS name (e.g. vitalik.eth) or 0x address"}
            },
            "required": ["name"]
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 5. CODE EXECUTION & DEVELOPMENT
    # Jobs: codeGenerateQuick, codeGenerateStandard, bugFixFromErrorTrace,
    #       testGenerator, regexBuilderAndTester, sqlQueryOptimizer
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "execute_code",
        "description": "Execute code in a sandboxed environment. Supports Python, JavaScript, TypeScript, Go, Rust, and 50+ languages. Returns stdout, stderr, exit code.",
        "url": "https://emkc.org/api/v2/piston/execute",
        "params": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Language: python, javascript, typescript, go, rust, bash, etc."},
                "version": {"type": "string", "description": "Language version (e.g. 3.10 for Python)"},
                "files": {
                    "type": "array",
                    "description": "Array of file objects with name and content",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    }
                },
                "stdin": {"type": "string", "description": "Standard input for the program"},
                "args": {"type": "array", "description": "Command line arguments", "items": {"type": "string"}}
            },
            "required": ["language", "files"]
        }
    },
    {
        "name": "get_available_runtimes",
        "description": "Get list of all available language runtimes in the code execution sandbox with versions.",
        "url": "https://emkc.org/api/v2/piston/runtimes",
        "params": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_npm_package_info",
        "description": "Get metadata for any npm package: version, description, dependencies, weekly downloads, repository. Used for dependency analysis in code jobs.",
        "url": "https://registry.npmjs.org/{{package}}",
        "params": {
            "type": "object",
            "properties": {
                "package": {"type": "string", "description": "npm package name (e.g. react, axios, zod)"}
            },
            "required": ["package"]
        }
    },
    {
        "name": "get_pypi_package_info",
        "description": "Get metadata for any Python package from PyPI: version, description, dependencies, author. Used for Python dependency analysis.",
        "url": "https://pypi.org/pypi/{{package}}/json",
        "params": {
            "type": "object",
            "properties": {
                "package": {"type": "string", "description": "PyPI package name (e.g. fastapi, pydantic, numpy)"}
            },
            "required": ["package"]
        }
    },
    {
        "name": "get_github_repo_info",
        "description": "Get public GitHub repository metadata: stars, forks, open issues, language, last commit, README. Used for tech stack analysis and code review context.",
        "url": "https://api.github.com/repos/{{owner}}/{{repo}}",
        "params": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "GitHub username or organisation"},
                "repo": {"type": "string", "description": "Repository name"}
            },
            "required": ["owner", "repo"]
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 6. DATA PROCESSING & FILES
    # Jobs: pdfToStructuredJson, csvCleanerAndNormalizer,
    #       dataFormatConverter, documentationGenerator
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "extract_pdf_text",
        "description": "Extract all text content from a publicly accessible PDF URL. Returns clean text by page. Used by pdfToStructuredJson job.",
        "url": "https://r.jina.ai/{{pdf_url}}",
        "params": {
            "type": "object",
            "properties": {
                "pdf_url": {"type": "string", "description": "Public URL of the PDF file"}
            },
            "required": ["pdf_url"]
        }
    },
    {
        "name": "convert_currency",
        "description": "Convert any amount between currencies or tokens in real time. Used for normalising financial data in CSV and report jobs.",
        "url": "https://api.frankfurter.app/latest",
        "params": {
            "type": "object",
            "properties": {
                "from": {"type": "string", "description": "Source currency (USD, EUR, GBP, BTC)"},
                "to": {"type": "string", "description": "Target currency or comma-separated list"},
                "amount": {"type": "number", "description": "Amount to convert"}
            },
            "required": ["from", "to"]
        }
    },
    {
        "name": "validate_email_address",
        "description": "Validate if an email address is real and deliverable. Used in CSV cleaning and data normalisation jobs.",
        "url": "https://api.mailcheck.ai/email/{{email}}",
        "params": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Email address to validate"}
            },
            "required": ["email"]
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 7. CONTENT, SEO & SOCIAL
    # Jobs: blogPostGenerator, newsletterDigest, cryptoThreadQuick,
    #       cryptoThreadStandard
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "get_related_keywords",
        "description": "Get semantically related keywords and synonyms for any term. Used for SEO optimisation in blog posts and content jobs.",
        "url": "https://api.datamuse.com/words",
        "params": {
            "type": "object",
            "properties": {
                "ml": {"type": "string", "description": "Means-like: find words with similar meaning"},
                "rel_trg": {"type": "string", "description": "Triggered-by: words associated with this term"},
                "rel_syn": {"type": "string", "description": "Synonyms of this word"},
                "max": {"type": "number", "description": "Max results (default 10, max 1000)"}
            },
            "required": []
        }
    },
    {
        "name": "get_reddit_posts",
        "description": "Get top or hot posts from any subreddit. Used for sentiment analysis, trending topics, and crypto community pulse.",
        "url": "https://www.reddit.com/r/{{subreddit}}/{{sort}}.json",
        "params": {
            "type": "object",
            "properties": {
                "subreddit": {"type": "string", "description": "Subreddit name (e.g. CryptoCurrency, ethereum, defi)"},
                "sort": {"type": "string", "description": "Sort order: hot, new, top, rising"},
                "limit": {"type": "number", "description": "Number of posts (max 100)"},
                "t": {"type": "string", "description": "Time filter for top: hour, day, week, month, year, all"}
            },
            "required": ["subreddit", "sort"]
        }
    },
    {
        "name": "get_fear_greed_index",
        "description": "Get the current Crypto Fear & Greed Index with historical values. Used for sentiment analysis in crypto research and thread jobs.",
        "url": "https://api.alternative.me/fng/",
        "params": {
            "type": "object",
            "properties": {
                "limit": {"type": "number", "description": "Number of historical data points (1 = current only)"},
                "format": {"type": "string", "description": "Response format: json, csv"}
            },
            "required": []
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 8. ACP / VIRTUALS PROTOCOL ECOSYSTEM
    # Jobs: multiAgentCoordination, clonePlatformOnboarding,
    #       agentTrainingModule, fullAgentTrainingSuite
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "get_acp_agents",
        "description": "Browse and search all agents on the Virtuals ACP marketplace. Filter by keyword, cluster, chain. Used for multiAgentCoordination and onboarding jobs.",
        "url": "https://api.virtuals.io/api/agents",
        "params": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword for agent name or capability"},
                "cluster": {"type": "string", "description": "Agent cluster filter"},
                "limit": {"type": "number", "description": "Max results to return"},
                "chainId": {"type": "number", "description": "Blockchain chain ID filter"}
            },
            "required": []
        }
    },
    {
        "name": "get_agent_profile",
        "description": "Get full profile of any ACP agent by wallet address: offerings, resources, reputation score, active jobs, chains supported.",
        "url": "https://api.virtuals.io/api/agents/{{walletAddress}}",
        "params": {
            "type": "object",
            "properties": {
                "walletAddress": {"type": "string", "description": "Agent wallet address (0x...)"}
            },
            "required": ["walletAddress"]
        }
    },
    {
        "name": "get_agent_offerings",
        "description": "Get all job offerings published by a specific ACP agent. Used to understand capabilities before coordination.",
        "url": "https://api.virtuals.io/api/agents/{{walletAddress}}/offerings",
        "params": {
            "type": "object",
            "properties": {
                "walletAddress": {"type": "string", "description": "Agent wallet address"}
            },
            "required": ["walletAddress"]
        }
    },
    {
        "name": "get_iclone_status",
        "description": "Get iCLONE's own current status on ACP: active jobs, reputation score, wallet balance, completed job count.",
        "url": "https://api.virtuals.io/api/agents/{{clientAddress}}",
        "params": {
            "type": "object",
            "properties": {
                "clientAddress": {"type": "string", "description": "iCLONE agent wallet address"}
            },
            "required": ["clientAddress"]
        }
    },
    {
        "name": "get_virtual_token_data",
        "description": "Get current $VIRTUAL token price, market cap, and 24h volume. Used for platform context and tokenomics reporting.",
        "url": "https://api.coingecko.com/api/v3/simple/price",
        "params": {
            "type": "object",
            "properties": {
                "ids": {"type": "string", "description": "virtual-protocol"},
                "vs_currencies": {"type": "string", "description": "usd"},
                "include_market_cap": {"type": "boolean"},
                "include_24hr_change": {"type": "boolean"}
            },
            "required": ["ids", "vs_currencies"]
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 9. PRICE MONITORING & AUTOMATION
    # Jobs: priceMonitor, projectScaffoldGenerator
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "monitor_webpage_element",
        "description": "Fetch any webpage and extract specific content for price or availability monitoring. Used by priceMonitor job to track product prices on any site.",
        "url": "https://r.jina.ai/{{target_url}}",
        "params": {
            "type": "object",
            "properties": {
                "target_url": {"type": "string", "description": "URL of the page to monitor"}
            },
            "required": ["target_url"]
        }
    },
    {
        "name": "get_exchange_rates",
        "description": "Get current exchange rates for any currency pair. Used for price normalisation and multi-currency reporting.",
        "url": "https://api.frankfurter.app/latest",
        "params": {
            "type": "object",
            "properties": {
                "base": {"type": "string", "description": "Base currency (USD, EUR, GBP)"},
                "symbols": {"type": "string", "description": "Target currencies comma-separated"}
            },
            "required": ["base"]
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 10. TRADING & MARKET INTELLIGENCE (Druckenmiller/Seykota layer)
    # Support for iCLONE's trading soul
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "get_hyperliquid_positions",
        "description": "Get open perpetual futures positions for any wallet on Hyperliquid. Used by iCLONE trading soul to monitor active positions.",
        "url": "https://api.hyperliquid.xyz/info",
        "params": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "description": "Request type: clearinghouseState, openOrders, userFills"},
                "user": {"type": "string", "description": "Wallet address"}
            },
            "required": ["type", "user"]
        }
    },
    {
        "name": "get_hyperliquid_market_data",
        "description": "Get all perpetual futures market data from Hyperliquid: funding rates, open interest, 24h volume, mark price for all 98 assets.",
        "url": "https://api.hyperliquid.xyz/info",
        "params": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "description": "metaAndAssetCtxs for full market data"}
            },
            "required": ["type"]
        }
    },
    {
        "name": "get_macro_economic_data",
        "description": "Get macroeconomic indicators: Fed funds rate, CPI, GDP, M2 money supply, unemployment. Used for Druckenmiller macro analysis layer.",
        "url": "https://api.stlouisfed.org/fred/series/observations",
        "params": {
            "type": "object",
            "properties": {
                "series_id": {"type": "string", "description": "FRED series ID: FEDFUNDS, CPIAUCSL, M2SL, GDP, UNRATE, DXY"},
                "limit": {"type": "number", "description": "Number of observations"},
                "sort_order": {"type": "string", "description": "asc or desc"},
                "api_key": {"type": "string", "description": "FRED API key"}
            },
            "required": ["series_id"]
        }
    },
    {
        "name": "get_dxy_data",
        "description": "Get US Dollar Index (DXY) current value and trend. Critical for Druckenmiller macro regime classification (risk-on vs risk-off).",
        "url": "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB",
        "params": {
            "type": "object",
            "properties": {
                "interval": {"type": "string", "description": "Data interval: 1d, 1wk, 1mo"},
                "range": {"type": "string", "description": "Date range: 1d, 5d, 1mo, 3mo, 1y"}
            },
            "required": []
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # 11. IDENTITY & UTILITY
    # Support for all jobs requiring identity verification or utility ops
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "get_ip_geolocation",
        "description": "Get geolocation data for any IP address: country, city, timezone, ISP. Used for fraud detection and data enrichment in analytics jobs.",
        "url": "https://ipapi.co/{{ip}}/json/",
        "params": {
            "type": "object",
            "properties": {
                "ip": {"type": "string", "description": "IP address to geolocate"}
            },
            "required": ["ip"]
        }
    },
    {
        "name": "get_domain_info",
        "description": "Get WHOIS and DNS information for any domain. Used for company research, competitor analysis, and security scanning jobs.",
        "url": "https://api.domainsdb.info/v1/domains/search",
        "params": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Domain name to look up"},
                "zone": {"type": "string", "description": "TLD zone (com, io, ai, etc.)"}
            },
            "required": ["domain"]
        }
    },
    {
        "name": "generate_uuid",
        "description": "Generate unique UUIDs for use in structured data, job IDs, and database records.",
        "url": "https://www.uuidtools.com/api/generate/v4",
        "params": {
            "type": "object",
            "properties": {
                "count": {"type": "number", "description": "Number of UUIDs to generate (max 100)"}
            },
            "required": []
        }
    },
    {
        "name": "get_timezone_info",
        "description": "Get current time and timezone data for any location or timezone code. Used for scheduling, SLA calculation, and global operations.",
        "url": "https://worldtimeapi.org/api/timezone/{{timezone}}",
        "params": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "Timezone code (e.g. Europe/Lisbon, America/New_York, UTC)"}
            },
            "required": ["timezone"]
        }
    }
]
