"""
CLONE — iCLONE Training Scheduler
Runs all training modules 2x per day: 07:00 UTC + 19:00 UTC

Usage:
  python -m agent.iclone.training.scheduler

Cron (add to crontab):
  0 7  * * * cd /path/to/iclone && python -m agent.iclone.training.scheduler
  0 19 * * * cd /path/to/iclone && python -m agent.iclone.training.scheduler
"""

import logging
from datetime import datetime, timezone

from .acp_training import ACPTrainingModule

logger = logging.getLogger("iclone.training.scheduler")


TRAINING_MODULES = [
    ACPTrainingModule,
]


def run_all_training() -> dict:
    """
    Execute all registered training modules.
    Called 2x daily by scheduler.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    results = {
        "timestamp": timestamp,
        "modules_run": 0,
        "modules_passed": 0,
        "modules_failed": 0,
        "sessions": [],
    }

    logger.info("=== iCLONE Daily Training — %s ===", timestamp)

    for ModuleClass in TRAINING_MODULES:
        module = ModuleClass()
        try:
            session = module.run_session()
            results["modules_run"] += 1
            if session.completed:
                results["modules_passed"] += 1
                logger.info("✓ %s — PASSED", ModuleClass.MODULE_ID)
            else:
                results["modules_failed"] += 1
                logger.warning("✗ %s — FAILED: %s", ModuleClass.MODULE_ID, session.errors)

            results["sessions"].append({
                "module": ModuleClass.MODULE_ID,
                "session_id": session.session_id,
                "completed": session.completed,
                "insights_count": len(session.insights),
                "errors": session.errors,
            })
        except Exception as exc:
            results["modules_failed"] += 1
            logger.error("✗ %s — EXCEPTION: %s", ModuleClass.MODULE_ID, exc)

    logger.info(
        "=== Training complete — %d/%d passed ===",
        results["modules_passed"],
        results["modules_run"],
    )

    return results


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run_all_training()
