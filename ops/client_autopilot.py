#!/usr/bin/env python3
"""
Generalized ACP Client Autopilot — reusable by ANY of our agents.

One codebase; behaviour is fully driven by env so each agent gets its own
hiring loop. Primary mode: hire a counterpart agent (mostly our own).
Optional: discover and hire EXTERNAL ACP agents (the "bootstrap" buy side).

Env:
  ACP_CONFIG_DIR          this agent's config dir (tokens + signer)
  AUTOPILOT_AGENT_NAME    label for logs (e.g. VEGETA, iCLONE)
  TARGET_WALLET           primary provider wallet to hire (the counterpart)
  TARGET_NAME             label for the counterpart (logs)
  JOBS_FILE               JSON file: [["offeringName", "{requirements json}"], ...]
  MINUTE_PARITY           odd | even | any  → alternating wall-clock cadence
  JOB_TIMEOUT             seconds to wait for each job phase (default 180)
  CYCLE_SLEEP             tick granularity in seconds (default 10)
  EXTERNAL_EVERY          hire an external agent every N internal cycles (0=off)
  EXTERNAL_QUERY          browse query for external discovery (e.g. "research")
  EXTERNAL_MAX_PRICE      max USDC to spend on an external job (default 0.10)
  LOG_PATH                log file (default ~/<agent>-autopilot.log)
"""
import subprocess, json, time, random, logging, os
from datetime import datetime, timezone
from pathlib import Path

AGENT_NAME   = os.getenv("AUTOPILOT_AGENT_NAME", "AGENT")
CHAIN_ID     = "8453"
CONFIG_DIR   = os.getenv("ACP_CONFIG_DIR", os.path.expanduser("~/.config/acp-iclone/acp"))
ENV          = {**os.environ, "ACP_CONFIG_DIR": CONFIG_DIR}

TARGET_WALLET = os.getenv("TARGET_WALLET", "").lower()
TARGET_NAME   = os.getenv("TARGET_NAME", "counterpart")
JOBS_FILE     = os.getenv("JOBS_FILE", "")
MINUTE_PARITY = os.getenv("MINUTE_PARITY", "any").lower()   # odd | even | any
JOB_TIMEOUT   = int(os.getenv("JOB_TIMEOUT", "180"))
CYCLE_SLEEP   = int(os.getenv("CYCLE_SLEEP", "30"))
MAX_ADVANCE_PER_PASS = int(os.getenv("MAX_ADVANCE_PER_PASS", "6"))

EXTERNAL_EVERY     = int(os.getenv("EXTERNAL_EVERY", "0"))
EXTERNAL_QUERY     = os.getenv("EXTERNAL_QUERY", "")
EXTERNAL_MAX_PRICE = float(os.getenv("EXTERNAL_MAX_PRICE", "0.10"))

LOG_PATH = os.getenv("LOG_PATH", os.path.expanduser(f"~/{AGENT_NAME.lower()}-autopilot.log"))

ACP_BIN = next((p for p in ["/opt/homebrew/bin/acp", "/usr/local/bin/acp", "/usr/bin/acp"]
                if Path(p).exists()), "acp")

# StreamHandler always (systemd captures stdout to the unit's log file). Add a
# FileHandler only when LOG_PATH is writable — avoids fighting systemd over the
# same file (double-write / permission errors) under StandardOutput=append.
_handlers: list[logging.Handler] = [logging.StreamHandler()]
try:
    _fh = logging.FileHandler(LOG_PATH)
    # Only keep it if it won't collide with systemd's own append handle.
    if not os.getenv("INVOCATION_ID"):  # set by systemd; absent on manual runs
        _handlers.append(_fh)
    else:
        _fh.close()
except (PermissionError, OSError):
    pass
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=_handlers,
)
log = logging.getLogger(f"{AGENT_NAME.lower()}.autopilot")


def acp_run(*args) -> tuple[str, str, int]:
    r = subprocess.run([ACP_BIN, *args], capture_output=True, text=True, timeout=90, env=ENV)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def load_jobs() -> list[tuple[str, str]]:
    """[ [offeringName, requirementsJson], ... ] from JOBS_FILE."""
    if not JOBS_FILE:
        return []
    p = Path(JOBS_FILE)
    if not p.is_absolute():
        p = Path(__file__).parent.parent / JOBS_FILE
    if not p.exists():
        log.error("JOBS_FILE not found: %s", p)
        return []
    data = json.loads(p.read_text())
    return [(j[0], j[1]) for j in data]


