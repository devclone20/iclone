"""
TDD — iCLONE Agent Test Suite
Tests the agent core: initialisation, skill loading, interface.
Run: pytest agent/iclone/tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock

from agent.iclone.agent import ICloneAgent
from agent.iclone.config import AgentConfig


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def config():
    return AgentConfig(
        game_api_key="test_game_key",
        virtuals_agent_id="test_agent_id",
        anthropic_api_key="test_anthropic_key",
        agent_name="iCLONE AI",
        wallet_address="0x743665952ec1240D62A3e580e5DC2c9e421d0537",
        platform_url="http://localhost:3000",
        environment="test",
    )

@pytest.fixture
def agent(config):
    return ICloneAgent(config)


# =============================================================================
# Initialisation
# =============================================================================

class TestICloneAgentInit:

    def test_agent_initialises(self, agent):
        assert agent is not None

    def test_agent_has_correct_name(self, agent):
        assert agent.name == "iCLONE AI"

    def test_agent_loads_four_base_skills(self, agent):
        assert len(agent.list_skills()) == 4

    def test_agent_loads_base_skill(self, agent):
        assert "base_skill_v1" in agent.list_skills()

    def test_agent_loads_crypto_skill(self, agent):
        assert "crypto_skill_v1" in agent.list_skills()

    def test_agent_loads_platform_skill(self, agent):
        assert "platform_skill_v1" in agent.list_skills()

    def test_agent_status_returns_dict(self, agent):
        status = agent.status()
        assert isinstance(status, dict)

    def test_agent_status_contains_wallet(self, agent):
        status = agent.status()
        assert status["wallet"] == "0x743665952ec1240D62A3e580e5DC2c9e421d0537"

    def test_agent_status_contains_version(self, agent):
        status = agent.status()
        assert "version" in status


# =============================================================================
# Core interface
# =============================================================================

class TestICloneAgentInterface:

    def test_respond_returns_success(self, agent):
        result = agent.respond("Hello iCLONE")
        assert result.success is True

    def test_respond_empty_message_fails(self, agent):
        result = agent.respond("")
        assert result.success is False

    def test_research_returns_success(self, agent):
        result = agent.research("Virtuals Protocol GAME SDK")
        assert result.success is True

    def test_market_analysis_returns_success(self, agent):
        result = agent.market_analysis("VIRTUAL")
        assert result.success is True

    def test_onboard_returns_success(self, agent):
        result = agent.onboard("user_001")
        assert result.success is True

    def test_deploy_skill_returns_success(self, agent):
        result = agent.deploy_skill("new_skill_v1", "agent_001")
        assert result.success is True


# =============================================================================
# Skill management
# =============================================================================

class TestICloneSkillManagement:

    def test_load_new_skill_succeeds(self, agent):
        mock_skill = MagicMock()
        result = agent.load_skill("new_skill_v2", mock_skill)
        assert result is True

    def test_load_duplicate_skill_fails(self, agent):
        mock_skill = MagicMock()
        result = agent.load_skill("base_skill_v1", mock_skill)
        assert result is False

    def test_load_empty_skill_id_fails(self, agent):
        mock_skill = MagicMock()
        result = agent.load_skill("", mock_skill)
        assert result is False

    def test_loaded_skill_appears_in_list(self, agent):
        mock_skill = MagicMock()
        agent.load_skill("plaza_skill_v1", mock_skill)
        assert "plaza_skill_v1" in agent.list_skills()

    def test_list_skills_returns_list(self, agent):
        assert isinstance(agent.list_skills(), list)


# =============================================================================
# Config
# =============================================================================

class TestAgentConfig:

    def test_config_missing_required_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError):
                AgentConfig.from_env()

    def test_config_is_production_false_in_test(self, config):
        assert config.is_production is False

    def test_config_is_production_true_when_set(self, config):
        config.environment = "production"
        assert config.is_production is True
