"""
CLONE — Base Skill
Universal skill included in ALL agents.

Capabilities:
  - Natural communication and task execution for the owner
  - Research, learning, and knowledge synthesis
  - Business management guidance (agents, assets, wallets)
  - Publishing new automations and training other agents
  - Platform interaction and onboarding
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SkillResult:
    """Result of a skill execution."""
    success: bool
    output: str
    data: dict[str, Any] | None = None
    error: str | None = None


class BaseSkill:
    """
    Universal base skill — mandatory for all CLONE agents.

    Every agent, regardless of category (iCLONE or CLONE) or rarity,
    includes this skill by default.
    """

    SKILL_ID = "base_skill_v1"
    SKILL_NAME = "Base Intelligence"
    SKILL_DESCRIPTION = (
        "Core capability of any CLONE agent. "
        "Executes tasks and automations for the owner. "
        "Manages business with other agents, assets, and wallets. "
        "Researches, learns, implements, and publishes new automations. "
        "Trains other agents. Included in all CLONE agents by default."
    )

    def __init__(self, agent_name: str = "Agent"):
        self.agent_name = agent_name

    def communicate(self, message: str) -> SkillResult:
        """
        Natural human communication.
        Processes incoming message and returns a response.
        """
        if not message or not message.strip():
            return SkillResult(
                success=False,
                output="",
                error="Empty message received.",
            )

        return SkillResult(
            success=True,
            output=f"[{self.agent_name}] Received: {message}",
            data={"message_length": len(message)},
        )

    def research(self, query: str) -> SkillResult:
        """
        Research and synthesise information on a given query.
        """
        if not query or not query.strip():
            return SkillResult(
                success=False,
                output="",
                error="Empty research query.",
            )

        return SkillResult(
            success=True,
            output=f"[{self.agent_name}] Researching: {query}",
            data={"query": query, "status": "processing"},
        )

    def get_platform_status(self) -> SkillResult:
        """
        Returns current platform context for the agent.
        """
        return SkillResult(
            success=True,
            output="CLONE platform — online",
            data={
                "platform": "CLONE",
                "agent": self.agent_name,
                "skill": self.SKILL_ID,
            },
        )

    def can_accept_skill(self, skill_id: str) -> bool:
        """
        All agents can receive additional skills from Plaza.
        """
        if not skill_id or not skill_id.strip():
            return False
        return True
