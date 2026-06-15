"""
iCLONE — Production ACP Server (polling-based)

Architecture:
  poll loop (30s) → acp job list → route by jobStatus
  open   → acp provider set-budget
  funded → execute_offering() → acp provider submit
  Supabase → record every state transition

Resilient to Virtuals API outages: uses exponential backoff,
auto-recovers when API comes back, catches all jobs including
those created during an outage.

Run:
  ~/Desktop/AI/iclone/venv312/bin/python3.12 agent/server.py
"""

import fcntl
import json
import logging
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path.home() / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env", override=False)

sys.path.insert(0, str(Path(__file__).parent))

from iclone.skills.acp_skill import ACPSkill
from iclone.skills.execution_engine import ExecutionEngine
from iclone import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(f"iclone.server.{os.environ.get('ICLONE_AGENT_NAME', 'CLONE')}")

AGENT_NAME    = os.environ.get("ICLONE_AGENT_NAME", "CLONE")
CHAIN_ID      = 8453  # Base mainnet
POLL_INTERVAL = 30    # seconds between job list polls
MAX_BACKOFF   = 300   # max backoff seconds when API is down

ACP_CONFIG_DIR  = os.environ.get("ACP_CONFIG_DIR", str(Path.home() / ".config/acp-iclone/acp"))
ACP_CONFIG_FILE = Path(ACP_CONFIG_DIR) / "config.json"


def _load_identity() -> tuple[str, str]:
    """This agent's (provider wallet, agent id), read from its own config.json.
    Env overrides: ICLONE_PROVIDER_WALLET, ICLONE_AGENT_ID. Lets one codebase
    run as any agent — the wallet gates which jobs this server provides for."""
    wallet = os.environ.get("ICLONE_PROVIDER_WALLET", "").lower()
    agent_id = os.environ.get("ICLONE_AGENT_ID", "")
    try:
        cfg = json.loads(ACP_CONFIG_FILE.read_text())
        if not wallet:
            wallet = cfg.get("activeWallet", "").lower()
        if not agent_id:
            for w, a in cfg.get("agents", {}).items():
                if w.lower() == wallet:
                    agent_id = a.get("id", "")
                    break
    except Exception:
        pass
    return wallet, agent_id


ICLONE_WALLET, ICLONE_AGENT_ID = _load_identity()
# Lock is per-agent (per config dir) so multiple agent servers don't serialize each other
ACP_LOCK_FILE   = f"/tmp/iclone-acp-{Path(ACP_CONFIG_DIR).parent.name}.lock"

_ACP_CANDIDATES = [
    "/opt/homebrew/bin/acp",
    "/usr/local/bin/acp",
    "/usr/bin/acp",
]
ACP_BIN = next((p for p in _ACP_CANDIDATES if Path(p).exists()), "acp")


