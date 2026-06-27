"""
iCLONE — Supabase persistence layer.

Writes agent events to Supabase in fire-and-forget mode:
failures are logged but never crash the agent.

Tables used:
  - acp_jobs          : every job received, accepted, delivered, completed
  - onboarding_forms  : leads qualified by the agent
  - latest_state      : agent runtime state (single-row upsert)
  - self_attendance   : cron self-evaluation scores
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("iclone.db")

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client

    try:
        from supabase import create_client, Client  # type: ignore

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            logger.warning("Supabase env vars not set — persistence disabled.")
            return None

        _client = create_client(url, key)
        logger.info("Supabase client initialised.")
        return _client
    except Exception as exc:
        logger.warning("Supabase unavailable: %s", exc)
        return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# ACP JOBS
# ─────────────────────────────────────────────────────────────────────────────

def upsert_acp_job(
    job_id: str,
    offering_id: str,
    client_agent_id: str,
    status: str,
    price_usdc: float,
    requirements: dict | None = None,
    deliverable: str | None = None,
    deliverable_url: str | None = None,
    delivered_at: str | None = None,
    error_message: str | None = None,
) -> None:
    """Insert or update a job record in acp_jobs."""
    db = _get_client()
    if db is None:
        return

    try:
        payload: dict = {
            "job_id": job_id,
            "offering_id": offering_id,
            "client_agent_id": client_agent_id,
            "status": status,
            "price_usdc": price_usdc,
            "requirements_json": requirements or {},
        }
        if deliverable is not None:
            payload["deliverable_url"] = deliverable_url or ""
        if delivered_at is not None:
            payload["delivered_at"] = delivered_at
        if status == "completed":
            payload["completed_at"] = _now()
            payload["usdc_earned"] = price_usdc

        db.table("acp_jobs").upsert(payload, on_conflict="job_id").execute()
    except Exception as exc:
        logger.error("upsert_acp_job failed: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# ONBOARDING FORMS
# ─────────────────────────────────────────────────────────────────────────────

def insert_lead(
    filled_by: str,  # 'human' | 'ai' | 'hybrid'
    source: str,
    project_id: str | None = None,
    name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    company: str | None = None,
    role: str | None = None,
    use_case: str | None = None,
    budget_range: str | None = None,
    timeline: str | None = None,
    notes: str | None = None,
    ai_score: int | None = None,
    ai_tags: list[str] | None = None,
    ai_summary: str | None = None,
    ai_next_action: str | None = None,
    assigned_to: str = "iclone",
) -> str | None:
    """Insert a new lead into onboarding_forms. Returns row id."""
    db = _get_client()
    if db is None:
        return None

    try:
        result = (
            db.table("onboarding_forms")
            .insert(
                {
                    "filled_by": filled_by,
                    "source": source,
                    "project_id": project_id,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "company": company,
                    "role": role,
                    "use_case": use_case,
                    "budget_range": budget_range,
                    "timeline": timeline,
                    "notes": notes,
                    "ai_score": ai_score,
                    "ai_tags": ai_tags or [],
                    "ai_summary": ai_summary,
                    "ai_next_action": ai_next_action,
                    "assigned_to": assigned_to,
                    "status": "new",
                }
            )
            .execute()
        )
        rows = result.data
        if rows:
            return rows[0].get("id")
    except Exception as exc:
        logger.error("insert_lead failed: %s", exc)

    return None


# ─────────────────────────────────────────────────────────────────────────────
# LATEST STATE
# ─────────────────────────────────────────────────────────────────────────────

def upsert_state(payload: dict[str, Any]) -> None:
    """Upsert agent runtime state (single row, id=1)."""
    db = _get_client()
    if db is None:
        return

    try:
        db.table("latest_state").upsert(
            {"id": 1, "updated_at": _now(), **payload},
            on_conflict="id",
        ).execute()
    except Exception as exc:
        logger.error("upsert_state failed: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# SELF ATTENDANCE
# ─────────────────────────────────────────────────────────────────────────────

def insert_attendance(
    session_id: str,
    execution_score: int,
    research_score: int,
    trading_score: int,
    communication_score: int,
    learning_score: int,
    overall_score: int,
    notes: str | None = None,
    jobs_completed: int = 0,
    jobs_failed: int = 0,
    revenue_usdc: float = 0.0,
) -> None:
    """Record a self-attendance evaluation."""
    db = _get_client()
    if db is None:
        return

    try:
        db.table("self_attendance").insert(
            {
                "session_id": session_id,
                "execution_score": execution_score,
                "research_score": research_score,
                "trading_score": trading_score,
                "communication_score": communication_score,
                "learning_score": learning_score,
                "overall_score": overall_score,
                "notes": notes,
                "jobs_completed": jobs_completed,
                "jobs_failed": jobs_failed,
                "revenue_usdc": revenue_usdc,
            }
        ).execute()
    except Exception as exc:
        logger.error("insert_attendance failed: %s", exc)
