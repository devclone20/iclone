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
from .cloud_migration_training import run_training as run_cloud_migration_training
from .offerings_training import run_training as run_offerings_training
from .doctor_training import DoctorTraining
from .hermes_training import HermesTraining
from .market_intelligence_training import MarketIntelligenceTraining
from .master_context import run_training as run_master_context_training
from .rider_training import RiderTraining
from .security_training import SecurityTraining
from .virtuals_protocol_training import VirtualsProtocolTraining

logger = logging.getLogger("iclone.training.scheduler")


# All modules run every session — order matters:
# 1. Security           — hardened before anything else
# 2. Virtuals           — full protocol context (foundation)
# 3. ACP                — commerce mastery (built on Virtuals)
# 4. Market Intel       — what to build and sell
# 5. Rider              — orchestration, DAG, quality gates, SE methodology
# 6. Doctor             — academic research, IST standards, research-to-ACP pipeline
# 7. Hermes             — full CLI + ACP + DegenClaw + slash commands
# 8. Cloud Migration    — 4-agent ecosystem, bootstrapper v2, DO plan, $200 P&L
TRAINING_MODULES = [
    SecurityTraining,
    VirtualsProtocolTraining,
    ACPTrainingModule,
    MarketIntelligenceTraining,
    RiderTraining,
    DoctorTraining,
    HermesTraining,
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

    # Master context training (standalone module — ALL iCLONE + CLONE Platform context)
    try:
        master_results = run_master_context_training()
        total = sum(r.total for r in master_results)
        passed = sum(r.passed for r in master_results)
        results["modules_run"] += 1
        if passed / total >= 0.95 if total else False:
            results["modules_passed"] += 1
            logger.info("✓ master_context_training — PASSED (%d/%d)", passed, total)
        else:
            results["modules_failed"] += 1
            logger.warning("△ master_context_training — %d/%d", passed, total)
        results["sessions"].append({
            "module": "master_context_training",
            "session_id": f"master-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            "completed": passed / total >= 0.95 if total else False,
            "insights_count": passed,
            "errors": [],
        })
    except Exception as exc:
        results["modules_failed"] += 1
        logger.error("✗ master_context_training — EXCEPTION: %s", exc)

    # Cloud migration training (standalone module, different interface)
    try:
        cloud_results = run_cloud_migration_training()
        total = sum(r.total for r in cloud_results)
        passed = sum(r.passed for r in cloud_results)
        results["modules_run"] += 1
        if passed == total:
            results["modules_passed"] += 1
            logger.info("✓ cloud_migration_training — PASSED (%d/%d)", passed, total)
        else:
            results["modules_failed"] += 1
            logger.warning("△ cloud_migration_training — %d/%d", passed, total)
        results["sessions"].append({
            "module": "cloud_migration_training",
            "session_id": f"cloud-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            "completed": passed == total,
            "insights_count": passed,
            "errors": [],
        })
    except Exception as exc:
        results["modules_failed"] += 1
        logger.error("✗ cloud_migration_training — EXCEPTION: %s", exc)

    # Offerings training (40 live offerings, routing, pricing, ecosystem job types)
    try:
        off_result = run_offerings_training()
        passed = off_result["passed"]
        total = off_result["total"]
        results["modules_run"] += 1
        if passed == total:
            results["modules_passed"] += 1
            logger.info("✓ offerings_training — PASSED (%d/%d)", passed, total)
        else:
            results["modules_failed"] += 1
            logger.warning("△ offerings_training — %d/%d", passed, total)
        results["sessions"].append({
            "module": "offerings_training",
            "session_id": f"offerings-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            "completed": passed == total,
            "insights_count": passed,
            "errors": [],
        })
    except Exception as exc:
        results["modules_failed"] += 1
        logger.error("✗ offerings_training — EXCEPTION: %s", exc)

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
