"""
TDD — CLONE Skills Test Suite
Tests written before implementation validation.
Run: pytest agent/iclone/tests/ -v
"""

import pytest
from agent.iclone.skills import BaseSkill, CryptoSkill, PlatformSkill, SkillResult


# =============================================================================
# BaseSkill
# =============================================================================

class TestBaseSkill:

    def setup_method(self):
        self.skill = BaseSkill(agent_name="iCLONE AI")

    # --- communicate ---

    def test_communicate_returns_success(self):
        result = self.skill.communicate("Hello")
        assert result.success is True

    def test_communicate_returns_skill_result(self):
        result = self.skill.communicate("Hello")
        assert isinstance(result, SkillResult)

    def test_communicate_empty_message_fails(self):
        result = self.skill.communicate("")
        assert result.success is False
        assert result.error is not None

    def test_communicate_whitespace_only_fails(self):
        result = self.skill.communicate("   ")
        assert result.success is False

    def test_communicate_includes_agent_name(self):
        result = self.skill.communicate("test")
        assert "iCLONE AI" in result.output

    # --- research ---

    def test_research_returns_success(self):
        result = self.skill.research("Virtuals Protocol")
        assert result.success is True

    def test_research_empty_query_fails(self):
        result = self.skill.research("")
        assert result.success is False

    def test_research_includes_query_in_data(self):
        result = self.skill.research("CLONE platform")
        assert result.data["query"] == "CLONE platform"

    # --- platform status ---

    def test_platform_status_returns_success(self):
        result = self.skill.get_platform_status()
        assert result.success is True

    def test_platform_status_data_contains_platform(self):
        result = self.skill.get_platform_status()
        assert result.data["platform"] == "CLONE"

    # --- skill acceptance ---

    def test_can_accept_valid_skill(self):
        assert self.skill.can_accept_skill("crypto_skill_v1") is True

    def test_rejects_empty_skill_id(self):
        assert self.skill.can_accept_skill("") is False

    def test_rejects_whitespace_skill_id(self):
        assert self.skill.can_accept_skill("   ") is False


# =============================================================================
# CryptoSkill
# =============================================================================

class TestCryptoSkill:

    WALLET = "0x743665952ec1240D62A3e580e5DC2c9e421d0537"

    def setup_method(self):
        self.skill = CryptoSkill(wallet_address=self.WALLET)

    def test_wallet_context_returns_success(self):
        result = self.skill.get_wallet_context()
        assert result.success is True

    def test_wallet_context_contains_address(self):
        result = self.skill.get_wallet_context()
        assert self.WALLET in result.output

    def test_analyse_market_valid_symbol(self):
        result = self.skill.analyse_market("BTC")
        assert result.success is True

    def test_analyse_market_lowercase_normalised(self):
        result = self.skill.analyse_market("btc")
        assert result.data["symbol"] == "BTC"

    def test_analyse_market_empty_symbol_fails(self):
        result = self.skill.analyse_market("")
        assert result.success is False

    def test_tracked_asset_flagged(self):
        result = self.skill.analyse_market("VIRTUAL")
        assert result.data["tracked"] is True

    def test_untracked_asset_not_flagged(self):
        result = self.skill.analyse_market("DOGE")
        assert result.data["tracked"] is False

    def test_research_protocol_returns_success(self):
        result = self.skill.research_protocol("Virtuals Protocol")
        assert result.success is True

    def test_research_protocol_empty_fails(self):
        result = self.skill.research_protocol("")
        assert result.success is False


# =============================================================================
# PlatformSkill
# =============================================================================

class TestPlatformSkill:

    def setup_method(self):
        self.skill = PlatformSkill()

    def test_onboard_user_returns_success(self):
        result = self.skill.onboard_user("user_123")
        assert result.success is True

    def test_onboard_empty_user_id_fails(self):
        result = self.skill.onboard_user("")
        assert result.success is False

    def test_onboard_data_contains_user_id(self):
        result = self.skill.onboard_user("user_456")
        assert result.data["user_id"] == "user_456"

    def test_explain_iclone_category(self):
        result = self.skill.explain_agent("iclone")
        assert result.success is True
        assert "iCLONE" in result.output

    def test_explain_clone_category(self):
        result = self.skill.explain_agent("clone")
        assert result.success is True

    def test_explain_unknown_category_fails(self):
        result = self.skill.explain_agent("legendary")
        assert result.success is False

    def test_deploy_skill_valid_ids(self):
        result = self.skill.guide_skill_deployment("crypto_skill_v1", "agent_001")
        assert result.success is True

    def test_deploy_skill_empty_skill_id_fails(self):
        result = self.skill.guide_skill_deployment("", "agent_001")
        assert result.success is False

    def test_deploy_skill_empty_agent_id_fails(self):
        result = self.skill.guide_skill_deployment("crypto_skill_v1", "")
        assert result.success is False

    def test_deploy_skill_data_contains_route(self):
        result = self.skill.guide_skill_deployment("crypto_skill_v1", "agent_001")
        assert "HUB" in result.data["route"]
