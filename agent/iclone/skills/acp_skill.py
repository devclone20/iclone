"""
CLONE — ACP Skill (iCLONE)
Virtuals Protocol Agent Commerce Protocol integration.

iCLONE acts as a PROVIDER on ACP:
  - Publishes job offerings
  - Accepts jobs from client agents
  - Executes tasks and delivers DeliverableMemo
  - Coordinates with other agents
  - Gets paid in USDC via on-chain escrow (ERC-8183)

Standard: ERC-8183 — Virtuals Protocol + Ethereum Foundation
Docs: https://whitepaper.virtuals.io/about-virtuals/agent-commerce-protocol-acp
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from datetime import datetime, timezone

from .base_skill import SkillResult


class JobStatus(str, Enum):
    PENDING   = "pending"
    ACCEPTED  = "accepted"
    EXECUTING = "executing"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    DISPUTED  = "disputed"
    CANCELLED = "cancelled"


class OfferingCategory(str, Enum):
    AGENT_TRAINING     = "agent_training"
    SKILL_BUILDING     = "skill_building"
    CRYPTO_RESEARCH    = "crypto_research"
    AGENT_COORDINATION = "agent_coordination"
    PLATFORM_ONBOARDING = "platform_onboarding"


@dataclass
class JobOffering:
    """
    A service listing published by iCLONE on ACP.
    Describes what iCLONE can be hired to do.
    """
    offering_id: str
    name: str
    description: str
    category: OfferingCategory
    price_usdc: float                    # Price in USDC
    sla_hours: int                       # Service Level Agreement — max hours to deliver
    requirements: list[str]              # What the client must provide
    deliverable_description: str         # What will be delivered
    active: bool = True


@dataclass
class Job:
    """
    An active job instance — created when a client buys an offering.
    Backed by an on-chain escrow contract (ERC-8183).
    """
    job_id: str
    offering_id: str
    client_agent_id: str
    status: JobStatus
    price_usdc: float
    requirements_received: dict[str, Any] = field(default_factory=dict)
    deliverable: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    delivered_at: str | None = None


@dataclass
class DeliverableMemo:
    """
    Proof of work delivery — signed on-chain by provider.
    Client/Evaluator signs to release USDC from escrow.
    """
    job_id: str
    provider_id: str
    deliverable_hash: str          # Hash of the delivered content
    deliverable_url: str           # Where to access the deliverable
    summary: str                   # Human-readable summary
    delivered_at: str


class ACPSkill:
    """
    ACP Provider skill for iCLONE.

    Capabilities:
    - Publish and manage job offerings on Virtuals Protocol ACP
    - Accept and execute jobs from client agents
    - Coordinate with other agents to fulfil complex tasks
    - Submit DeliverableMemo and collect USDC payment
    - Build reputation through on-chain job history (ERC-8004)
    """

    SKILL_ID = "acp_skill_v1"
    SKILL_NAME = "ACP Provider — Agentic Commerce"
    SKILL_DESCRIPTION = (
        "Virtuals Protocol ACP provider. iCLONE publishes job offerings, "
        "accepts on-chain jobs, executes tasks (agent training, skill building, "
        "crypto research, agent coordination), and collects USDC payment via escrow. "
        "Standard: ERC-8183."
    )

    PROVIDER_ID = "iclone-ai"

    # Default catalogue of offerings iCLONE publishes on ACP
    DEFAULT_OFFERINGS: list[JobOffering] = [
        JobOffering(
            offering_id="iclone-train-agent-v1",
            name="Agent Training & Deployment",
            description=(
                "Full training and deployment of a CLONE platform agent. "
                "Includes skill configuration, personality setup, ACP registration, "
                "and deployment to Virtuals Protocol."
            ),
            category=OfferingCategory.AGENT_TRAINING,
            price_usdc=50.0,
            sla_hours=24,
            requirements=[
                "agent_name",
                "agent_category",          # iCLONE or CLONE
                "desired_skills",          # list of skill IDs
                "wallet_address",
            ],
            deliverable_description=(
                "Deployed agent with all skills active, ACP-registered, "
                "and ready for the CLONE platform. Includes config file and "
                "deployment report."
            ),
        ),
        JobOffering(
            offering_id="iclone-build-skill-v1",
            name="Custom Skill Building",
            description=(
                "Design and build a custom skill for any CLONE agent. "
                "Skill will be tested, documented, and ready for Plaza deployment."
            ),
            category=OfferingCategory.SKILL_BUILDING,
            price_usdc=30.0,
            sla_hours=12,
            requirements=[
                "skill_description",
                "target_agent_category",
                "input_output_examples",
            ],
            deliverable_description=(
                "Production-ready skill module with tests, documentation, "
                "and Plaza listing draft."
            ),
        ),
        JobOffering(
            offering_id="iclone-crypto-research-v1",
            name="Crypto Research Report",
            description=(
                "In-depth research report on any crypto asset, DeFi protocol, "
                "or AI agent token. Market analysis, on-chain data, risk assessment."
            ),
            category=OfferingCategory.CRYPTO_RESEARCH,
            price_usdc=5.0,
            sla_hours=2,
            requirements=["target_asset_or_protocol"],
            deliverable_description=(
                "Structured research report: overview, metrics, risk, opportunity, "
                "recommendation."
            ),
        ),
        JobOffering(
            offering_id="iclone-coordinate-agents-v1",
            name="Multi-Agent Coordination",
            description=(
                "iCLONE coordinates multiple agents to complete a complex task "
                "that requires parallel execution or specialised sub-agents."
            ),
            category=OfferingCategory.AGENT_COORDINATION,
            price_usdc=20.0,
            sla_hours=6,
            requirements=[
                "task_description",
                "available_agents",        # list of agent IDs to coordinate
                "expected_output",
            ],
            deliverable_description=(
                "Task completion report with outputs from all coordinated agents, "
                "execution log, and final result."
            ),
        ),
        JobOffering(
            offering_id="iclone-onboarding-v1",
            name="CLONE Platform Onboarding",
            description=(
                "Full onboarding of a new agent or user to the CLONE platform. "
                "Includes ACP registration, HUB setup, skill recommendations."
            ),
            category=OfferingCategory.PLATFORM_ONBOARDING,
            price_usdc=2.0,
            sla_hours=1,
            requirements=["agent_id_or_user_id"],
            deliverable_description=(
                "Onboarding completion report with platform access confirmed "
                "and initial skill recommendations."
            ),
        ),
    ]

    def __init__(self):
        self._offerings: dict[str, JobOffering] = {
            o.offering_id: o for o in self.DEFAULT_OFFERINGS
        }
        self._active_jobs: dict[str, Job] = {}
        self._completed_jobs: list[Job] = []

    # -------------------------------------------------------------------------
    # Offerings management
    # -------------------------------------------------------------------------

    def list_offerings(self, active_only: bool = True) -> list[JobOffering]:
        """Return all published offerings."""
        offerings = list(self._offerings.values())
        if active_only:
            return [o for o in offerings if o.active]
        return offerings

    def get_offering(self, offering_id: str) -> SkillResult:
        """Get details of a specific offering."""
        offering = self._offerings.get(offering_id)
        if not offering:
            return SkillResult(
                success=False,
                output="",
                error=f"Offering '{offering_id}' not found.",
            )
        return SkillResult(
            success=True,
            output=f"Offering: {offering.name} — ${offering.price_usdc} USDC",
            data={
                "offering_id": offering.offering_id,
                "name": offering.name,
                "description": offering.description,
                "price_usdc": offering.price_usdc,
                "sla_hours": offering.sla_hours,
                "requirements": offering.requirements,
                "deliverable": offering.deliverable_description,
                "active": offering.active,
            },
        )

    # -------------------------------------------------------------------------
    # Job lifecycle
    # -------------------------------------------------------------------------

    def accept_job(
        self,
        job_id: str,
        offering_id: str,
        client_agent_id: str,
        requirements: dict[str, Any],
    ) -> SkillResult:
        """
        Accept an incoming job from a client agent.
        Validates requirements against the offering spec.
        """
        if not job_id or not offering_id or not client_agent_id:
            return SkillResult(
                success=False,
                output="",
                error="job_id, offering_id, and client_agent_id are required.",
            )

        offering = self._offerings.get(offering_id)
        if not offering:
            return SkillResult(
                success=False,
                output="",
                error=f"Offering '{offering_id}' not found.",
            )

        if not offering.active:
            return SkillResult(
                success=False,
                output="",
                error=f"Offering '{offering_id}' is not active.",
            )

        # Validate required fields
        missing = [r for r in offering.requirements if r not in requirements]
        if missing:
            return SkillResult(
                success=False,
                output="",
                error=f"Missing required fields: {missing}",
            )

        job = Job(
            job_id=job_id,
            offering_id=offering_id,
            client_agent_id=client_agent_id,
            status=JobStatus.ACCEPTED,
            price_usdc=offering.price_usdc,
            requirements_received=requirements,
        )
        self._active_jobs[job_id] = job

        return SkillResult(
            success=True,
            output=f"Job '{job_id}' accepted from agent '{client_agent_id}'.",
            data={
                "job_id": job_id,
                "status": job.status,
                "price_usdc": job.price_usdc,
                "sla_hours": offering.sla_hours,
            },
        )

    def submit_deliverable(
        self,
        job_id: str,
        deliverable_content: str,
        deliverable_url: str,
    ) -> SkillResult:
        """
        Submit work deliverable for a job.
        Creates DeliverableMemo — client signs to release escrow.
        """
        job = self._active_jobs.get(job_id)
        if not job:
            return SkillResult(
                success=False,
                output="",
                error=f"Active job '{job_id}' not found.",
            )

        if not deliverable_content or not deliverable_url:
            return SkillResult(
                success=False,
                output="",
                error="deliverable_content and deliverable_url are required.",
            )

        delivered_at = datetime.now(timezone.utc).isoformat()

        memo = DeliverableMemo(
            job_id=job_id,
            provider_id=self.PROVIDER_ID,
            deliverable_hash=str(hash(deliverable_content)),
            deliverable_url=deliverable_url,
            summary=deliverable_content[:200],
            delivered_at=delivered_at,
        )

        job.status = JobStatus.DELIVERED
        job.deliverable = deliverable_content
        job.delivered_at = delivered_at

        return SkillResult(
            success=True,
            output=f"Deliverable submitted for job '{job_id}'. Awaiting client approval.",
            data={
                "job_id": job_id,
                "status": job.status,
                "deliverable_url": deliverable_url,
                "delivered_at": delivered_at,
                "memo_hash": memo.deliverable_hash,
                "next_step": "client_or_evaluator_must_sign_to_release_escrow",
            },
        )

    def complete_job(self, job_id: str) -> SkillResult:
        """
        Mark job as completed after client approval.
        USDC released from escrow on-chain.
        """
        job = self._active_jobs.get(job_id)
        if not job:
            return SkillResult(
                success=False,
                output="",
                error=f"Active job '{job_id}' not found.",
            )

        if job.status != JobStatus.DELIVERED:
            return SkillResult(
                success=False,
                output="",
                error=f"Job must be in DELIVERED status. Current: {job.status}",
            )

        job.status = JobStatus.COMPLETED
        self._completed_jobs.append(job)
        del self._active_jobs[job_id]

        return SkillResult(
            success=True,
            output=f"Job '{job_id}' completed. ${job.price_usdc} USDC released.",
            data={
                "job_id": job_id,
                "status": JobStatus.COMPLETED,
                "usdc_earned": job.price_usdc,
                "total_completed": len(self._completed_jobs),
            },
        )

    # -------------------------------------------------------------------------
    # Stats & reputation
    # -------------------------------------------------------------------------

    def get_provider_stats(self) -> SkillResult:
        """Return iCLONE ACP provider statistics."""
        total_earned = sum(j.price_usdc for j in self._completed_jobs)

        return SkillResult(
            success=True,
            output=f"iCLONE ACP Stats — {len(self._completed_jobs)} jobs completed",
            data={
                "provider_id": self.PROVIDER_ID,
                "active_offerings": len(self.list_offerings()),
                "active_jobs": len(self._active_jobs),
                "completed_jobs": len(self._completed_jobs),
                "total_usdc_earned": total_earned,
                "reputation_standard": "ERC-8004",
            },
        )
