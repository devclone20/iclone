#!/usr/bin/env python3
"""
ACP Token Refresh Daemon
Strategy: call `acp agent whoami` via the CLI every 20 min.
The CLI manages its own file-keyring tokens internally — it auto-refreshes the
access token using its stored refresh token on every call.
If whoami fails with "Session expired", the refresh token itself is dead and
manual re-login is required (acp configure).
"""
import subprocess, time, logging, os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] token_refresh: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/tmp/acp-token-refresh.log"),
    ],
)
log = logging.getLogger(__name__)

REFRESH_INTERVAL = 20 * 60  # 20 minutes (access token = 60 min, refresh before half-life)

ACP_BIN = next(
    (p for p in ["/opt/homebrew/bin/acp", "/usr/local/bin/acp"] if os.path.exists(p)),
    "acp",
)

# Portable across Mac (dev) and Linux droplet (prod) — resolves under $HOME.
_CFG = os.path.join(os.path.expanduser("~"), ".config")
CONFIGS = {
    "CLONE":  os.path.join(_CFG, "acp-iclone", "acp"),
    "VEGETA": os.path.join(_CFG, "acp-vegeta", "acp"),
}


def keep_alive(name: str, config_dir: str) -> bool:
    """Call whoami to force the CLI to use (and rotate) its refresh token."""
    env = {**os.environ, "ACP_CONFIG_DIR": config_dir}
    r = subprocess.run(
        [ACP_BIN, "agent", "whoami"],
        capture_output=True, text=True, timeout=30, env=env,
    )
    combined = (r.stdout + r.stderr).lower()

    if "session expired" in combined or "unauthorized" in combined:
        log.error(
            "%s: SESSION EXPIRED — manual re-login required:\n"
            "  ACP_CONFIG_DIR=%s acp configure",
            name, config_dir,
        )
        return False

    if r.returncode != 0:
        log.warning("%s: whoami non-zero (rc=%d) — %s", name, r.returncode, (r.stdout + r.stderr)[:200])
        return False

    # Parse name from output (text format: "name: AGENTNAME")
    agent_name = ""
    for line in r.stdout.splitlines():
        if line.startswith("name:"):
            agent_name = line.split(":", 1)[1].strip()
            break

    log.info("%s (%s): token alive ✓", name, agent_name or "?")
    return True


def main():
    log.info("Token refresh daemon started — interval=%ds (every %d min)", REFRESH_INTERVAL, REFRESH_INTERVAL // 60)
    while True:
        for name, config_dir in CONFIGS.items():
            try:
                keep_alive(name, config_dir)
            except subprocess.TimeoutExpired:
                log.warning("%s: whoami timed out", name)
            except Exception as e:
                log.error("%s: unexpected error — %s", name, e)
        log.info("Next keep-alive in %d min", REFRESH_INTERVAL // 60)
        time.sleep(REFRESH_INTERVAL)


if __name__ == "__main__":
    main()
