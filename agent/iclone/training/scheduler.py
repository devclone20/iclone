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
from .doctor_training import DoctorTraining
from .market_intelligence_training import MarketIntelligenceTraining
from .rider_training import RiderTraining
from .security_training import SecurityTraining
from .virtuals_protocol_training import VirtualsProtocolTraining

logger = logging.getLogger("iclone.training.scheduler")


# All modules run every session — order matters:
# 1. Security     — hardened before anything else
# 2. Virtuals     — full protocol context (foundation)
# 3. ACP          — commerce mastery (built on Virtuals)
# 4. Market Intel — what to build and sell
# 5. Rider        — orchestration, DAG, quality gates, SE methodology
# 6. Doctor       — academic research, IST standards, research-to-ACP pipeline
TRAINING_MODULES = [
    SecurityTraining,
    VirtualsProtocolTraining,
    ACPTrainingModule,
    MarketIntelligenceTraining,
    RiderTraining,
    DoctorTraining,
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

            # Support both dataclass and dict session formats
            completed = session.completed if hasattr(session, "completed") else session.get("completed", False)
            insights = session.insights if hasattr(session, "insights") else session.get("insights", [])
            errors = session.errors if hasattr(session, "errors") else session.get("errors", [])
            session_id = session.session_id if hasattr(session, "session_id") else session.get("session_id", "")

            if completed:
                results["modules_passed"] += 1
                logger.info("✓ %s — PASSED (%d insights)", ModuleClass.MODULE_ID, len(insights))
            else:
                results["modules_failed"] += 1
                logger.warning("✗ %s — FAILED: %s", ModuleClass.MODULE_ID, errors)

            results["sessions"].append({
                "module": ModuleClass.MODULE_ID,
                "session_id": session_id,
                "completed": completed,
                "insights_count": len(insights),
                "errors": errors,
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
