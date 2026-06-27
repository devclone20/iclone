"""
iCLONE — Server Watchdog

Checks if the ACP server process is alive.
If not, restarts it. Logs to ~/Library/Logs/iclone-watchdog.log.

Run as launchd job every 5 minutes (see com.iclone.watchdog.plist).

Usage:
  ~/Desktop/AI/iclone/venv312/bin/python3.12 ops/watchdog.py
"""

import os
import subprocess
import sys
import logging
import signal
import time
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / "Library" / "Logs" / "iclone-watchdog.log"
PID_FILE = Path.home() / "Library" / "Application Support" / "iclone" / "server.pid"
PROJECT = Path(__file__).parent.parent
VENV_PYTHON = PROJECT / "venv312" / "bin" / "python3.12"
SERVER_SCRIPT = PROJECT / "agent" / "server.py"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHDOG] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("watchdog")


def _ensure_dirs():
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _read_pid() -> int | None:
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except ValueError:
            return None
    return None


def _write_pid(pid: int):
    PID_FILE.write_text(str(pid))


def _process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)  # signal 0 = check existence
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _server_responsive() -> bool:
    """Check if the server process is running by name."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "agent/server.py"],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def _start_server() -> int:
    """Start the ACP server as a background process."""
    log.info("Starting iCLONE ACP server...")

    env = os.environ.copy()
    # Load .env.local into subprocess env
    env_local = Path.home() / ".env.local"
    env_file = PROJECT / ".env"

    for path in [env_file, env_local]:
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    # strip surrounding quotes
                    v = v.strip().strip('"').strip("'")
                    env.setdefault(k.strip(), v)

    proc = subprocess.Popen(
        [str(VENV_PYTHON), str(SERVER_SCRIPT)],
        cwd=str(PROJECT),
        env=env,
        stdout=open(Path.home() / "Library" / "Logs" / "iclone-server.log", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,  # detach from current session
    )

    time.sleep(2)  # give it a moment to start

    if proc.poll() is not None:
        log.error("Server exited immediately with code %d", proc.returncode)
        return -1

    log.info("Server started — PID %d", proc.pid)
    return proc.pid


def _check_wallet_deployed() -> bool:
    """Quick on-chain check — skip restart if wallet not deployed yet."""
    try:
        from web3 import Web3
        from dotenv import load_dotenv
        load_dotenv(Path.home() / ".env.local")
        load_dotenv(PROJECT / ".env", override=False)

        wallet = os.environ.get("AGENT_WALLET_ADDRESS", "")
        if not wallet:
            return False

        rpc = "https://alchemy-proxy-prod.virtuals.io/api/proxy/rpc"
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 5}))
        code = w3.eth.get_code(Web3.to_checksum_address(wallet))
        return len(code) > 0
    except Exception as e:
        log.warning("Wallet check failed: %s", e)
        return False


def run():
    _ensure_dirs()

    # Check wallet deployed — no point starting server if not
    if not _check_wallet_deployed():
        log.warning(
            "Smart wallet not deployed on Base mainnet — server not started. "
            "Deploy via Virtuals dashboard → Agent Settings → Register on ACP."
        )
        return

    pid = _read_pid()
    alive = pid and _process_alive(pid)
    responsive = _server_responsive()

    if alive and responsive:
        log.info("Server alive (PID %d) — no action needed.", pid)
        return

    if pid and not alive:
        log.warning("Server PID %d no longer alive — restarting.", pid)
    elif not responsive:
        log.warning("Server not found in process list — starting fresh.")

    new_pid = _start_server()
    if new_pid > 0:
        _write_pid(new_pid)
        log.info("Watchdog: server running at PID %d", new_pid)
    else:
        log.error("Watchdog: failed to start server — check iclone-server.log")


if __name__ == "__main__":
    # Can also accept --status flag
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        pid = _read_pid()
        alive = pid and _process_alive(pid)
        responsive = _server_responsive()
        wallet_ok = _check_wallet_deployed()
        print(f"PID file    : {pid or 'none'}")
        print(f"PID alive   : {alive}")
        print(f"Process found: {responsive}")
        print(f"Wallet deployed: {wallet_ok}")
        sys.exit(0 if (alive and responsive) else 1)
    else:
        run()