JOBS = load_jobs()


def get_job_status(job_id: str) -> str | None:
    out, _, _ = acp_run("job", "history", "--job-id", job_id, "--chain-id", CHAIN_ID)
    if not out:
        return None
    first = out.splitlines()[0]
    parts = first.split("\t")
    return parts[1].strip().lower() if len(parts) > 1 else None


def wait_for_status(job_id: str, target: str, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        st = get_job_status(job_id)
        log.info("Job #%s status: %s (waiting for %s)", job_id, st, target)
        if st == target:
            return True
        if st in ("rejected", "expired", "cancelled"):
            log.warning("Job #%s terminal state %s — abort wait", job_id, st)
            return False
        time.sleep(15)
    log.warning("Job #%s timed out waiting for %s", job_id, target)
    return False


def create_job(provider_wallet: str, offering: str, requirements: str) -> str | None:
    # Always inject offering_id — ACP does not propagate the offering name to providers.
    try:
        req = json.loads(requirements)
        req.setdefault("offering_id", offering)
        requirements = json.dumps(req)
    except json.JSONDecodeError:
        requirements = json.dumps({"offering_id": offering, "input": requirements})
    out, err, rc = acp_run(
        "client", "create-job",
        "--provider", provider_wallet,
        "--offering-name", offering,
        "--requirements", requirements,
        "--chain-id", CHAIN_ID,
    )
    blob = out + " " + err
    import re
    m = re.search(r"#?(\d{4,})", blob)
    if rc == 0 and m:
        job_id = m.group(1)
        log.info("Job #%s created → %s (offering: %s)", job_id, provider_wallet[:10], offering)
        return job_id
    log.error("create-job failed: %s | %s", out[:200], err[:200])
    return None


def fund_job(job_id: str) -> bool:
    out, err, rc = acp_run("client", "fund", "--job-id", job_id, "--chain-id", CHAIN_ID)
    ok = rc == 0 or "funded" in (out + err).lower()
    log.info("Job #%s funded %s", job_id, "✅" if ok else f"FAILED: {err[:120]}")
    return ok


def complete_job(job_id: str) -> bool:
    out, err, rc = acp_run("client", "complete", "--job-id", job_id, "--chain-id", CHAIN_ID)
    ok = rc == 0 or "completed" in (out + err).lower()
    log.info("Job #%s completed %s", job_id, "✅ escrow released" if ok else f"FAILED: {err[:120]}")
    return ok


def _my_wallet() -> str:
    try:
        cfg = json.loads((Path(CONFIG_DIR) / "config.json").read_text())
        return cfg.get("activeWallet", "").lower()
    except Exception:
        return ""


MY_WALLET = _my_wallet()


def advance_inflight() -> int:
    """Non-blocking single pass: fund budget_set jobs, complete submitted jobs
    where WE are the client. Keeps the per-minute fire fast (no waiting)."""
    out, _, rc = acp_run("job", "list", "--json")
    if rc != 0 or not out:
        return 0
    try:
        jobs = json.loads(out).get("jobs", [])
    except json.JSONDecodeError:
        return 0
    advanced = 0
    checks = 0
    for j in jobs:
        if j.get("clientAddress", "").lower() != MY_WALLET:
            continue
        list_st = (j.get("jobStatus", "") or "").lower()
        if list_st in ("completed", "rejected", "expired", "cancelled"):
            continue
        # Cap history lookups per pass — each acp call spawns a heavy Node
        # process; on a 1-vCPU box an unbounded backlog scan saturates the CPU.
        if checks >= MAX_ADVANCE_PER_PASS:
            break
        checks += 1
        jid = str(j.get("onChainJobId", ""))
        # `acp job list` reports budget_set jobs as "open" — confirm the TRUE
        # status via job history, otherwise we never fund and a backlog builds.
        st = get_job_status(jid) or list_st
        if st in ("budget_set", "budgetset"):
            if fund_job(jid):
                advanced += 1
        elif st == "submitted":
            if complete_job(jid):
                advanced += 1
    return advanced


def create_one(provider_wallet: str, offering: str, requirements: str, label: str) -> bool:
    """Fire a new job and return immediately — the provider sets budget async,
    we fund/complete it on later ticks via advance_inflight()."""
    log.info("── Hiring %s: %s ──", label, offering)
    return bool(create_job(provider_wallet, offering, requirements))


def hire_internal() -> bool:
    if not JOBS or not TARGET_WALLET:
        log.warning("No JOBS or TARGET_WALLET configured — skip internal cycle")
        return False
    offering, requirements = random.choice(JOBS)
    return create_one(TARGET_WALLET, offering, requirements, TARGET_NAME)


def discover_external() -> list[dict]:
    """Browse the ACP market for external agents matching EXTERNAL_QUERY."""
    if not EXTERNAL_QUERY:
        return []
    out, err, rc = acp_run("browse", EXTERNAL_QUERY, "--top-k", "10",
                           "--sort-by", "successfulJobCount", "--online", "online", "--json")
    if rc != 0 or not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    agents = data.get("data", data if isinstance(data, list) else [])
    ours = {TARGET_WALLET}
    return [a for a in agents
            if a.get("walletAddress", "").lower() not in ours
            and a.get("walletAddress")]


def hire_external() -> bool:
    """Bootstrap buy-side: hire a real external agent (spends real USDC)."""
    candidates = discover_external()
    if not candidates:
        log.info("External discovery: no candidates for '%s'", EXTERNAL_QUERY)
        return False
    for a in candidates:
        wallet = a.get("walletAddress", "")
        offs = a.get("offerings") or a.get("services") or []
        for o in (offs if isinstance(offs, list) else []):
            name = o.get("name") if isinstance(o, dict) else None
            price = float(o.get("priceValue", o.get("price", 999)) or 999) if isinstance(o, dict) else 999
            if name and price <= EXTERNAL_MAX_PRICE:
                log.info("External hire → %s (%s) @ $%s", a.get("name"), name, price)
                reqs = json.dumps({"offering_id": name, "query": EXTERNAL_QUERY,
                                   "note": "autonomous procurement"})
                return create_one(wallet, name, reqs, f"EXTERNAL:{a.get('name','?')}")
    log.info("External discovery: %d agents, none within $%.2f", len(candidates), EXTERNAL_MAX_PRICE)
    return False


FIRE_PERIOD = int(os.getenv("FIRE_PERIOD_MIN", "0"))   # 0 = use legacy parity
FIRE_OFFSET = int(os.getenv("FIRE_OFFSET_MIN", "0"))


def fire_now() -> bool:
    """Should this agent create a new job this minute?

    Preferred: slot mode — fire when minute % FIRE_PERIOD == FIRE_OFFSET.
    Two agents with the same period and offsets 0 / period/2 alternate evenly
    (e.g. period 8, offsets 0 & 4 → one job every 4 min, alternating).
    Legacy: parity mode (odd/even/any) when FIRE_PERIOD is 0."""
    minute = datetime.now(timezone.utc).minute
    if FIRE_PERIOD > 0:
        return (minute % FIRE_PERIOD) == (FIRE_OFFSET % FIRE_PERIOD)
    if MINUTE_PARITY == "any":
        return True
    return (minute % 2 == 1) if MINUTE_PARITY == "odd" else (minute % 2 == 0)


def main():
    log.info("%s client autopilot — target=%s parity=%s jobs=%d external_every=%d wallet=%s",
             AGENT_NAME, TARGET_NAME, MINUTE_PARITY, len(JOBS), EXTERNAL_EVERY, MY_WALLET[:10])

    last_fired_minute = -1
    cycle_count = 0
    while True:
        # Every tick: advance in-flight jobs (fund/complete) — fast, non-blocking,
        # independent of parity so jobs settle quickly in both directions.
        try:
            advance_inflight()
        except Exception as e:
            log.exception("advance_inflight error: %s", e)

        now = datetime.now(timezone.utc)
        if fire_now() and now.minute != last_fired_minute:
            last_fired_minute = now.minute
            cycle_count += 1
            try:
                if EXTERNAL_EVERY and cycle_count % EXTERNAL_EVERY == 0:
                    hire_external() or hire_internal()
                else:
                    hire_internal()
            except Exception as e:
                log.exception("Cycle error: %s", e)
        time.sleep(CYCLE_SLEEP)


if __name__ == "__main__":
    main()