@contextmanager
def acp_exclusive():
    """Exclusive lock so server and autopilot don't conflict on active agent."""
    with open(ACP_LOCK_FILE, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def ensure_iclone_active():
    """Switch active agent to iCLONE if needed."""
    try:
        cfg = json.loads(ACP_CONFIG_FILE.read_text())
        if cfg.get("activeWallet", "").lower() != ICLONE_WALLET:
            subprocess.run(
                [ACP_BIN, "agent", "use", "--agent-id", ICLONE_AGENT_ID],
                capture_output=True, text=True, timeout=30
            )
    except Exception:
        pass


def acp(*args: str, check: bool = True, timeout: int = 60) -> dict[str, Any]:
    """Run an acp-cli command and return parsed JSON output."""
    cmd = [ACP_BIN, *args, "--json"]
    env = {**os.environ, "ACP_CONFIG_DIR": ACP_CONFIG_DIR}
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        output = result.stdout.strip() or result.stderr.strip()
        if not output:
            return {}
        parsed = json.loads(output)
        if check and result.returncode != 0 and "error" in parsed:
            raise RuntimeError(f"acp {' '.join(args)}: {parsed['error']}")
        return parsed
    except json.JSONDecodeError:
        logger.error("acp %s → non-JSON: %s", " ".join(args), (result.stdout or result.stderr)[:200])
        return {}
    except subprocess.TimeoutExpired:
        logger.error("acp %s timed out", " ".join(args))
        return {}


def poll_active_jobs() -> list[dict]:
    """Fetch all active jobs from the Virtuals API. Returns [] on outage."""
    result = acp("job", "list", check=False, timeout=45)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result.get("jobs", [])


def get_job_entries(job_id: str) -> dict:
    """Fetch full job history (entries, status, offering context)."""
    result = acp("job", "history", "--job-id", job_id, "--chain-id", str(CHAIN_ID), check=False, timeout=60)
    if "error" in result:
        raise RuntimeError(result["error"])
    return result


class ICloneACPServer:
    def __init__(self):
        self.skill = ACPSkill()
        self.engine = ExecutionEngine()
        self.offerings = self._load_offerings()
        self.job_state: dict[str, dict] = {}
        # Track jobs where we already set budget / submitted to avoid re-processing
        self.budget_set_jobs: set[str] = set()
        self.submitted_jobs: set[str] = set()
        self.jobs_processed = 0
        self.jobs_failed = 0

    def _load_offerings(self) -> dict[str, dict]:
        # Per-agent offerings file (env-overridable so one codebase serves N agents)
        offerings_file = os.environ.get("ICLONE_OFFERINGS_FILE", "published_offerings.json")
        offerings_path = Path(offerings_file)
        if not offerings_path.is_absolute():
            offerings_path = Path(__file__).parent.parent / offerings_file
        if not offerings_path.exists():
            logger.warning("Offerings file not found: %s", offerings_path)
            return {}
        data = json.loads(offerings_path.read_text())
        result = {}
        for o in data.get("published", []):
            result[o["offering_id"]] = o
            cli_name = o["offering_id"].replace("iclone-", "").replace("-v1", "").replace("-", "_")
            result[cli_name] = o
        return result

    def _get_offering_by_name(self, name: str) -> dict | None:
        if name in self.offerings:
            return self.offerings[name]
        acp_off = self.skill._offerings.get(name)
        if acp_off:
            return {"price_usdc": acp_off.price_usdc, "offering_id": name}
        normalized = name.lower().replace("iclone", "").strip("-_")
        for key, val in self.offerings.items():
            if normalized in key.lower():
                return val
        return None

    def _extract_offering_context(self, job: dict, entries: dict) -> tuple[str, dict, float]:
        """
        Extract (offering_name, requirements, price_usdc) from job data and history entries.
        Falls back to defaults if data is missing.
        """
        offering_name = ""
        requirements: dict = {}

        # Try to extract from job history entries
        entry_list = entries.get("entries", [])
        for entry in entry_list:
            content_raw = entry.get("content", "")
            if not content_raw:
                continue
            try:
                content = json.loads(content_raw) if isinstance(content_raw, str) else content_raw
                if isinstance(content, dict):
                    offering_name = content.get("offering_id", content.get("offeringName", offering_name))
                    requirements = content.get("requirements", content.get("params", requirements))
                    if offering_name:
                        break
            except (json.JSONDecodeError, TypeError):
                pass

        offering = self._get_offering_by_name(offering_name) if offering_name else None
        price = offering["price_usdc"] if offering else 0.25
        offering_id = offering["offering_id"] if offering else (offering_name or "unknown")

        return offering_id, requirements, price

    def process_job(self, job: dict) -> None:
        job_id = str(job.get("onChainJobId", ""))
        status = job.get("jobStatus", "").lower()
        provider_addr = job.get("providerAddress", "").lower()
        chain_id = int(job.get("chainId", CHAIN_ID))

        if provider_addr != ICLONE_WALLET:
            return  # not our job

        if status == "open" and job_id not in self.budget_set_jobs:
            logger.info("Job %s is open — setting budget", job_id)
            with acp_exclusive():
                ensure_iclone_active()
                self._handle_set_budget(job_id, chain_id)

        elif status == "funded" and job_id not in self.submitted_jobs:
            logger.info("Job %s is funded — executing and submitting", job_id)
            with acp_exclusive():
                ensure_iclone_active()
                self._handle_submit(job_id, chain_id)

        elif status in ("completed", "rejected", "expired"):
            self._handle_terminal(job_id, status)

    def _handle_set_budget(self, job_id: str, chain_id: int) -> None:
        # Fetch job context for offering name/requirements
        try:
            entries = get_job_entries(job_id)
        except Exception as e:
            logger.warning("Could not fetch history for job %s: %s — using defaults", job_id, e)
            entries = {}

        offering_id, requirements, price = self._extract_offering_context({}, entries)

        self.job_state[job_id] = {
            "requirements": requirements,
            "offering_id": offering_id,
            "chain_id": chain_id,
            "price_usdc": price,
        }

        logger.info("Setting budget for job %s: $%.2f (offering: %s)", job_id, price, offering_id)
        result = acp(
            "provider", "set-budget",
            "--job-id", job_id,
            "--amount", str(price),
            "--chain-id", str(chain_id),
            check=False,
        )

        if result.get("success"):
            self.budget_set_jobs.add(job_id)
            logger.info("Budget set for job %s ✓", job_id)
            try:
                db.upsert_acp_job(
                    job_id=job_id,
                    offering_id=offering_id,
                    client_agent_id="",
                    status="accepted",
                    price_usdc=price,
                    requirements=requirements,
                )
            except Exception as e:
                logger.warning("DB upsert failed for job %s: %s", job_id, e)
        else:
            logger.error("Failed to set budget for job %s: %s", job_id, result)
            # If it already errored with "already set" or similar, mark as done
            err_msg = str(result.get("error", "")).lower()
            if "already" in err_msg or "budget" in err_msg:
                self.budget_set_jobs.add(job_id)

    def _handle_submit(self, job_id: str, chain_id: int) -> None:
        state = self.job_state.get(job_id, {})
        offering_id = state.get("offering_id", "")
        requirements = state.get("requirements", {})
        price_usdc = state.get("price_usdc", 0.0)

        # If we don't have state (e.g. server restarted between set-budget and submit)
        if not offering_id:
            try:
                entries = get_job_entries(job_id)
                offering_id, requirements, price_usdc = self._extract_offering_context({}, entries)
                self.job_state[job_id] = {
                    "requirements": requirements,
                    "offering_id": offering_id,
                    "chain_id": chain_id,
                    "price_usdc": price_usdc,
                }
            except Exception as e:
                logger.warning("Could not fetch context for job %s: %s", job_id, e)

        logger.info("Executing job %s — offering: %s", job_id, offering_id)
        offering_meta = self._get_offering_by_name(offering_id) or {}
        import concurrent.futures as _cf
        with _cf.ThreadPoolExecutor(max_workers=1) as _pool:
            _future = _pool.submit(self.engine.execute, offering_id, requirements, offering_meta)
            try:
                result = _future.result(timeout=120)
            except _cf.TimeoutError:
                logger.error("Execution timed out for job %s after 120s", job_id)
                from iclone.skills.base_skill import SkillResult
                result = SkillResult(success=False, output="", error="execution timed out after 120s")

        if not result.success:
            logger.error("Execution failed for job %s: %s", job_id, result.error)
            self.jobs_failed += 1
            try:
                db.upsert_acp_job(
                    job_id=job_id,
                    offering_id=offering_id,
                    client_agent_id="",
                    status="disputed",
                    price_usdc=price_usdc,
                    error_message=result.error,
                )
            except Exception:
                pass
            acp(
                "provider", "submit",
                "--job-id", job_id,
                "--deliverable", json.dumps({"error": result.error, "status": "failed"}),
                "--chain-id", str(chain_id),
                check=False,
            )
            self.submitted_jobs.add(job_id)
            return

        deliverable = json.dumps(result.data, ensure_ascii=False)
        if len(deliverable) > 8000:
            deliverable = json.dumps({"truncated": True, "preview": deliverable[:500]})

        sub = acp(
            "provider", "submit",
            "--job-id", job_id,
            "--deliverable", deliverable,
            "--chain-id", str(chain_id),
            check=False,
        )

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()

        if sub.get("success"):
            self.submitted_jobs.add(job_id)
            logger.info("Deliverable submitted for job %s ✓", job_id)
            self.jobs_processed += 1
            try:
                db.upsert_acp_job(
                    job_id=job_id,
                    offering_id=offering_id,
                    client_agent_id="",
                    status="delivered",
                    price_usdc=price_usdc,
                    deliverable=deliverable[:500],
                    delivered_at=now,
                )
            except Exception:
                pass
        else:
            logger.error("Submit failed for job %s: %s", job_id, sub)
            err_msg = str(sub.get("error", "")).lower()
            if "already" in err_msg:
                self.submitted_jobs.add(job_id)
            else:
                self.jobs_failed += 1
                try:
                    db.upsert_acp_job(
                        job_id=job_id,
                        offering_id=offering_id,
                        client_agent_id="",
                        status="disputed",
                        price_usdc=price_usdc,
                        error_message=str(sub),
                    )
                except Exception:
                    pass

        logger.info(
            "Job %s done — processed: %d | failed: %d",
            job_id, self.jobs_processed, self.jobs_failed,
        )

    def _handle_terminal(self, job_id: str, status: str) -> None:
        state = self.job_state.pop(job_id, {})
        if status == "completed":
            logger.info("Job %s completed — payment released", job_id)
            try:
                db.upsert_acp_job(
                    job_id=job_id,
                    offering_id=state.get("offering_id", ""),
                    client_agent_id="",
                    status="completed",
                    price_usdc=state.get("price_usdc", 0.0),
                )
            except Exception:
                pass
        else:
            logger.info("Job %s ended: %s", job_id, status)
        # Cleanup tracking sets for terminal jobs
        self.budget_set_jobs.discard(job_id)
        self.submitted_jobs.discard(job_id)

    def run(self) -> None:
        logger.info("Starting %s ACP provider server (polling mode)...", AGENT_NAME)

        whoami = acp("agent", "whoami", check=False)
        if "error" in whoami:
            logger.error("acp agent whoami failed — run: acp configure && acp agent use")
            sys.exit(1)

        agent_name = whoami.get("name", "?")
        wallet = whoami.get("walletAddress", "?")
        offering_count = len(whoami.get("offerings", []))
        logger.info(
            "Agent: %s | Wallet: %s | Offerings: %d",
            agent_name, wallet, offering_count,
        )
        logger.info(
            "%s LIVE — polling every %ds | wallet: %s",
            AGENT_NAME, POLL_INTERVAL, wallet,
        )

        backoff = POLL_INTERVAL
        consecutive_failures = 0

        try:
            while True:
                try:
                    jobs = poll_active_jobs()
                    consecutive_failures = 0
                    backoff = POLL_INTERVAL  # reset on success

                    if jobs:
                        logger.info("Polled %d active job(s)", len(jobs))
                    else:
                        logger.debug("No active jobs")

                    for job in jobs:
                        try:
                            self.process_job(job)
                        except Exception as e:
                            logger.error(
                                "Error processing job %s: %s",
                                job.get("onChainJobId", "?"), e,
                                exc_info=True,
                            )

                except RuntimeError as e:
                    consecutive_failures += 1
                    # Exponential backoff: 30s → 60s → 120s → 300s (max)
                    backoff = min(POLL_INTERVAL * (2 ** min(consecutive_failures - 1, 3)), MAX_BACKOFF)
                    logger.warning(
                        "API unavailable (%s) — retry in %ds (failure #%d)",
                        e, backoff, consecutive_failures,
                    )
                except Exception as e:
                    consecutive_failures += 1
                    backoff = min(POLL_INTERVAL * (2 ** min(consecutive_failures - 1, 3)), MAX_BACKOFF)
                    logger.error("Unexpected error: %s — retry in %ds", e, backoff, exc_info=True)

                time.sleep(backoff)

        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    server = ICloneACPServer()
    server.run()
