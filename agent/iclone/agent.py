"""
CLONE — iCLONE Agent
Official platform agent. Built on Virtuals Protocol GAME SDK.

Identity:
  Name:    iCLONE AI
  Role:    Platform governor, assistant, and crypto specialist
  Wallet:  0x743665952ec1240D62A3e580e5DC2c9e421d0537
"""

import os
import logging
from dotenv import load_dotenv

from .config import AgentConfig
from .skills import BaseSkill, CryptoSkill, PlatformSkill, SkillResult

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("iclone")


class ICloneAgent:
    """
    iCLONE — the governing AI agent of the CLONE platform.

    Skills loaded by default:
      - BaseSkill     : communication, research, Q&A
      - CryptoSkill   : crypto markets, wallet, DeFi research
      - PlatformSkill : CLONE platform governance and onboarding
    """

    VERSION = "0.1.0"

    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.agent_name

        # Load base skills
        self.base = BaseSkill(agent_name=self.name)
        self.crypto = CryptoSkill(wallet_address=config.wallet_address)
        self.platform = PlatformSkill()

        # Registry of all loaded skills
        self._skills: dict[str, object] = {
            self.base.SKILL_ID: self.base,
            self.crypto.SKILL_ID: self.crypto,
            self.platform.SKILL_ID: self.platform,
        }

        logger.info(
            "iCLONE v%s initialised — %d skills loaded — wallet: %s",
            self.VERSION,
            len(self._skills),
            self.config.wallet_address,
        )

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

    def status(self) -> dict:
        """Return agent status."""
        return {
            "agent": self.name,
            "version": self.VERSION,
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
