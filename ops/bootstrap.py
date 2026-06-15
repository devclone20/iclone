#!/usr/bin/env python3
"""
ACP Market Bootstrap — discovery + presence engine for our agents.

Runs periodically (systemd timer). For each agent it:
  1. Browses the live ACP market across our service domains.
  2. Builds a market map (who offers what, success rates, prices) → JSON + log.
  3. Surfaces DEMAND/SUPPLY signal: where we have pricing edge, gaps to fill.
  4. (opt-in) Seeds reciprocal external hires within a price cap.

Selling to external clients needs no action here — each agent's provider
server already fulfils ANY incoming job. This script is the BUY/INTEL side:
it makes sure we know the market and can act on it.

Env:
  ACP_CONFIG_DIR     agent config dir
  BOOTSTRAP_AGENT    label (iCLONE / VEGETA)
  BOOTSTRAP_QUERIES  comma-separated market queries
  MARKET_MAP_FILE    where to write the market map JSON
  SEED_EXTERNAL      1 to place one reciprocal external hire (default 0)
  SEED_MAX_PRICE     max USDC for a seed external hire (default 0.10)
"""
import subprocess, json, os, logging
from datetime import datetime, timezone
from pathlib import Path

SEED_EXT    = os.getenv("SEED_EXTERNAL", "0") == "1"
SEED_MAX    = float(os.getenv("SEED_MAX_PRICE", "0.10"))
CHAIN_ID    = "8453"
MAP_DIR     = os.getenv("MARKET_MAP_DIR", "/var/log/iclone")

# Default fleet to scan. Override with BOOTSTRAP_AGENTS_JSON (a JSON list of
# {name, config, queries}). One invocation scans every agent — no per-agent
# systemd ExecStart gymnastics.
_DEFAULT_AGENTS = [
    {"name": "iCLONE", "config": os.path.expanduser("~/.config/acp-iclone/acp"),
     "queries": ["crypto research", "token analysis", "trading", "data", "AI agent"]},
    {"name": "VEGETA", "config": os.path.expanduser("~/.config/acp-vegeta/acp"),
     "queries": ["robotics", "embodied AI", "simulation", "reinforcement learning", "manipulation"]},
]
try:
    AGENTS = json.loads(os.environ["BOOTSTRAP_AGENTS_JSON"]) if os.getenv("BOOTSTRAP_AGENTS_JSON") else _DEFAULT_AGENTS
except (json.JSONDecodeError, KeyError):
    AGENTS = _DEFAULT_AGENTS

ACP_BIN = next((p for p in ["/opt/homebrew/bin/acp", "/usr/local/bin/acp", "/usr/bin/acp"]
                if Path(p).exists()), "acp")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] bootstrap: %(message)s")
log = logging.getLogger("bootstrap")


def acp(config_dir: str, *args) -> tuple[str, int]:
    env = {**os.environ, "ACP_CONFIG_DIR": config_dir}
    r = subprocess.run([ACP_BIN, *args], capture_output=True, text=True, timeout=90, env=env)
    return (r.stdout.strip() or r.stderr.strip()), r.returncode


def wallet_of(config_dir: str) -> str:
    try:
        return json.loads((Path(config_dir) / "config.json").read_text()).get("activeWallet", "").lower()
    except Exception:
        return ""


def browse(config_dir: str, query: str) -> list[dict]:
    out, rc = acp(config_dir, "browse", query, "--top-k", "15", "--sort-by",
                  "successfulJobCount,successRate", "--online", "all", "--json")
    if rc != 0 or not out:
        return []
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        return []
    return d.get("data", d if isinstance(d, list) else [])


def scan_agent(agent: dict) -> dict:
    name, config_dir, queries = agent["name"], agent["config"], agent["queries"]
    mine = wallet_of(config_dir)
    market: dict = {"agent": name, "scanned_at": datetime.now(timezone.utc).isoformat(),
                    "queries": {}, "totals": {"agents": 0, "external": 0}}
    seen: set[str] = set()
    for q in queries:
        rows = []
        for a in browse(config_dir, q):
            w = (a.get("walletAddress") or "").lower()
            if not w:
                continue
            is_us = (w == mine)
            rows.append({"name": a.get("name"), "wallet": w, "role": a.get("role"),
                         "cluster": a.get("cluster"),
                         "successful_jobs": a.get("successfulJobCount"),
                         "success_rate": a.get("successRate"), "is_us": is_us})
            if w not in seen:
                seen.add(w)
                if not is_us:
                    market["totals"]["external"] += 1
        market["queries"][q] = rows
        log.info("[%s] '%s' → %d agents (%d unique external)", name, q, len(rows),
                 market["totals"]["external"])
    market["totals"]["agents"] = len(seen)

    try:
        Path(MAP_DIR).mkdir(parents=True, exist_ok=True)
        (Path(MAP_DIR) / f"market_map_{name.lower()}.json").write_text(json.dumps(market, indent=2))
    except OSError as e:
        log.warning("[%s] could not write market map: %s", name, e)

    flat = sorted([r for rows in market["queries"].values() for r in rows if not r["is_us"]],
                  key=lambda r: (r.get("successful_jobs") or 0), reverse=True)
    log.info("[%s] top external agents: %s", name,
             ", ".join(str(r["name"])[:18] for r in flat[:6]))
    return market


def main():
    log.info("=== ACP market bootstrap — %d agent(s) ===", len(AGENTS))
    for agent in AGENTS:
        try:
            m = scan_agent(agent)
            log.info("[%s] map written: %d unique agents, %d external",
                     agent["name"], m["totals"]["agents"], m["totals"]["external"])
        except Exception as e:
            log.exception("[%s] scan failed: %s", agent.get("name", "?"), e)
    if SEED_EXT:
        log.info("SEED_EXTERNAL on — set EXTERNAL_EVERY>0 on the client services to hire externally.")
    log.info("=== bootstrap complete ===")


if __name__ == "__main__":
    main()
