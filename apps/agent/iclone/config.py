"""
CLONE — iCLONE Agent Configuration
All configuration loaded from environment variables.
No credentials hardcoded.
"""

import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """iCLONE agent configuration."""

    # Virtuals Protocol
    game_api_key: str
    virtuals_agent_id: str

    # AI
    anthropic_api_key: str

    # Identity
    agent_name: str
    wallet_address: str

    # Platform
    platform_url: str
    environment: str

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        required = [
            "GAME_API_KEY",
            "ANTHROPIC_API_KEY",
        ]

        missing = [key for key in required if not os.environ.get(key)]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Copy .env.example to .env and fill in your values."
            )

        return cls(
            game_api_key=os.environ["GAME_API_KEY"],
            virtuals_agent_id=os.environ.get("VIRTUALS_AGENT_ID", ""),
            anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
            agent_name=os.environ.get("AGENT_NAME", "iCLONE AI"),
            wallet_address=os.environ.get(
                "AGENT_WALLET_ADDRESS",
                "0x743665952ec1240D62A3e580e5DC2c9e421d0537",
            ),
            platform_url=os.environ.get("CLONE_PLATFORM_URL", "http://localhost:3000"),
            environment=os.environ.get("NODE_ENV", "development"),
        )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"
