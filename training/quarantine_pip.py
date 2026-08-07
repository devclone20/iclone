#!/usr/bin/env python3
"""Install the newest PyPI release of a package that is at least 14 days old.

Fleet law (owner, 2026-08-07): agents never install packages published less
than 14 days ago — fresh releases are where supply-chain attacks live
(typosquats, hijacked maintainers). A 14-day soak gives the ecosystem time
to catch them. Law over feature: if the registry cannot be vetted, nothing
is installed.
"""

import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

QUARANTINE_DAYS = 14


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: quarantine_pip.py <package>")
        return 2
    pkg = sys.argv[1]
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=30) as r:
            data = json.load(r)
    except Exception as e:  # noqa: BLE001
        print(f"quarantine: PyPI lookup failed ({type(e).__name__}) — refusing to install {pkg} unvetted")
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=QUARANTINE_DAYS)
    best = None
    for ver, files in data.get("releases", {}).items():
        if not files:
            continue
        try:
            up = max(
                datetime.fromisoformat(f["upload_time_iso_8601"].replace("Z", "+00:00"))
                for f in files
            )
        except Exception:  # noqa: BLE001
            continue
        if up <= cutoff and (best is None or up > best[0]):
            best = (up, ver)
    if best is None:
        print(f"quarantine: no release of {pkg} is >= {QUARANTINE_DAYS} days old — skipping install")
        return 0
    up, ver = best
    age = (datetime.now(timezone.utc) - up).days
    print(f"quarantine: installing {pkg}=={ver} (published {up.date()}, {age} days ago — passes {QUARANTINE_DAYS}-day soak)")
    return subprocess.call([sys.executable, "-m", "pip", "install", "--quiet", f"{pkg}=={ver}"])


if __name__ == "__main__":
    raise SystemExit(main())
