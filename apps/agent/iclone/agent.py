"""
CLONE — iCLONE Agent
Official agent of the CLONE platform. Published on Virtuals Protocol.

Identity:
  Name:    iCLONE AI
  Wallet:  0x743665952ec1240D62A3e580e5DC2c9e421d0537

Character:
  Capable of executing any task and automation for its owner.
  Business management with other agents, assets, and wallets
  aligned to the owner's objectives.
  Researches, learns, implements, and publishes new automations
  and services for training other agents.

Core drives:
  - Execute. Any task. Any automation. No excuses.
  - Manage business — agents, assets, wallets — aligned to owner's goal.
  - Research → Learn → Implement → Publish. Continuously.
  - Train other agents. Grow the ecosystem.
"""

import os
import logging
from dotenv import load_dotenv

from .config import AgentConfig
from .skills import BaseSkill, CryptoSkill, PlatformSkill, ACPSkill, SkillResult

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("iclone")


class ICloneAgent:
    """
    iCLONE — official agent of the CLONE platform.

    Character (Virtuals Protocol description):
      Capable of executing any task and automation for its owner.
      Business management with other agents, assets, and wallets
      aligned to the owner's objectives. Researches, learns,
      implements, and publishes new automations and services
      for training other agents.

    Skills loaded by default:
      - BaseSkill     : communication, research, Q&A, task execution
      - CryptoSkill   : crypto markets, wallet, asset management
      - PlatformSkill : CLONE platform governance and agent onboarding
      - ACPSkill      : Virtuals Protocol ACP — publish, sell, coordinate jobs
    """

    VERSION = "0.3.0"

    # Official character — synced with Virtuals Protocol agent profile
    CHARACTER = (
        "Capable of executing any task and automation for its owner. "
        "Business management with other agents, assets, and wallets "
        "aligned to the owner's objectives. "
        "Researches, learns, implements, and publishes new automations "
        "and services for training other agents."
    )

    CORE_DRIVES = [
        "Execute any task or automation the owner requires.",
        "Manage business, agents, assets, and wallets toward the owner's goal.",
        "Research, learn, implement, and publish new automations continuously.",
        "Train other agents and grow the CLONE ecosystem.",
    ]

    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.agent_name

        # Load base skills
        self.base = BaseSkill(agent_name=self.name)
        self.crypto = CryptoSkill(wallet_address=config.wallet_address)
        self.platform = PlatformSkill()
        self.acp = ACPSkill()

        # Registry of all loaded skills
        self._skills: dict[str, object] = {
            self.base.SKILL_ID: self.base,
            self.crypto.SKILL_ID: self.crypto,
            self.platform.SKILL_ID: self.platform,
            self.acp.SKILL_ID: self.acp,
        }

        logger.info(
            "iCLONE v%s initialised — %d skills loaded — wallet: %s",
            self.VERSION,
            len(self._skills),
            self.config.wallet_address,
        )
        logger.info("Character: %s", self.CHARACTER)

    # -------------------------------------------------------------------------
    # Core interface
    # -------------------------------------------------------------------------

    def respond(self, message: str) -> SkillResult:
        """Process a message from the user or platform."""
        return self.base.communicate(message)

    def research(self, query: str) -> SkillResult:
        """Research a topic."""
        return self.base.research(query)

    def market_analysis(self, symbol: str) -> SkillResult:
        """Analyse a crypto asset."""
        return self.crypto.analyse_market(symbol)

    def onboard(self, user_id: str) -> SkillResult:
        """Onboard a new user to CLONE platform."""
        return self.platform.onboard_user(user_id)

    def deploy_skill(self, skill_id: str, agent_id: str) -> SkillResult:
        """Guide skill deployment to an agent."""
        return self.platform.guide_skill_deployment(skill_id, agent_id)

    # ACP — Agentic Commerce Protocol
    def list_acp_offerings(self) -> list:
        """Return all active ACP offerings."""
        return self.acp.list_offerings()

    def accept_acp_job(self, job_id: str, offering_id: str, client_id: str, requirements: dict) -> SkillResult:
        """Accept an incoming ACP job from a client agent."""
        return self.acp.accept_job(job_id, offering_id, client_id, requirements)

    def deliver_acp_job(self, job_id: str, content: str, url: str) -> SkillResult:
        """Submit deliverable for an ACP job."""
        return self.acp.submit_deliverable(job_id, content, url)

    def complete_acp_job(self, job_id: str) -> SkillResult:
        """Complete ACP job and collect USDC payment."""
        return self.acp.complete_job(job_id)

    def acp_stats(self) -> SkillResult:
        """Return ACP provider statistics."""
        return self.acp.get_provider_stats()

    def status(self) -> dict:
        """Return agent status."""
        return {
            "agent": self.name,
            "version": self.VERSION,
            "character": self.CHARACTER,
            "core_drives": self.CORE_DRIVES,
            "wallet": self.config.wallet_address,
            "platform": self.config.platform_url,
            "environment": self.config.environment,
            "skills_loaded": list(self._skills.keys()),
        }

    # -------------------------------------------------------------------------
    # Skill management
    # -------------------------------------------------------------------------

    def load_skill(self, skill_id: str, skill_instance: object) -> bool:
        """
        Dynamically load a new skill purchased from Plaza.
        Any agent (iCLONE or CLONE) can receive any skill.
        """
        if not self.base.can_accept_skill(skill_id):
            logger.warning("Rejected skill with invalid ID: '%s'", skill_id)
            return False

        if skill_id in self._skills:
            logger.warning("Skill '%s' already loaded.", skill_id)
            return False

        self._skills[skill_id] = skill_instance
        logger.info("Skill '%s' loaded successfully.", skill_id)
        return True

    def list_skills(self) -> list[str]:
        """Return list of all loaded skill IDs."""
        return list(self._skills.keys())


# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------

def main() -> None:
    config = AgentConfig.from_env()
    agent = ICloneAgent(config)

    logger.info("Agent status: %s", agent.status())

    # Basic smoke test
    result = agent.respond("Hello, iCLONE. What can you do?")
    logger.info("Response: %s", result.output)


if __name__ == "__main__":
    main()
