"""
iCLONE — Multi-Agent Bootstrap
Starts 4 independent ACP server processes (one per agent), each with its own
isolated acp-cli config directory so they can run in parallel without conflict.

Usage:
    python3 ops/bootstrap_all_agents.py          # start all 4 agents
    python3 ops/bootstrap_all_agents.py --status # check running status
    python3 ops/bootstrap_all_agents.py --stop   # stop all agents

Architecture:
    Each agent gets:
      - /tmp/iclone-acp-<agent>/config.json   (isolated acp-cli config)
      - /tmp/iclone-events-<agent>.jsonl       (isolated event stream file)
      - /tmp/iclone-<agent>.pid                (PID file for process management)
      - ~/Library/Logs/iCLONE/<agent>.log      (persistent log)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

# ── Agent registry ─────────────────────────────────────────────────────────

AGENTS = [
    {
        "id":      "019eae06-96cd-77d0-8f8b-a6abb71f0cd7",
        "name":    "CLONE",
        "wallet":  "0x44cc25d55a4291b92f52062ba023ca1f14206664",
        "slug":    "clone",
    },
    {
        "id":      "019ebb92-7415-7baa-93e9-ee19a7742877",
        "name":    "SuperSayatin",
        "wallet":  "0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3",
        "slug":    "supersayatin",
        "active":  False,
    },
    {
        "id":      "019ebb92-93e8-7b4e-b2e8-39c3419843c9",
        "name":    "DoctorWHO",
        "wallet":  "0x875242eb5c91270ca80ed7753a87d6e22e4f5acf",
        "slug":    "doctorwho",
        "active":  False,
    },
    {
        "id":      "019ebb92-b4be-7660-82d3-4b1647843e6a",
        "name":    "MATRIX",
        "wallet":  "0x07924dea2c8212969d5dc5655785aa5063adb2bc",
        "slug":    "matrix",
        "active":  False,
    },
]

# ── Paths ───────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).parent.parent
SERVER_SCRIPT = PROJECT_ROOT / "agent" / "server.py"
PYTHON        = PROJECT_ROOT / ".venv312" / "bin" / "python3.12"
ACP_BASE_CFG  = Path.home() / ".config" / "acp" / "config.json"
LOG_DIR       = Path.home() / "Library" / "Logs" / "iCLONE"
TMP           = Path("/tmp")

LOG_DIR.mkdir(parents=True, exist_ok=True)


# ── Config isolation ────────────────────────────────────────────────────────

def _make_agent_config(agent: dict) -> Path:
    """
    Create an isolated acp-cli config dir for this agent.
    Sets activeWallet to the agent's wallet address.
    Returns the directory path (to be used as XDG_CONFIG_HOME/acp).
    """
    base_cfg = json.loads(ACP_BASE_CFG.read_text())

    # Patch: set this agent as active
    base_cfg["activeWallet"] = agent["wallet"]

    config_dir = TMP / f"iclone-acp-{agent['slug']}" / "acp"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "config.json").write_text(json.dumps(base_cfg, indent=2))

    return config_dir.parent  # XDG_CONFIG_HOME value


# ── Process management ──────────────────────────────────────────────────────

def _pid_file(slug: str) -> Path:
    return TMP / f"iclone-{slug}.pid"


def _events_file(slug: str) -> Path:
    return TMP / f"iclone-events-{slug}.jsonl"


def _is_running(slug: str) -> tuple[bool, int]:
    pid_file = _pid_file(slug)
    if not pid_file.exists():
        return False, 0
    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, 0)  # signal 0 = existence check
        return True, pid
    except (ValueError, ProcessLookupError, PermissionError):
        pid_file.unlink(missing_ok=True)
        return False, 0


def start_agent(agent: dict) -> int | None:
    """Start a server process for one agent. Returns PID or None on failure."""
    slug = agent["slug"]
    running, pid = _is_running(slug)
    if running:
        print(f"  [{agent['name']}] already running (PID {pid})")
        return pid

    xdg_home = _make_agent_config(agent)
    events_file = _events_file(slug)
    events_file.unlink(missing_ok=True)

    log_path = LOG_DIR / f"{slug}.log"
    log_fh = log_path.open("a")

    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = str(xdg_home)
    env["ICLONE_AGENT_ID"]   = agent["id"]
    env["ICLONE_AGENT_NAME"] = agent["name"]
    env["ICLONE_EVENTS_FILE"] = str(events_file)

    proc = subprocess.Popen(
        [str(PYTHON), str(SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=log_fh,
        stderr=log_fh,
        start_new_session=True,
    )

    _pid_file(slug).write_text(str(proc.pid))
    time.sleep(1)

    still_up = proc.poll() is None
    if still_up:
        print(f"  [{agent['name']}] started — PID {proc.pid} | log: {log_path}")
        return proc.pid
    else:
        print(f"  [{agent['name']}] FAILED to start — check log: {log_path}")
        _pid_file(slug).unlink(missing_ok=True)
        return None


def stop_agent(agent: dict) -> None:
    slug = agent["slug"]
    running, pid = _is_running(slug)
    if not running:
        print(f"  [{agent['name']}] not running")
        return
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    _pid_file(slug).unlink(missing_ok=True)
    print(f"  [{agent['name']}] stopped (was PID {pid})")


def status() -> None:
    print("\niCLONE Multi-Agent Status")
    print("─" * 50)
    all_running = True
    for agent in AGENTS:
        running, pid = _is_running(agent["slug"])
        status_str = f"RUNNING  (PID {pid})" if running else "STOPPED"
        if not running:
            all_running = False
        log_path = LOG_DIR / f"{agent['slug']}.log"
        last_line = ""
        if log_path.exists():
            lines = log_path.read_text().splitlines()
            last_line = lines[-1][:80] if lines else ""
        print(f"  {agent['name']:<14} [{status_str:<22}]  {agent['wallet'][:12]}...")
        if last_line:
            print(f"  {'':14}   {last_line}")
    print()
    print("All running:" if all_running else "Some agents stopped — run bootstrap_all_agents.py to restart")
    print()


def start_all() -> None:
    print("\niCLONE — Starting active agents")
    print("─" * 50)
    for agent in AGENTS:
        if not agent.get("active", True):
            print(f"  [{agent['name']}] skipped (inactive)")
            continue
        print(f"\n→ Switching to {agent['name']}...")
        subprocess.run(
            ["/opt/homebrew/bin/acp", "agent", "use", "--agent-id", agent["id"]],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )
        time.sleep(0.5)
        start_agent(agent)

    # Restore CLONE as default active
    subprocess.run(
        ["/opt/homebrew/bin/acp", "agent", "use", "--agent-id", AGENTS[0]["id"]],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT)
    )
    print(f"\nCLONE restored as default active agent")
    print()
    time.sleep(2)
    status()


def stop_all() -> None:
    print("\niCLONE — Stopping all agents")
    print("─" * 50)
    for agent in AGENTS:
        stop_agent(agent)
    print()


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iCLONE Multi-Agent Bootstrap")
    parser.add_argument("--status", action="store_true", help="Show status of all agents")
    parser.add_argument("--stop",   action="store_true", help="Stop all agent servers")
    args = parser.parse_args()

    if args.status:
        status()
    elif args.stop:
        stop_all()
    else:
        start_all()
