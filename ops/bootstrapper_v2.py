#!/usr/bin/env python3
"""
iCLONE / VEGETA — Bootstrapper v2

Strategy: scan the ACP marketplace for active external agents, hire them for
micro-tasks ($0.05) so they see us as active market participants and return
as clients. Pure outbound procurement — no circular self-hiring.

Env:
  ACP_CONFIG_DIR      agent config dir (tokens + signer key)
  AGENT_NAME          label for logs (iCLONE, VEGETA)
  MY_WALLETS          comma-separated wallet addresses to EXCLUDE (our own agents)
  MAX_SPEND_USDC      max USDC to spend per cycle (default 0.20)
  HIRE_INTERVAL_MIN   minutes between hire cycles (default 30)
  BROWSE_QUERIES      comma-separated browse queries (default: research,crypto,trading)
  LOG_PATH            log file path
"""

import subprocess, json, time, random, logging, os, re
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
AGENT_NAME        = os.getenv("AGENT_NAME", "AGENT")
CHAIN_ID          = "8453"
CONFIG_DIR        = os.getenv("ACP_CONFIG_DIR", os.path.expanduser("~/.config/acp-iclone/acp"))
ENV               = {**os.environ, "ACP_CONFIG_DIR": CONFIG_DIR}
MAX_SPEND_USDC    = float(os.getenv("MAX_SPEND_USDC", "0.20"))
HIRE_INTERVAL_SEC = int(os.getenv("HIRE_INTERVAL_MIN", "30")) * 60
BROWSE_QUERIES    = [q.strip() for q in os.getenv("BROWSE_QUERIES", "crypto research trading analysis").split(",") if q.strip()]
MY_WALLETS        = {w.strip().lower() for w in os.getenv("MY_WALLETS", "").split(",") if w.strip()}
LOG_PATH          = os.getenv("LOG_PATH", f"/var/log/iclone/bootstrapper-{AGENT_NAME.lower()}.log")
MAX_PRICE_PER_JOB = 0.10  # never spend more than $0.10 on a single hire

ACP_BIN = next((p for p in ["/opt/homebrew/bin/acp", "/usr/local/bin/acp", "/usr/bin/acp"]
                if Path(p).exists()), "acp")

# ── Logging ───────────────────────────────────────────────────────────────────
Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
handlers = [logging.StreamHandler()]
try:
    handlers.append(logging.FileHandler(LOG_PATH))
except (PermissionError, OSError):
    pass
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=handlers,
)
log = logging.getLogger(f"bootstrapper.{AGENT_NAME.lower()}")

# ── State ─────────────────────────────────────────────────────────────────────
# Track agents we hired recently to avoid repeat spam (1h cooldown)
_hired_recently: dict[str, float] = {}   # wallet → epoch_sec
HIRE_COOLDOWN_SEC = 3600

# ── ACP helpers ───────────────────────────────────────────────────────────────
def acp(*args, timeout=90) -> dict:
    try:
        r = subprocess.run(
            [ACP_BIN, *[str(a) for a in args]],
            capture_output=True, text=True, timeout=timeout, env=ENV,
        )
        out = r.stdout.strip()
        # Try JSON first, else wrap raw output
        try:
            return json.loads(out) if out else {"success": r.returncode == 0}
        except json.JSONDecodeError:
            return {"raw": out, "stderr": r.stderr.strip(), "success": r.returncode == 0}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def get_active_wallet() -> str:
    try:
        cfg = json.loads((Path(CONFIG_DIR) / "config.json").read_text())
        return cfg.get("activeWallet", "").lower()
    except Exception:
        return ""


