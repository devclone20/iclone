"""
iCLONE — Daily Performance Report

Pulls stats from Supabase and prints a structured report.
Used by the launchd cron (daily at 08:00) and can be run manually.

Run:
  ~/Desktop/AI/iclone/venv312/bin/python3.12 ops/daily_report.py
"""

import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path.home() / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env", override=False)

sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

logging.basicConfig(level=logging.WARNING)


def _client():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def fetch_stats(days: int = 1) -> dict:
    db = _client()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    # Jobs in window
    jobs = (
        db.table("acp_jobs")
        .select("offering_id, status, price_usdc, delivered_at, usdc_earned")
        .gte("delivered_at", since)
        .execute()
        .data
    ) or []

    # All-time totals
    all_jobs = db.table("acp_jobs").select("status, price_usdc, usdc_earned").execute().data or []

    total_jobs = len(jobs)
    completed = [j for j in jobs if j["status"] in ("delivered", "completed")]
    failed = [j for j in jobs if j["status"] in ("disputed", "failed")]

    revenue_window = sum(float(j.get("usdc_earned") or j.get("price_usdc") or 0) for j in completed)
    success_rate = (len(completed) / total_jobs * 100) if total_jobs > 0 else 0

    # Top offerings in window
    from collections import Counter
    offering_counts = Counter(j["offering_id"] for j in completed)
    top_offerings = offering_counts.most_common(5)

    # All-time
    all_completed = [j for j in all_jobs if j["status"] in ("delivered", "completed")]
    all_revenue = sum(float(j.get("usdc_earned") or j.get("price_usdc") or 0) for j in all_completed)

    return {
        "window_days": days,
        "window_jobs": total_jobs,
        "window_completed": len(completed),
        "window_failed": len(failed),
        "window_revenue_usdc": revenue_window,
        "window_success_rate": success_rate,
        "top_offerings": top_offerings,
        "alltime_completed": len(all_completed),
        "alltime_revenue_usdc": all_revenue,
    }


def _target_jobs_per_day(scenario: str) -> tuple[int, float]:
    # jobs/day, avg_price_usdc
    scenarios = {
        "conservative": (10, 0.25),    # $75/month — starting out
        "growth": (50, 0.25),          # $375/month — gaining traction
        "aixbt": (118, 1.00),          # $3,540/month — strong niche
        "nox_pattern": (1000, 0.25),   # $7,500/month — volume utility
        "ethy": (3145, 0.10),          # $9,435/month USDC + VIRTUAL rewards
    }
    return scenarios.get(scenario, (50, 0.25))


def print_report(stats: dict, scenario: str = "growth"):
    target_jobs, target_price = _target_jobs_per_day(scenario)
    target_revenue = target_jobs * target_price

    days = stats["window_days"]
    actual_jobs = stats["window_jobs"]
    actual_revenue = stats["window_revenue_usdc"]
    success_rate = stats["window_success_rate"]

    jobs_per_day = actual_jobs / days if days > 0 else 0
    revenue_per_day = actual_revenue / days if days > 0 else 0

    pct_jobs = (jobs_per_day / target_jobs * 100) if target_jobs > 0 else 0
    pct_revenue = (revenue_per_day / target_revenue * 100) if target_revenue > 0 else 0

    bar_jobs = "█" * int(pct_jobs / 5) + "░" * (20 - int(pct_jobs / 5))
    bar_rev = "█" * int(pct_revenue / 5) + "░" * (20 - int(pct_revenue / 5))

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print(f"║  iCLONE Daily Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}          ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print(f"  Window     : last {days} day(s)")
    print(f"  Scenario   : {scenario} ({target_jobs} jobs/day @ ${target_price:.2f})")
    print()
    print("  ── Jobs ────────────────────────────────────")
    print(f"  Today      : {actual_jobs} jobs  ({jobs_per_day:.1f}/day)")
    print(f"  Target     : {target_jobs * days} jobs  ({target_jobs}/day)")
    print(f"  Progress   : {bar_jobs} {pct_jobs:.0f}%")
    print(f"  Success    : {stats['window_completed']} ok / {stats['window_failed']} failed  ({success_rate:.0f}%)")
    print()
    print("  ── Revenue ─────────────────────────────────")
    print(f"  Today      : ${actual_revenue:.4f} USDC")
    print(f"  Target     : ${target_revenue * days:.4f} USDC")
    print(f"  Progress   : {bar_rev} {pct_revenue:.0f}%")
    print()

    if stats["top_offerings"]:
        print("  ── Top Offerings ───────────────────────────")
        for name, count in stats["top_offerings"]:
            print(f"  {count:4d} × {name}")
        print()

    print("  ── All-Time ────────────────────────────────")
    print(f"  Jobs       : {stats['alltime_completed']}")
    print(f"  Revenue    : ${stats['alltime_revenue_usdc']:.4f} USDC")
    print()

    # Advisory
    if success_rate < 90 and actual_jobs > 0:
        print("  ⚠️  SUCCESS RATE BELOW 90% — investigate failed jobs in Supabase")
    if pct_jobs < 10 and actual_jobs == 0:
        print("  ℹ️  No jobs today — server may be offline or wallet not deployed")
    elif pct_jobs < 25:
        print("  📈 Low volume — ensure server is 24/7 and offerings are visible on Virtuals")
    elif pct_jobs >= 80:
        print("  ✅ On track for target scenario")

    print("═" * 56)
    print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--scenario", default="growth",
                        choices=["conservative", "growth", "aixbt", "nox_pattern", "ethy"])
    args = parser.parse_args()

    try:
        stats = fetch_stats(args.days)
        print_report(stats, args.scenario)
    except Exception as e:
        print(f"Report failed: {e}")
        sys.exit(1)
