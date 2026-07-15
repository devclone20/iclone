#!/usr/bin/env python3
"""Keep ACP session tokens alive for iCLONE and VEGETA.
Calls 'acp agent whoami' every 4 hours on both configs.
"""
import subprocess, time, logging, os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [token-refresh] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

CONFIGS = {
    "iCLONE": "/home/iclone/.config/acp-iclone/acp",
    "VEGETA": "/home/iclone/.config/acp-vegeta/acp",
}
ACP_BIN = next((p for p in ["/usr/bin/acp", "/usr/local/bin/acp"] if Path(p).exists()), "acp")
INTERVAL = 4 * 3600  # 4 horas


def ping(name, config_dir):
    env = {**os.environ, "ACP_CONFIG_DIR": config_dir}
    r = subprocess.run(
        [ACP_BIN, "agent", "whoami"],
        capture_output=True, text=True, env=env, timeout=30,
    )
    if r.returncode == 0:
        log.info("%s token OK: %s", name, r.stdout.strip().split("\t")[0])
    else:
        log.warning("%s token FAIL: %s", name, r.stderr.strip()[:200])


def main():
    log.info("Token refresh started — interval=%dh", INTERVAL // 3600)
    while True:
        for name, cfg in CONFIGS.items():
            try:
                ping(name, cfg)
            except Exception as e:
                log.error("%s ping error: %s", name, e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
