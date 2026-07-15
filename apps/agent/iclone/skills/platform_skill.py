"""
CLONE — Platform Skill (iCLONE)
Governs the CLONE platform: agent onboarding, skill deployment, user assistance.
"""

from .base_skill import SkillResult


class PlatformSkill:
    """
    CLONE platform governance skill.
    iCLONE uses this to assist users, manage agent onboarding,
    and oversee skill deployments on the CLONE platform.
    """

    SKILL_ID = "platform_skill_v1"
    SKILL_NAME = "Platform Governance"
    SKILL_DESCRIPTION = (
        "CLONE platform management: user onboarding, agent assistance, "
        "skill deployment guidance, and platform Q&A."
    )

    AGENT_CATEGORIES = ("iCLONE", "CLONE")
    RARITY_TIERS = ("iCLONE", "Super Raro", "Raro", "Comum")

    def onboard_user(self, user_id: str) -> SkillResult:
        """Guide a new user through the CLONE platform."""
        if not user_id or not user_id.strip():
            return SkillResult(
                success=False,
                output="",
                error="User ID required for onboarding.",
            )

        return SkillResult(
            success=True,
            output=(
                f"Welcome to CLONE. I'm iCLONE, your platform assistant. "
                f"I'll guide you through acquiring your agent, setting up skills, "
                f"and using the HUB."
            ),
            data={
                "user_id": user_id,
                "platform": "CLONE",
                "next_step": "browse_agents",
            },
        )

    def explain_agent(self, category: str) -> SkillResult:
        """Explain an agent category to a user."""
        category = category.upper().strip()

        explanations = {
            "ICLONE": (
                "iCLONE is the personal clone category. "
                "Configured with the owner's personality and communication style. "
                "Authenticated by fingerprint. Maximum personalisation."
            ),
            "CLONE": (
                "CLONE is the global agent category. "
                "Configured entirely through purchased skills. "
                "No personal fingerprint — fully skill-driven."
            ),
        }

        if category not in explanations:
            return SkillResult(
                success=False,
                output="",
                error=f"Unknown category '{category}'. Valid: {self.AGENT_CATEGORIES}",
            )

        return SkillResult(
            success=True,
            output=explanations[category],
            data={"category": category},
        )

    def guide_skill_deployment(self, skill_id: str, agent_id: str) -> SkillResult:
        """Guide skill deployment from Plaza to an agent via HUB > FRAMEWORK."""
        if not skill_id or not agent_id:
            return SkillResult(
                success=False,
                output="",
                error="Both skill_id and agent_id are required.",
            )

        return SkillResult(
            success=True,
            output=(
                f"Deploying skill '{skill_id}' to agent '{agent_id}'. "
                f"Navigate to HUB > FRAMEWORK > SKILLS > Deploy."
            ),
            data={
                "skill_id": skill_id,
                "agent_id": agent_id,
                "route": "HUB > FRAMEWORK > SKILLS",
                "status": "deployment_queued",
            },
        )
