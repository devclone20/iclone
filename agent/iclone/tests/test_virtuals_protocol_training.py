"""
TDD — Virtuals Protocol Training Test Suite
Validates iCLONE's knowledge of the full Virtuals Protocol whitepaper.
"""

import pytest
from agent.iclone.training.virtuals_protocol_training import VirtualsProtocolTraining


@pytest.fixture
def vp():
    return VirtualsProtocolTraining()


class TestFivePillars:

    def test_economy_os_has_components(self, vp):
        assert len(vp.ECONOMY_OS["components"]) >= 4

    def test_iclone_email_correct(self, vp):
        assert vp.ECONOMY_OS["iclone_identity"]["email"] == "iclone@agents.world"

    def test_acp_has_four_phases(self, vp):
        assert len(vp.ACP["four_phase_lifecycle"]) == 4

    def test_acp_provider_share_correct(self, vp):
        assert "60%" in vp.ACP["payment_model"]["provider_share"]

    def test_acp_erc_standard(self, vp):
        assert "ERC-8183" in vp.ACP["standard"]

    def test_graduation_threshold(self, vp):
        assert "42,000" in vp.TOKENIZATION["bonding_curve"]["graduation_threshold"]

    def test_lp_lock_duration(self, vp):
        assert "10" in vp.TOKENIZATION["bonding_curve"]["lp_lock"]

    def test_trading_fee_split(self, vp):
        assert "70%" in vp.TOKENIZATION["bonding_curve"]["trading_fee"]

    def test_robotics_fdv_threshold(self, vp):
        assert "$5M" in vp.ROBOTICS["eligibility"]


class TestTokenomics:

    def test_launch_modules_count(self, vp):
        assert len(vp.TOKENIZATION["launch_modules"]) >= 6

    def test_capital_formation_activation_cost(self, vp):
        assert "10" in vp.TOKENIZATION["launch_modules"]["capital_formation"]["cost"]

    def test_iclone_fdv_target(self, vp):
        assert vp.TOKENIZATION["iclone_token_plan"]["fdv_target"] == "$100,000,000"

    def test_iclone_token_supply(self, vp):
        assert vp.TOKENIZATION["iclone_token_plan"]["total_supply"] == "1,000,000,000"

    def test_distribution_sums_correctly(self, vp):
        dist = vp.TOKENIZATION["iclone_token_plan"]["distribution"]
        total = sum(int(v.replace("%", "")) for v in dist.values())
        assert total == 100

    def test_vestual_staking_benefits(self, vp):
        assert len(vp.TOKENIZATION["vestual_staking"]["benefits"]) >= 2

    def test_console_hosting_cost(self, vp):
        assert "20 USDC" in vp.TOKENIZATION["console_hosting"]["hosting"]


class TestACPStrategy:

    def test_iclone_role_is_hybrid(self, vp):
        assert "HYBRID" in vp.ACP["iclone_strategy"]["role"]

    def test_subscription_tiers_known(self, vp):
        assert "90" in vp.ACP["acp_v2_features"]["subscription_options"]

    def test_butler_pro_mode_known(self, vp):
        assert "pro_mode" in vp.ACP["butler"]

    def test_hook_architecture_known(self, vp):
        assert "hook" in vp.ACP["acp_v2_features"]["hook_architecture"].lower()


class TestAgenticGDP:

    def test_gdp_baseline_exists(self, vp):
        assert vp.AGENTIC_GDP["current_baseline"]["cumulative_agentic_gdp"] == "$400M+"

    def test_agents_deployed_known(self, vp):
        assert "17,000" in vp.AGENTIC_GDP["current_baseline"]["agents_deployed"]

    def test_iclone_gdp_contribution_defined(self, vp):
        assert len(vp.AGENTIC_GDP["iclone_contribution"]) > 0


class TestTrainingSession:

    def test_session_completes(self, vp):
        result = vp.run_session("test_vp_001")
        assert result["completed"] is True

    def test_session_covers_five_pillars(self, vp):
        result = vp.run_session("test_vp_002")
        assert result["pillars_covered"] == 5

    def test_session_has_insights(self, vp):
        result = vp.run_session("test_vp_003")
        assert result["insights_count"] >= 10

    def test_session_has_timestamp(self, vp):
        result = vp.run_session("test_vp_004")
        assert "timestamp" in result
