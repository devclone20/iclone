"""
iCLONE — ACP Bootstrapper v2

Suporta 3 modos:
  1. --agent supersayatin|doctorwho|matrix  → client dedicado, contrata CLONE
  2. --agent auto                            → comportamento original (browse livre)
  3. --multi                                 → corre os 3 clientes em paralelo (threads)

Cada cliente usa a mesma developer wallet mas um agent_id diferente.
O acp-cli faz switch automático antes de qualquer operação.

Run:
  python3 ops/bootstrapper.py --agent supersayatin
  python3 ops/bootstrapper.py --agent matrix --dry-run
  python3 ops/bootstrapper.py --multi
  python3 ops/bootstrapper.py --agent auto --max-price 0.05
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.home() / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env", override=False)

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))
from iclone import db

_ACP_CANDIDATES = [
    "/opt/homebrew/bin/acp",
    "/usr/local/bin/acp",
    "/usr/bin/acp",
]
ACP_BIN = next((p for p in _ACP_CANDIDATES if Path(p).exists()), "acp")
CHAIN_ID = 8453

# ── Dedicated CLIENT agents ────────────────────────────────────────────────────
CLONE_WALLET  = "0x44cc25d55a4291b92f52062ba023ca1f14206664"
CLONE_AGENT_ID = "019eae06-96cd-77d0-8f8b-a6abb71f0cd7"

DEDICATED_CLIENTS = {
    "supersayatin": {
        "agent_id":   "019ebb92-7415-7baa-93e9-ee19a7742877",
        "wallet":     "0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3",
        "name":       "SuperSayatin",
        # Matches offering_ids: research, crypto, wallet, price-monitor, pdf
        "categories": ["research", "crypto", "wallet", "price", "pdf"],
        "target":     CLONE_WALLET,
    },
    "doctorwho": {
        "agent_id":   "019ebb92-93e8-7b4e-b2e8-39c3419843c9",
        "wallet":     "0x875242eb5c91270ca80ed7753a87d6e22e4f5acf",
        "name":       "DoctorWHO",
        # Matches offering_ids: thread, blog, newsletter, docs, csv, onboarding
        "categories": ["thread", "blog", "newsletter", "docs", "csv", "onboarding"],
        "target":     CLONE_WALLET,
    },
    "matrix": {
        "agent_id":   "019ebb92-b4be-7660-82d3-4b1647843e6a",
        "wallet":     "0x07924dea2c8212969d5dc5655785aa5063adb2bc",
        "name":       "MATRIX",
        # Matches offering_ids: code, bug, sql, regex, test, scaffold, defi, build-skill
        "categories": ["code", "bug", "sql", "regex", "test", "scaffold", "defi", "build"],
        "target":     CLONE_WALLET,
    },
}

# ── Config defaults ────────────────────────────────────────────────────────────
DEFAULT_DAILY_BUDGET   = 10.0
DEFAULT_MAX_JOB_PRICE  = 0.10
DEFAULT_JOBS_PER_HOUR  = 10
DEFAULT_MAX_CONCURRENT = 20
POLL_INTERVAL = 8


def _make_logger(name: str) -> logging.Logger:
    log_dir = Path.home() / "Library" / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"iclone-{name.lower()}.log"
    logger = logging.getLogger(name)
    if not logger.handlers:
        fmt = logging.Formatter(f"%(asctime)s [{name.upper()}] %(message)s")
        fh = logging.FileHandler(log_file)
        fh.setFormatter(fmt)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        logger.addHandler(fh)
        logger.addHandler(sh)
        logger.setLevel(logging.INFO)
    return logger


def acp(*args: str, check: bool = True) -> dict:
    cmd = [ACP_BIN, *args, "--json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        combined = (r.stdout + "\n" + r.stderr).strip()
        for line in reversed(combined.splitlines()):
            line = line.strip()
            if line.startswith("{") or line.startswith("["):
                try:
                    parsed = json.loads(line)
                    if check and r.returncode != 0 and "error" in parsed:
                        raise RuntimeError(f"acp {' '.join(args)}: {parsed['error']}")
                    return parsed
                except json.JSONDecodeError:
                    continue
        return {}
    except subprocess.TimeoutExpired:
        return {}


def switch_agent(agent_id: str, logger: logging.Logger) -> bool:
    """Switch the active acp-cli agent by ID."""
    resp = acp("agent", "use", "--agent-id", agent_id, check=False)
    ok = resp.get("success", False) or resp.get("activeAgent")
    if ok:
        logger.info("Switched to agent: %s", resp.get("activeAgent", agent_id[:8]))
    else:
        logger.error("Failed to switch agent: %s", resp)
    return bool(ok)


def restore_clone(logger: logging.Logger):
    """Always restore CLONE as the active agent when done."""
    acp("agent", "use", "--agent-id", CLONE_AGENT_ID, check=False)
    logger.info("Restored active agent → CLONE")


def get_clone_offerings(categories: list[str]) -> list[dict]:
    """
    Load CLONE's offerings from local published_offerings.json filtered by category.
    The file is the authoritative source — no API call needed.
    Falls back to acp agent whoami if the file is missing.
    """
    offerings_path = Path(__file__).parent.parent / "published_offerings.json"

    if offerings_path.exists():
        data = json.loads(offerings_path.read_text())
        all_offerings = [
            {
                "name":       o["offering_id"].replace("iclone-", "").replace("-v1", "").replace("-", "_"),
                "priceValue": o["price_usdc"],
                "requirements": json.dumps(o.get("requirements_schema", {})),
                "isHidden":   False,
            }
            for o in data.get("published", [])
        ]
    else:
        # Fallback: ask the CLI (CLONE must be active)
        resp = acp("agent", "whoami", check=False)
        all_offerings = resp.get("offerings", [])

    # Filter by category keywords matching the offering_id fragments
    matched = [
        o for o in all_offerings
        if not o.get("isHidden")
        and any(cat.lower() in o["name"].lower() for cat in categories)
        and float(o.get("priceValue", 999)) <= 1.0   # max $1 per job
    ]

    # Fallback: cheapest 5 if nothing matches
    if not matched:
        matched = sorted(
            [o for o in all_offerings if not o.get("isHidden")],
            key=lambda x: float(x.get("priceValue", 999)),
        )[:5]

    return matched


def browse_cheap_agents(max_price: float, logger: logging.Logger) -> list[dict]:
    """Browse marketplace for cheap agents (auto mode)."""
    logger.info("Browsing agents (max: $%.2f)...", max_price)
    queries = ["web research", "crypto analysis", "data processing",
               "code generation", "content creation", "document"]
    results = []
    seen = set()
    for q in queries:
        resp = acp("browse", q, "--top-k", "30", check=False)
        for agent in resp.get("data", []):
            wallet = agent.get("walletAddress", "")
            if wallet in seen:
                continue
            cheap = [o for o in agent.get("offerings", [])
                     if float(o.get("priceValue", 999)) <= max_price
                     and not o.get("isHidden", False)]
            if cheap:
                seen.add(wallet)
                results.append({"wallet": wallet, "name": agent.get("name", ""), "offerings": cheap})
    logger.info("Found %d agents ≤ $%.2f", len(results), max_price)
    return results


def _build_requirements(offering: dict) -> str:
    req_schema = offering.get("requirements", "")
    try:
        schema = json.loads(req_schema) if isinstance(req_schema, str) else req_schema
        required_fields = schema.get("required", []) if isinstance(schema, dict) else []
        props = schema.get("properties", {}) if isinstance(schema, dict) else {}
    except (json.JSONDecodeError, AttributeError):
        required_fields, props = [], {}

    if not required_fields and isinstance(req_schema, str):
        import re
        required_fields = re.findall(r"'([a-zA-Z_][a-zA-Z0-9_]+)'", req_schema)

    defaults = {
        "query": "artificial intelligence market trends",
        "topic": "artificial intelligence",
        "keyword": "AI agents",
        "token": "VIRTUAL", "token_symbol": "VIRTUAL",
        "symbol": "VIRTUAL", "asset": "VIRTUAL", "coin": "BTC",
        "wallet": CLONE_WALLET, "wallet_address": CLONE_WALLET, "address": CLONE_WALLET,
        "language": "en", "lang": "en",
        "url": "https://virtuals.io",
        "text": "Analyze AI agent marketplaces.",
        "content": "AI agents are transforming commerce.",
        "message": "Hello from iCLONE",
        "description": "AI agent marketplace analysis",
        "prompt": "Summarize key trends in AI agent commerce.",
        "input": "artificial intelligence", "data": "{}",
        "format": "json", "limit": 5, "count": 3, "amount": 1,
        "duration": "1d", "interval": "1h",
        "chain": "base", "chain_id": 8453, "network": "base",
        "category": "technology", "type": "analysis",
        "mode": "standard", "style": "professional", "source": "web",
    }

    payload = {}
    for field in required_fields:
        fl = field.lower()
        if fl in defaults:
            payload[field] = defaults[fl]
            continue
        matched = next((v for k, v in defaults.items() if k in fl or fl in k), None)
        if matched is not None:
            payload[field] = matched
        else:
            prop_type = props.get(field, {}).get("type", "string")
            payload[field] = (1 if prop_type in ("number", "integer")
                              else True if prop_type == "boolean"
                              else [] if prop_type == "array"
                              else f"iclone_bootstrap_{field}")

    return json.dumps(payload) if payload else json.dumps(
        {"query": "artificial intelligence", "topic": "AI agents", "language": "en"}
    )


class Bootstrapper:
    def __init__(
        self,
        agent_key: str = "auto",
        daily_budget: float = DEFAULT_DAILY_BUDGET,
        max_job_price: float = DEFAULT_MAX_JOB_PRICE,
        jobs_per_hour: int = DEFAULT_JOBS_PER_HOUR,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        dry_run: bool = False,
    ):
        self.agent_key    = agent_key
        self.client_cfg   = DEDICATED_CLIENTS.get(agent_key)  # None if auto
        self.daily_budget = daily_budget
        self.max_job_price = max_job_price
        self.jobs_per_hour = jobs_per_hour
        self.max_concurrent = max_concurrent
        self.dry_run      = dry_run

        name = self.client_cfg["name"] if self.client_cfg else "Bootstrap"
        self.log = _make_logger(name)
        self.events_file = Path(f"/tmp/iclone-bootstrap-{agent_key}.jsonl")

        self.spent_today          = 0.0
        self.jobs_created_today   = 0
        self.jobs_completed_today = 0
        self.day_start = datetime.now(timezone.utc).date()
        self.open_jobs: dict[str, dict] = {}

        # Agent pool (auto mode)
        self._agents: list[dict] = []
        self._cursor  = 0
        self._last_job_at = 0.0

        # Dedicated mode: CLONE offerings
        self._clone_offerings: list[dict] = []
        self._offering_cursor = 0

    def _reset_if_new_day(self):
        today = datetime.now(timezone.utc).date()
        if today != self.day_start:
            self.log.info("New day — resetting counters")
            self.spent_today = self.jobs_created_today = self.jobs_completed_today = 0
            self.day_start = today
            self._agents = []
            self._clone_offerings = []

    def _can_create(self) -> bool:
        self._reset_if_new_day()
        if self.spent_today + self.max_job_price > self.daily_budget:
            return False
        if len(self.open_jobs) >= self.max_concurrent:
            return False
        if time.time() - self._last_job_at < 3600 / self.jobs_per_hour:
            return False
        return True

    def _next_target(self) -> tuple[str, dict] | tuple[None, None]:
        """Return (provider_wallet, offering) for the next job."""
        if self.client_cfg:
            # Dedicated mode: always hire CLONE
            if not self._clone_offerings:
                cats = self.client_cfg["categories"]
                self._clone_offerings = get_clone_offerings(cats)
                self._offering_cursor = 0
                if not self._clone_offerings:
                    self.log.warning("No CLONE offerings found for categories: %s", cats)
                    return None, None
                self.log.info("Loaded %d CLONE offerings for %s",
                              len(self._clone_offerings), self.client_cfg["name"])

            offering = self._clone_offerings[self._offering_cursor % len(self._clone_offerings)]
            self._offering_cursor += 1
            return CLONE_WALLET, offering
        else:
            # Auto mode: browse marketplace
            if not self._agents:
                self._agents = browse_cheap_agents(self.max_job_price, self.log)
                self._cursor = 0
            for _ in range(len(self._agents)):
                agent = self._agents[self._cursor % len(self._agents)]
                self._cursor += 1
                if agent["offerings"]:
                    return agent["wallet"], agent["offerings"][0]
            return None, None

    def _switch_to_self(self) -> bool:
        """Switch acp-cli to this client agent (dedicated mode only)."""
        if not self.client_cfg:
            return True  # auto mode: use whatever is active
        return switch_agent(self.client_cfg["agent_id"], self.log)

    def maybe_create_job(self):
        if not self._can_create():
            return

        wallet, offering = self._next_target()
        if not wallet:
            return

        price = float(offering.get("priceValue", 0))
        name  = offering.get("name", "")

        if self.dry_run:
            self.log.info("[DRY-RUN] Would hire %s @ $%.2f from %s",
                          name, price, wallet[:10])
            self._last_job_at = time.time()
            self.jobs_created_today += 1
            return

        # Switch to this client agent before creating job
        if not self._switch_to_self():
            self.log.error("Cannot switch agent — skipping job creation")
            return

        req = _build_requirements(offering)
        resp = acp(
            "client", "create-job",
            "--provider", wallet,
            "--offering-name", name,
            "--requirements", req,
            "--chain-id", str(CHAIN_ID),
            check=False,
        )

        if resp.get("success") or resp.get("jobId"):
            job_id = str(resp.get("jobId", ""))
            self.open_jobs[job_id] = {
                "amount": price, "provider": wallet,
                "offering": name, "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._last_job_at = time.time()
            self.jobs_created_today += 1
            self.log.info("Job %s created: %s @ $%.2f | Open: %d",
                          job_id, name, price, len(self.open_jobs))
        else:
            self.log.warning("Create-job failed: %s", resp.get("error", resp))

    def handle_events(self, events: list[dict]):
        for event in events:
            job_id = str(event.get("jobId", ""))
            status = event.get("status", "")
            roles  = event.get("roles", [])
            tools  = event.get("availableTools", [])

            if "client" not in roles or job_id not in self.open_jobs:
                continue

            job = self.open_jobs[job_id]

            if "fund" in tools and status == "budget_set":
                if self.dry_run:
                    self.log.info("[DRY-RUN] Would fund %s: $%.2f", job_id, job["amount"])
                    continue
                if not self._switch_to_self():
                    continue
                resp = acp("client", "fund",
                           "--job-id", job_id,
                           "--amount", str(job["amount"]),
                           "--chain-id", str(CHAIN_ID), check=False)
                if resp.get("success"):
                    self.spent_today += job["amount"]
                    self.log.info("Funded %s: $%.2f | Spent today: $%.4f",
                                  job_id, job["amount"], self.spent_today)

            elif "complete" in tools and status == "submitted":
                if self.dry_run:
                    self.log.info("[DRY-RUN] Would complete %s", job_id)
                    continue
                if not self._switch_to_self():
                    continue
                resp = acp("client", "complete",
                           "--job-id", job_id,
                           "--chain-id", str(CHAIN_ID),
                           "--reason", "Deliverable received and accepted.",
                           check=False)
                if resp.get("success"):
                    self.jobs_completed_today += 1
                    db.upsert_acp_job(
                        job_id=job_id,
                        offering_id=f"dedicated:{job['offering']}",
                        client_agent_id=job["provider"],
                        status="completed",
                        price_usdc=job["amount"],
                    )
                    del self.open_jobs[job_id]
                    self.log.info("Completed %s | Total today: %d | Spent: $%.4f",
                                  job_id, self.jobs_completed_today, self.spent_today)

            elif status in ("expired", "rejected"):
                self.log.info("Job %s ended: %s", job_id, status)
                del self.open_jobs[job_id]

    def run(self):
        mode = f"DEDICATED → {self.client_cfg['name']}" if self.client_cfg else "AUTO"
        self.log.info("Bootstrapper starting | Mode: %s%s", mode,
                      " [DRY-RUN]" if self.dry_run else "")
        self.log.info("Budget: $%.2f/day | Max price: $%.2f | %d jobs/hr | %d concurrent",
                      self.daily_budget, self.max_job_price,
                      self.jobs_per_hour, self.max_concurrent)

        self.events_file.unlink(missing_ok=True)
        listener = subprocess.Popen(
            [ACP_BIN, "events", "listen", "--output", str(self.events_file), "--json"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.log.info("Event listener PID %d", listener.pid)
        time.sleep(2)

        last_status = time.time()

        try:
            while True:
                if listener.poll() is not None:
                    self.log.warning("Listener died — restarting")
                    self.events_file.unlink(missing_ok=True)
                    listener = subprocess.Popen(
                        [ACP_BIN, "events", "listen", "--output", str(self.events_file), "--json"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    )
                    time.sleep(2)

                if self.events_file.exists():
                    resp = acp("events", "drain",
                               "--file", str(self.events_file),
                               "--limit", "20", check=False)
                    events = resp.get("events", [])
                    if events:
                        self.handle_events(events)

                self.maybe_create_job()

                if time.time() - last_status > 60:
                    self.log.info(
                        "── Status ── Created: %d | Completed: %d | "
                        "Spent: $%.4f/$%.2f | Open: %d",
                        self.jobs_created_today, self.jobs_completed_today,
                        self.spent_today, self.daily_budget, len(self.open_jobs),
                    )
                    last_status = time.time()

                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            self.log.info("Stopped. Created: %d | Completed: %d | Spent: $%.4f",
                          self.jobs_created_today, self.jobs_completed_today, self.spent_today)
            listener.terminate()
        finally:
            if self.client_cfg:
                restore_clone(self.log)


def run_multi(args: argparse.Namespace):
    """Run all 3 dedicated clients in parallel threads."""
    print("Starting all 3 dedicated clients in parallel...")
    threads = []
    for key in DEDICATED_CLIENTS:
        b = Bootstrapper(
            agent_key=key,
            daily_budget=args.daily_budget,
            max_job_price=args.max_price,
            jobs_per_hour=args.jobs_per_hour,
            max_concurrent=args.max_concurrent // 3,  # split concurrent slots
            dry_run=args.dry_run,
        )
        t = threading.Thread(target=b.run, name=key, daemon=True)
        threads.append(t)
        time.sleep(2)  # stagger starts
        t.start()

    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        print("Shutting down all clients...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iCLONE ACP Bootstrapper v2")
    parser.add_argument(
        "--agent",
        choices=["supersayatin", "doctorwho", "matrix", "auto"],
        default="auto",
        help="Which client agent to run as (default: auto)",
    )
    parser.add_argument(
        "--multi", action="store_true",
        help="Run all 3 dedicated clients in parallel",
    )
    parser.add_argument("--daily-budget",  type=float, default=DEFAULT_DAILY_BUDGET)
    parser.add_argument("--max-price",     type=float, default=DEFAULT_MAX_JOB_PRICE)
    parser.add_argument("--jobs-per-hour", type=int,   default=DEFAULT_JOBS_PER_HOUR)
    parser.add_argument("--max-concurrent",type=int,   default=DEFAULT_MAX_CONCURRENT)
    parser.add_argument("--dry-run",       action="store_true")
    args = parser.parse_args()

    if args.multi:
        run_multi(args)
    else:
        b = Bootstrapper(
            agent_key=args.agent,
            daily_budget=args.daily_budget,
            max_job_price=args.max_price,
            jobs_per_hour=args.jobs_per_hour,
            max_concurrent=args.max_concurrent,
            dry_run=args.dry_run,
        )
        b.run()