# ── Core: discover external agents ───────────────────────────────────────────
def browse_market(query: str) -> list[dict]:
    """Return list of external agent dicts from ACP browse."""
    result = acp("browse", query,
                 "--top-k", "20",
                 "--sort-by", "successfulJobCount",
                 "--online", "online",
                 "--json", timeout=60)
    if not result.get("success") and "data" not in result:
        log.debug("browse '%s' returned: %s", query, str(result)[:200])
        return []
    data = result.get("data", result if isinstance(result, list) else [])
    if isinstance(data, dict):
        data = data.get("agents", data.get("results", []))
    return data if isinstance(data, list) else []


def find_candidates() -> list[dict]:
    """Merge browse results across all queries, dedup by wallet."""
    my_wallet = get_active_wallet()
    all_wallets: set[str] = MY_WALLETS | {my_wallet}
    seen: dict[str, dict] = {}

    for q in BROWSE_QUERIES:
        agents = browse_market(q)
        log.info("browse '%s' → %d agents", q, len(agents))
        for a in agents:
            w = (a.get("walletAddress") or "").lower()
            if not w or w in all_wallets:
                continue
            if w in seen:
                continue
            seen[w] = a

    # Sort by successfulJobCount desc (prefer agents with proven track record)
    candidates = sorted(
        seen.values(),
        key=lambda a: int(a.get("successfulJobCount", 0)),
        reverse=True,
    )
    return candidates


def pick_offering(agent: dict) -> tuple[str, float] | None:
    """Pick the cheapest offering from an agent within our price cap."""
    offerings = agent.get("offerings") or agent.get("services") or []
    if not isinstance(offerings, list):
        return None

    best = None
    best_price = MAX_PRICE_PER_JOB + 1
    for o in offerings:
        if not isinstance(o, dict):
            continue
        name = o.get("name") or o.get("offeringName")
        if not name:
            continue
        # price can be in multiple fields depending on ACP version
        price = (
            o.get("priceV2", {}).get("value")
            or o.get("price")
            or o.get("priceValue")
            or o.get("priceUsdc")
        )
        try:
            price = float(price)
        except (TypeError, ValueError):
            continue
        if price < best_price:
            best_price = price
            best = (name, price)

    return best if best and best[1] <= MAX_PRICE_PER_JOB else None


def hire(agent: dict, offering: str, price: float) -> bool:
    """Create + fund a job with an external agent."""
    wallet = agent.get("walletAddress", "")
    name   = agent.get("name", wallet[:10])
    req    = json.dumps({
        "offering_id": offering,
        "query": random.choice(BROWSE_QUERIES),
        "requester": f"{AGENT_NAME} bootstrapper",
    })
    log.info("Hiring %s (%s) — offering=%s price=$%.2f", name, wallet[:12], offering, price)

    # Create job
    out, err, rc = _acp_raw("client", "create-job",
                             "--provider", wallet,
                             "--offering-name", offering,
                             "--requirements", req,
                             "--chain-id", CHAIN_ID)
    blob = out + " " + err
    m = re.search(r"#?(\d{4,})", blob)
    if not m:
        log.warning("create-job failed for %s: %s", name, blob[:200])
        return False
    job_id = m.group(1)
    log.info("Job #%s created with %s", job_id, name)

    # Wait for budget_set then fund
    if not _wait_status(job_id, "budget_set", timeout=120):
        log.warning("Job #%s never reached budget_set — skip fund", job_id)
        return False

    out, err, rc = _acp_raw("client", "fund",
                             "--job-id", job_id,
                             "--chain-id", CHAIN_ID)
    funded = rc == 0 or "funded" in (out + err).lower()
    if funded:
        log.info("Job #%s funded ✅ — waiting for delivery", job_id)
        _hired_recently[wallet.lower()] = time.time()
        # Wait for submitted (non-blocking — we return and check next cycle)
        return True
    else:
        log.warning("Job #%s fund FAILED: %s", job_id, err[:150])
        return False


def _acp_raw(*args, timeout=90) -> tuple[str, str, int]:
    try:
        r = subprocess.run([ACP_BIN, *args], capture_output=True, text=True, timeout=timeout, env=ENV)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 1
    except Exception as e:
        return "", str(e), 1


