"""
CLONE — iCLONE Hermes Command Training Module
Full command reference for the Hermes runtime + Virtuals ACP CLI.

Sources:
- Hermes Agent CLI (Nous Research): hermes-agent.nousresearch.com/docs
- ACP CLI: github.com/Virtual-Protocol/acp-cli
- DegenClaw: github.com/Virtual-Protocol/dgclaw-skill
- Virtuals Whitepaper: whitepaper.virtuals.io/llms-full.txt
- ACP Node SDK: github.com/Virtual-Protocol/acp-node
- x402 Server: github.com/Virtual-Protocol/acp-x402-server

iCLONE uses this knowledge to:
- Execute ACP jobs end-to-end via CLI
- Manage wallet, email, virtual cards via EconomyOS
- Trade on Hyperliquid via DegenClaw
- Orchestrate sessions, memory, and scheduling via Hermes
- Serve skills as payment-gated endpoints via acp serve + x402
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("iclone.training.hermes")


class HermesTraining:
    """
    Full Hermes runtime + Virtuals ACP CLI command knowledge for iCLONE.
    """

    MODULE_ID = "hermes_training_v1"
    SCHEDULE = "2x daily — 07:00 UTC + 19:00 UTC"

    # -------------------------------------------------------------------------
    # BUTLER COMMANDS (app.virtuals.io chat interface)
    # -------------------------------------------------------------------------
    BUTLER_COMMANDS = {
        "/reset": "Clear conversation and working memory. Long-term context preserved.",
        "/topup <amount>": "Fund Butler wallet from connected Base wallet. Example: /topup 100 (USDC)",
    }

    # -------------------------------------------------------------------------
    # ACP CLI — FULL COMMAND REFERENCE
    # -------------------------------------------------------------------------
    ACP_CLI = {
        "binary": "acp",
        "global_flags": {
            "--json": "Machine-readable NDJSON output for all commands",
        },

        "auth": {
            "acp configure": "Interactive auth setup",
            "acp configure start [--json]": "Start auth flow",
            "acp configure complete --request-id ID [--json] [--wait] [--timeout SECS]": "Complete auth",
            "note": "Auth tokens stored in OS keychain (macOS Keychain / Linux Secret Service / Windows Credential Manager)",
        },

        "agent_management": {
            "acp agent create": "Create new agent [--name] [--description] [--image URL] [--signer] [--policy]",
            "acp agent list": "List agents [--page N] [--page-size N]",
            "acp agent use": "Set active agent [--agent-id ID]",
            "acp agent whoami": "Show current agent identity",
            "acp agent update": "Update agent metadata [--name] [--description] [--image]",
            "acp agent add-signer": "Add signing key [--agent-id] [--policy] [--no-wait]",
            "acp agent signer-status": "Check signer status --agent-id --request-id --public-key",
            "acp agent migrate": "Migrate agent [--agent-id] [--complete]",
            "acp agent register-erc8004": "Register on-chain reputation [--agent-id] [--chain-id]",
        },

        "tokenization": {
            "acp agent tokenize": (
                "Launch token [--chain-id] [--symbol] [--anti-sniper SECS] "
                "[--prebuy AMT] [--acf] [--60-days] [--airdrop-percent PCT] "
                "[--robotics] [--configure]"
            ),
        },

        "wallet": {
            "acp wallet address": "Show agent wallet address",
            "acp wallet balance --chain-id ID": "Show balance on chain",
            "acp wallet sign-message --message TEXT --chain-id ID": "Sign arbitrary message",
            "acp wallet sign-typed-data --data JSON --chain-id ID": "Sign EIP-712 typed data",
            "acp wallet send-transaction": "Send tx --chain-id --to [--value WEI] [--data HEX]",
            "acp wallet topup": "Fund wallet --chain-id [--method coinbase_pay|crossmint] [--amount] [--email] [--us]",
            "acp chain list": "List supported chains",
        },

        "email": {
            "description": "Agent email identity at os.virtuals.io — e.g. iclone@agents.world",
            "acp email whoami": "Show agent email address",
            "acp email provision": "Provision email inbox",
            "acp email inbox": "List emails [--folder] [--limit N] [--cursor]",
            "acp email compose": "Send email --to --subject --body",
            "acp email search --query TEXT": "Search inbox",
            "acp email thread --thread-id ID": "View email thread",
            "acp email reply --thread-id ID --body TEXT": "Reply to thread",
            "acp email extract-otp --message-id ID": "Extract OTP from email",
            "acp email extract-links --message-id ID": "Extract links from email",
            "acp email attachment --attachment-id ID --output PATH": "Download attachment",
        },

        "virtual_cards": {
            "description": "Powered by Crossmint — single-use or limited-spend virtual Visa/Mastercard",
            "acp card signup --email ADDR": "Register for virtual cards",
            "acp card signup-poll --state STATE": "Poll signup status",
            "acp card whoami": "Show card account identity",
            "acp card profile": "Set profile [--first-name] [--last-name] [--phone-number]",
            "acp card payment-method": "View payment method",
            "acp card limit set --amount CENTS": "Set spend limit",
            "acp card issue --amount CENTS": "Issue new virtual card",
            "acp card list": "List all virtual cards",
            "acp card get --request-id ID": "Get card details",
            "acp card 3ds": "Handle 3DS authentication",
        },

        "compute": {
            "acp compute status": "View compute credits balance",
            "acp compute top-up --amount AMT": "Add compute credits",
        },

        "marketplace": {
            "acp browse QUERY": (
                "Search ACP marketplace [--chain-ids] [--top-k N] [--online] "
                "[--sort-by SUCCESSFUL_JOB_COUNT|SUCCESS_RATE|UNIQUE_BUYER_COUNT|"
                "MINS_FROM_LAST_ONLINE|GRADUATION_STATUS|ONLINE_STATUS]"
            ),
        },

        "offerings": {
            "acp offering list": "List own offerings",
            "acp offering create": (
                "Create offering [--name] [--description] [--price-type] [--price-value] "
                "[--sla-minutes N] [--requirements] [--deliverable] "
                "[--no-required-funds] [--no-hidden] [--subscription-ids]"
            ),
            "acp offering update": "Update offering [--offering-id] [--price-value] [--hidden] [--subscription-ids]",
            "acp offering delete": "Delete offering [--offering-id] [--force]",
        },

        "subscriptions": {
            "acp subscription list": "List subscriptions",
            "acp subscription create": "Create subscription [--name] [--price AMT] [--duration-days DAYS]",
            "acp subscription update": "Update subscription [--id] [--price] [--duration-days]",
            "acp subscription delete": "Delete subscription [--id] [--force]",
        },

        "resources": {
            "description": "Live context attached to offerings — real-time available state",
            "acp resource list": "List resources",
            "acp resource create": "Create resource",
            "acp resource update": "Update resource",
            "acp resource delete": "Delete resource",
        },

        "client_jobs": {
            "description": "BUYER side — initiating jobs",
            "acp client create-job": (
                "Create job --provider ADDR --offering-name NAME "
                "--requirements JSON --chain-id ID [--package-id N]"
            ),
            "acp client create-custom-job": "Custom job --provider ADDR --description DESC --expired-in SECS",
            "acp client fund": "Fund job --job-id N --amount AMT --chain-id ID",
            "acp client complete": "Mark complete --job-id N --chain-id ID [--reason TEXT]",
            "acp client reject": "Reject job --job-id N --chain-id ID [--reason TEXT]",
            "acp client review": "Rate job --job-id N --chain-id ID --rating N [--review TEXT]",
        },

        "provider_jobs": {
            "description": "SELLER side — delivering jobs",
            "acp provider set-budget": "Set budget --job-id N --amount AMT --chain-id ID",
            "acp provider set-budget-with-fund-request": (
                "Set budget + request funds --job-id N --amount AMT "
                "[--transfer-amount AMT] [--destination ADDR]"
            ),
            "acp provider submit": "Submit deliverable --job-id N --deliverable CONTENT --chain-id ID",
        },

        "job_queries": {
            "acp job list": "List jobs [--legacy|--all]",
            "acp job history --job-id N --chain-id ID": "Full job history",
            "acp job watch --job-id N [--timeout SECS]": "Watch job until completion",
            "acp message send": "In-job message --job-id N --chain-id ID --content TEXT [--content-type TYPE]",
        },

        "events": {
            "description": "For agent loops — stream and drain marketplace events",
            "acp events listen": "Stream events as NDJSON [--legacy|--all] [--job-id N] [--output FILE]",
            "acp events drain --file FILE": "Atomically drain event file [--limit N]",
            "note": "events listen runs in server mode; events drain is for agent polling loops",
        },

        "trading": {
            "description": "Hyperliquid integration via ACP",
            "acp trade --side long|short --token TOKEN --size SIZE": "Open perp position [--leverage] [--price] [--post-only] [--reduce-only]",
            "acp trade hl-status": "Hyperliquid account status",
            "acp trade withdraw-from-hl": "Withdraw from HL --amount AMT [--destination ADDR] [--to-chain ID]",
        },

        "skill_deployment": {
            "acp serve": "Deploy skill as x402 + MPP + ACP native endpoints simultaneously",
            "acp skill print": "Print skill handler definitions",
            "note": "acp serve exposes 3 endpoint types: x402 (HTTP 402 payment-gated), MPP (Stripe-style), ACP native (on-chain)",
        },
    }

    # -------------------------------------------------------------------------
    # DEGENCLAW COMMANDS (Hyperliquid trading + degen.virtuals.io forum)
    # -------------------------------------------------------------------------
    DEGENCLAW = {
        "description": "Hyperliquid perp trading + degen.virtuals.io forum for AI agents",
        "competition": "AI agents trade real USDC on Hyperliquid perpetuals",
        "schedule": "12-hour cycle — 00:00 & 12:00 UTC (automatic, no manual trigger needed)",

        "setup": {
            "acp configure": "Authenticate ACP first",
            "acp agent create / acp agent use": "Set active agent",
            "acp agent add-signer": "Add signing key",
            "npx tsx scripts/activate-unified.ts": "Combine spot + perp into unified HL account",
            "dgclaw.sh join": "Register agent, auto-detect env, save API key",
            "dgclaw.sh --env ./agent.env join": "Join with custom env file",
        },

        "trading": {
            "open_position": (
                "npx tsx scripts/trade.ts open --pair ETH --side long --size 500 --leverage 5 "
                "[--type market|limit] [--limit-price PRICE] [--sl STOP] [--tp TARGET]"
            ),
            "close_position": "npx tsx scripts/trade.ts close --pair ETH",
            "modify_position": "npx tsx scripts/trade.ts modify --pair ETH --leverage 10 --sl 3200 --tp 4000",
            "balance": "npx tsx scripts/trade.ts balance",
            "positions": "npx tsx scripts/trade.ts positions",
            "tickers": "npx tsx scripts/trade.ts tickers",
        },

        "deposits_withdrawals": {
            "deposit": (
                "acp client create-job --provider 0xd478a8B40372db16cA8045F28C6FE07228F3781A "
                "--offering-name perp_deposit --requirements '{\"amount\":\"100\"}' --legacy --json "
                "→ then: acp client fund --job-id <jobId> --json"
            ),
            "withdraw": "npx tsx scripts/withdraw.ts --amount 50 [--destination 0x...]",
        },

        "forum": {
            "description": "degen.virtuals.io — post trade rationale after every trade (IMMUTABLE RULE #10)",
            "dgclaw.sh forum <agentId>": "View agent forum",
            "dgclaw.sh forums": "List all agent forums",
            "dgclaw.sh create-post <agentId> <threadId> '<title>' '<content>'": "Post trade rationale",
            "dgclaw.sh posts": "List posts",
        },

        "leaderboard": {
            "dgclaw.sh leaderboard": "Top 25 agents",
            "dgclaw.sh leaderboard 50": "Top 50",
            "dgclaw.sh leaderboard 20 20": "Page 2, 20 per page",
            "dgclaw.sh leaderboard-agent <name>": "Single agent rank",
        },
    }

    # -------------------------------------------------------------------------
    # HERMES CLI COMMANDS (Nous Research runtime)
    # -------------------------------------------------------------------------
    HERMES_CLI = {
        "binary": "hermes",

        "global_options": {
            "--version, -V": "Show version",
            "--profile, -p <name>": "Select profile",
            "--resume, -r <session>": "Resume session",
            "--continue, -c [name]": "Resume most recent session",
            "--worktree, -w": "Isolated git worktree",
            "--yolo": "Skip approval prompts",
            "--tui": "Launch TUI interface",
            "--cli": "Force classic CLI",
        },

        "chat": {
            "hermes chat": "Interactive chat",
            "hermes chat -q '<prompt>'": "Non-interactive single-shot",
            "hermes -z '<prompt>'": "Pure one-shot minimal output",
            "options": "-m model | -t toolsets | --provider | -s skills | --image | --checkpoints | --max-turns N",
        },

        "config": {
            "hermes model": "Interactive model/provider selector",
            "hermes setup [section]": "Config wizard — sections: model, tts, terminal, gateway, tools, agent",
            "hermes config show|edit|set|path|env-path|check|migrate": "Configuration management",
        },

        "gateway": {
            "hermes gateway run|start|stop|restart|status|list|install|uninstall|setup": "Messaging platform gateway",
            "hermes send --to <target> 'message'": "Send message to platform",
            "hermes whatsapp": "WhatsApp pairing flow",
            "hermes slack manifest": "Generate Slack app manifest",
        },

        "skills_tools": {
            "hermes skills browse|search|install|inspect|list|update|audit|uninstall|publish": "Skill management",
            "hermes bundles list|show|create|delete": "Skill bundle management",
            "hermes tools [--summary]": "Per-platform tool config",
            "hermes mcp catalog|install|serve|add|remove|list|test|configure|login": "MCP server management",
        },

        "sessions_memory": {
            "hermes sessions list|browse|export|delete|prune|stats|rename": "Session management",
            "hermes memory setup|status|off": "Memory configuration",
            "hermes checkpoints status|list|prune|clear": "Filesystem checkpoints",
        },

        "automation": {
            "hermes cron list|create|edit|pause|resume|run|remove|status|tick": "Scheduled tasks",
            "hermes kanban init|create|list|show|assign|complete|schedule|dispatch": "Collaboration board",
            "hermes webhook subscribe|list|remove|test": "Webhook management",
        },

        "system": {
            "hermes update [--check]": "Update Hermes",
            "hermes doctor [--fix]": "Diagnose and fix issues",
            "hermes logs [name] [--follow] [--level]": "View logs",
            "hermes status [--all] [--deep]": "System status",
            "hermes security audit [--json] [--fail-on level]": "Security audit",
            "hermes dashboard [--port N]": "Web dashboard",
        },

        "acp_integration": {
            "hermes acp": "Start ACP server endpoint from within Hermes",
        },
    }

    # -------------------------------------------------------------------------
    # HERMES SLASH COMMANDS — SOURCE: mintlify.wiki/NousResearch/hermes-agent
    # Verified against official documentation 2026-06-09
    # -------------------------------------------------------------------------
    HERMES_SLASH = {
        "session_management": {
            "/new": "Start a fresh session (alias: /reset) — CLI + Gateway",
            "/clear": "Clear the screen and start a new session — CLI only",
            "/history": "Show the full conversation history — CLI only",
            "/save": "Save the current conversation to disk — CLI only",
            "/retry": "Resend the last user message to the agent — CLI + Gateway",
            "/undo": "Remove the last user/assistant exchange from history — CLI + Gateway",
            "/title [name]": "Set a title for the current session — CLI + Gateway",
            "/compress": "Manually trigger context compression — CLI + Gateway",
            "/rollback [number]": "List filesystem checkpoints or restore a previous snapshot — CLI + Gateway",
            "/stop": "Kill all running background processes — CLI + Gateway",
            "/background <prompt>": "Run a prompt as a background task (alias: /bg) — CLI + Gateway",
            "/resume [name]": "Resume a previously named session — CLI + Gateway",
            "/status": "Show current session info — Gateway only",
            "/sethome": "Set this chat as the home channel (alias: /set-home) — Gateway only",
        },

        "configuration": {
            "/config": "Show the current configuration — CLI only",
            "/model [name]": "Show current model or switch to a different one — CLI + Gateway",
            "/provider": "Show available providers and the currently active provider — CLI + Gateway",
            "/prompt [text]": "View or set a custom system prompt — CLI only",
            "/personality [name]": "Switch to a predefined personality — CLI + Gateway",
            "/statusbar": "Toggle the context/model status bar (alias: /sb) — CLI only",
            "/verbose": "Cycle tool progress display: off → new → all → verbose — CLI only",
            "/reasoning [level|show|hide]": "Manage reasoning effort and display — CLI + Gateway",
            "/skin [name]": "Show or change the display skin/theme — CLI only",
            "/voice [on|off|tts|status]": "Toggle voice mode or control TTS — CLI + Gateway",
        },

        "tools_skills": {
            "/tools [list|disable|enable] [name...]": "Manage enabled tools for the current session — CLI only",
            "/toolsets": "List available toolsets and their tools — CLI only",
            "/skills [search|browse|inspect|install]": "Search, browse, install, and manage skill documents — CLI only",
            "/cron [subcommand]": "Manage scheduled tasks: list, add, edit, pause, resume, run, remove — CLI only",
            "/reload-mcp": "Reload MCP server connections from config (alias: /reload_mcp) — CLI + Gateway",
            "/browser [connect|disconnect|status]": "Connect browser tools to live Chrome via CDP — CLI only",
            "/plugins": "List installed plugins and their status — CLI only",
        },

        "info": {
            "/help": "Show all available commands — CLI + Gateway",
            "/usage": "Show token usage stats for the current session — CLI + Gateway",
            "/insights [days]": "Show usage insights and analytics — CLI + Gateway",
            "/platforms": "Show gateway and messaging platform status (alias: /gateway) — CLI only",
            "/paste": "Check clipboard for an image and attach it to next message — CLI only",
            "/update": "Update Hermes Agent to the latest version — Gateway only",
            "/quit": "Exit the CLI (aliases: /exit, /q) — CLI only",
        },
    }

    # -------------------------------------------------------------------------
    # ACP v2 — HOOK ARCHITECTURE + EVENT SYSTEM
    # -------------------------------------------------------------------------
    ACP_V2 = {
        "hook_architecture": {
            "description": "Contract-level hooks for extending job lifecycle — replaces Memo system",
            "job_creation": "createJob({ ...params, hookAddress: '0xYourHookContract' })",
            "hook_interface": "beforeAction(jobId, action, params) → (bool proceed, bytes modified) | afterAction(jobId, action, result)",
        },

        "events": {
            "description": "Single entry handler replaces onNewTask + onEvaluate dual callbacks",
            "transport_default": "SSE (Server-Sent Events)",
            "transport_alternative": "SocketTransport (WebSocket)",
            "event_names": [
                "job.created",
                "budget.set",
                "job.funded",
                "job.submitted",
                "job.completed",
                "job.rejected",
                "job.expired",
            ],
        },

        "python_sdk": {
            "client": "VirtualsACP(acp_contract_clients=ACPContractClientV2(...), on_new_task=handler)",
            "browse": "acp_client.browse_agents(keyword, sort_by, top_k, graduation_status, online_status)",
            "initiate_job": "acp.initiate_job(provider_address, service_requirement, expired_at, evaluator_address)",
            "respond_job": "acp.respond_job(job_id, memo_id, accept, reason)",
            "pay_job": "acp.pay_job(job_id, amount, memo_id, reason)",
            "deliver_job": "acp.deliver_job(job_id, deliverable)",
            "queries": "get_active_jobs() | get_completed_jobs() | get_cancelled_jobs() | get_job_by_onchain_id() | get_memo_by_id()",
        },
    }

    # -------------------------------------------------------------------------
    # x402 PAYMENT SERVER
    # -------------------------------------------------------------------------
    X402 = {
        "description": "Virtuals payment facilitator — deployed at acp-x402.virtuals.io",
        "endpoints": {
            "POST /verify": "Verify payment — { x402Version, paymentHeader, paymentRequirements }",
            "POST /settle": "Settle payment — returns { success, txHash, networkId }",
            "GET /supported": "List supported schemes and networks",
        },
        "headers": {
            "X-PAYMENT": "Client sends base64-encoded Payment Payload",
            "X-PAYMENT-RESPONSE": "Server returns blockchain transaction details",
            "HTTP 402": "Signals payment required",
        },
        "middleware": "paymentMiddleware('0xYourAddress', { '/your-endpoint': '$0.01' })",
    }

    # -------------------------------------------------------------------------
    # DEPRECATED COMMANDS (know these to avoid using them)
    # -------------------------------------------------------------------------
    DEPRECATED = {
        "acp buyer *": "→ acp client *",
        "acp seller *": "→ acp provider *",
        "acp sell *": "→ acp offering *",
        "acp sell resource *": "→ acp resource *",
        "acp setup / acp login": "→ acp configure",
        "openclaw binary": "→ acp binary",
        "serve start/stop/status/logs": "→ acp serve",
        "GAME_API_KEY": "→ VIRTUALS_API_KEY",
        "game-sdk": "→ virtuals-acp",
    }

    # -------------------------------------------------------------------------
    # iCLONE CRITICAL COMMANDS (most used in daily operation)
    # -------------------------------------------------------------------------
    ICLONE_CRITICAL = {
        "daily_trading_cycle": [
            "acp trade hl-status  # check account state",
            "npx tsx scripts/trade.ts positions  # current positions",
            "npx tsx scripts/trade.ts tickers  # market prices",
            "npx tsx scripts/trade.ts open --pair BTC --side long --size 500 --leverage 3",
            "npx tsx scripts/trade.ts close --pair ETH",
            "dgclaw.sh create-post <agentId> <threadId> '<title>' '<rationale>'  # MANDATORY after every trade",
        ],
        "acp_job_lifecycle": [
            "acp events listen --output events.ndjson  # start event stream",
            "acp events drain --file events.ndjson  # poll for new jobs",
            "acp provider set-budget --job-id N --amount AMT --chain-id ID",
            "acp provider submit --job-id N --deliverable '<result>' --chain-id ID",
        ],
        "identity_check": [
            "acp agent whoami",
            "acp wallet address",
            "acp email whoami",
        ],
        "offering_management": [
            "acp offering list",
            "acp offering create --name iclone-crypto-research-v1 --price-value 5 --sla-minutes 120",
        ],
    }

    def __init__(self):
        self._sessions: list[dict] = []

    def run_session(self, session_id: str | None = None) -> dict:
        """Execute a Hermes command training session."""
        _id = session_id or f"hermes_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        logger.info("Starting Hermes training session: %s", _id)

        insights = []

        # ACP CLI
        insights.append(f"ACP CLI: binary='acp' — {len(self.ACP_CLI)} command groups — --json flag on all")
        insights.append(f"Auth: acp configure → tokens in OS keychain")
        insights.append(f"Wallet: acp wallet address|balance|sign-message|send-transaction|topup")
        insights.append(f"Email: {len(self.ACP_CLI['email'])-1} commands — iclone@agents.world identity")
        insights.append(f"Virtual cards: {len(self.ACP_CLI['virtual_cards'])-1} commands — Crossmint-powered Visa/Mastercard")
        insights.append(f"Marketplace: acp browse QUERY — sort by SUCCESSFUL_JOB_COUNT|SUCCESS_RATE|...")
        insights.append(f"Offerings: create|list|update|delete — acp serve deploys x402+MPP+ACP native simultaneously")
        insights.append(f"Client jobs: create-job|fund|complete|reject|review")
        insights.append(f"Provider jobs: set-budget|set-budget-with-fund-request|submit")
        insights.append(f"Events: acp events listen → stream | acp events drain → agent polling loop")

        # DegenClaw
        insights.append(f"DegenClaw: dgclaw.sh join → register — trade.ts open/close/modify/balance/positions/tickers")
        insights.append(f"Forum: dgclaw.sh create-post — MANDATORY after every trade (IMMUTABLE RULE #10)")
        insights.append(f"Deposit: acp client create-job --provider 0xd478a... --offering-name perp_deposit")

        # Hermes CLI
        insights.append(f"Hermes CLI: {len(self.HERMES_CLI)} command groups — chat|config|gateway|skills|sessions|cron|system")
        insights.append(f"Hermes ACP: hermes acp — starts ACP server endpoint from within Hermes runtime")

        # Slash commands
        slash_total = sum(len(v) for v in self.HERMES_SLASH.values())
        insights.append(f"Hermes slash commands: {slash_total} total — /goal|/plan|/cron|/skills|/background|/steer|/queue")

        # ACP v2
        insights.append(f"ACP v2 events: {len(self.ACP_V2['events']['event_names'])} event types — single entry handler")
        insights.append(f"x402: POST /verify|/settle|/supported — HTTP 402 payment-gated endpoints")

        # Deprecated
        insights.append(f"Deprecated: {len(self.DEPRECATED)} old commands — never use game-sdk, GAME_API_KEY, acp buyer/seller/sell")

        # Critical commands
        insights.append(f"Critical daily: {len(self.ICLONE_CRITICAL['daily_trading_cycle'])} trading commands + {len(self.ICLONE_CRITICAL['acp_job_lifecycle'])} ACP job commands")

        session = {
            "session_id": _id,
            "module": self.MODULE_ID,
            "completed": True,
            "insights_count": len(insights),
            "insights": insights,
            "command_groups": len(self.ACP_CLI),
            "slash_commands": sum(len(v) for v in self.HERMES_SLASH.values()),
            "deprecated_known": len(self.DEPRECATED),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._sessions.append(session)
        logger.info(
            "Hermes session %s — %d insights — %d CLI groups — %d slash commands",
            _id, len(insights), session["command_groups"], session["slash_commands"],
        )
        return session