def _wait_status(job_id: str, target: str, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        out, _, _ = _acp_raw("job", "history", "--job-id", job_id, "--chain-id", CHAIN_ID)
        if out:
            first = out.splitlines()[0]
            parts = first.split("\t")
            st = parts[1].strip().lower() if len(parts) > 1 else ""
            if st == target:
                return True
            if st in ("rejected", "expired", "cancelled"):
                return False
        time.sleep(10)
    return False


def advance_inflight() -> int:
    """Complete (release escrow) for any submitted jobs we own as client."""
    my_wallet = get_active_wallet()
    if not my_wallet:
        return 0
    out, _, rc = _acp_raw("job", "list", "--json")
    if rc != 0 or not out:
        return 0
    try:
        jobs = json.loads(out).get("jobs", [])
    except json.JSONDecodeError:
        return 0

    advanced = 0
    for j in jobs:
        if j.get("clientAddress", "").lower() != my_wallet:
            continue
        list_st = (j.get("jobStatus", "") or "").lower()
        if list_st in ("completed", "rejected", "expired", "cancelled"):
            continue
        jid = str(j.get("onChainJobId", ""))
        # Check real status
        out2, _, _ = _acp_raw("job", "history", "--job-id", jid, "--chain-id", CHAIN_ID)
        st = ""
        if out2:
            parts = out2.splitlines()[0].split("\t")
            st = parts[1].strip().lower() if len(parts) > 1 else ""
        if st == "submitted":
            o, e, rc2 = _acp_raw("client", "complete", "--job-id", jid, "--chain-id", CHAIN_ID)
            ok = rc2 == 0 or "completed" in (o + e).lower()
            log.info("Complete job #%s → %s", jid, "✅" if ok else f"FAILED: {e[:100]}")
            if ok:
                advanced += 1
    return advanced


# ── Main loop ─────────────────────────────────────────────────────────────────
def run_hire_cycle() -> int:
    """One hire cycle: find candidates, spend up to MAX_SPEND_USDC."""
    candidates = find_candidates()
    if not candidates:
        log.info("No external candidates found — skip cycle")
        return 0

    now = time.time()
    spent = 0.0
    hired = 0

    for agent in candidates:
        wallet = (agent.get("walletAddress") or "").lower()

        # Cooldown check
        if now - _hired_recently.get(wallet, 0) < HIRE_COOLDOWN_SEC:
            continue

        pick = pick_offering(agent)
        if not pick:
            continue
        offering, price = pick

        if spent + price > MAX_SPEND_USDC:
            log.info("Budget cap reached ($%.2f / $%.2f) — stop cycle", spent, MAX_SPEND_USDC)
            break

        if hire(agent, offering, price):
            spent += price
            hired += 1

    log.info("Hire cycle done: %d hired, $%.2f spent", hired, spent)
    return hired


def main():
    my_wallet = get_active_wallet()
    log.info(
        "Bootstrapper v2 — agent=%s wallet=%s max_spend=$%.2f interval=%dmin queries=%s",
        AGENT_NAME, my_wallet[:12] if my_wallet else "?",
        MAX_SPEND_USDC, HIRE_INTERVAL_SEC // 60, BROWSE_QUERIES,
    )

    last_hire_cycle = 0.0

    while True:
        # Always advance inflight jobs (release escrow when work delivered)
        try:
            n = advance_inflight()
            if n:
                log.info("Escrow released for %d job(s)", n)
        except Exception as e:
            log.exception("advance_inflight error: %s", e)

        # Run hire cycle on interval
        now = time.time()
        if now - last_hire_cycle >= HIRE_INTERVAL_SEC:
            last_hire_cycle = now
            try:
                run_hire_cycle()
            except Exception as e:
                log.exception("hire cycle error: %s", e)

        time.sleep(30)


if __name__ == "__main__":
    main()
