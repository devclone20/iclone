"""
TDD — ACP Skill Test Suite
Tests iCLONE as ACP Provider on Virtuals Protocol.
Run: pytest agent/iclone/tests/test_acp_skill.py -v
"""

import pytest
from agent.iclone.skills.acp_skill import (
    ACPSkill,
    JobOffering,
    JobStatus,
    OfferingCategory,
)


@pytest.fixture
def skill():
    return ACPSkill()


VALID_REQUIREMENTS = {
    "agent_name": "TestAgent",
    "agent_category": "CLONE",
    "desired_skills": ["crypto_skill_v1"],
    "wallet_address": "0x123",
}


# =============================================================================
# Offerings
# =============================================================================

class TestACPOfferings:

    def test_default_offerings_loaded(self, skill):
        offerings = skill.list_offerings()
        assert len(offerings) >= 5

    def test_all_default_offerings_are_active(self, skill):
        for o in skill.list_offerings():
            assert o.active is True

    def test_get_offering_valid_id(self, skill):
        result = skill.get_offering("iclone-train-agent-v1")
        assert result.success is True

    def test_get_offering_contains_price(self, skill):
        result = skill.get_offering("iclone-crypto-research-v1")
        assert result.data["price_usdc"] == 5.0

    def test_get_offering_invalid_id_fails(self, skill):
        result = skill.get_offering("nonexistent")
        assert result.success is False

    def test_offering_has_required_fields(self, skill):
        result = skill.get_offering("iclone-train-agent-v1")
        data = result.data
        assert "name" in data
        assert "description" in data
        assert "price_usdc" in data
        assert "sla_hours" in data
        assert "requirements" in data
        assert "deliverable" in data

    def test_all_offerings_have_sla(self, skill):
        for o in skill.list_offerings():
            assert o.sla_hours > 0

    def test_all_offerings_have_price(self, skill):
        for o in skill.list_offerings():
            assert o.price_usdc > 0


# =============================================================================
# Job acceptance
# =============================================================================

class TestACPJobAcceptance:

    def test_accept_valid_job(self, skill):
        result = skill.accept_job(
            "job_001",
            "iclone-train-agent-v1",
            "client_agent_xyz",
            VALID_REQUIREMENTS,
        )
        assert result.success is True

    def test_accept_job_status_is_accepted(self, skill):
        result = skill.accept_job(
            "job_002",
            "iclone-train-agent-v1",
            "client_agent_xyz",
            VALID_REQUIREMENTS,
        )
        assert result.data["status"] == JobStatus.ACCEPTED

    def test_accept_job_missing_required_field_fails(self, skill):
        incomplete = {"agent_name": "Test"}
        result = skill.accept_job(
            "job_003",
            "iclone-train-agent-v1",
            "client_agent_xyz",
            incomplete,
        )
        assert result.success is False
        assert "Missing required fields" in result.error

    def test_accept_job_invalid_offering_fails(self, skill):
        result = skill.accept_job(
            "job_004",
            "nonexistent_offering",
            "client_agent_xyz",
            VALID_REQUIREMENTS,
        )
        assert result.success is False

    def test_accept_job_empty_job_id_fails(self, skill):
        result = skill.accept_job("", "iclone-train-agent-v1", "client", VALID_REQUIREMENTS)
        assert result.success is False

    def test_accept_job_contains_price(self, skill):
        result = skill.accept_job(
            "job_005",
            "iclone-train-agent-v1",
            "client_agent_xyz",
            VALID_REQUIREMENTS,
        )
        assert result.data["price_usdc"] == 50.0


# =============================================================================
# Deliverable submission
# =============================================================================

class TestACPDeliverable:

    def setup_method(self):
        self.skill = ACPSkill()
        self.skill.accept_job(
            "job_del_001",
            "iclone-train-agent-v1",
            "client_agent_xyz",
            VALID_REQUIREMENTS,
        )

    def test_submit_deliverable_success(self):
        result = self.skill.submit_deliverable(
            "job_del_001",
            "Agent deployed and configured.",
            "https://example.com/deliverable/job_del_001",
        )
        assert result.success is True

    def test_submit_deliverable_status_is_delivered(self):
        result = self.skill.submit_deliverable(
            "job_del_001",
            "Agent deployed.",
            "https://example.com/d/001",
        )
        assert result.data["status"] == JobStatus.DELIVERED

    def test_submit_deliverable_nonexistent_job_fails(self):
        result = self.skill.submit_deliverable(
            "nonexistent_job",
            "Content",
            "https://example.com",
        )
        assert result.success is False

    def test_submit_deliverable_empty_content_fails(self):
        result = self.skill.submit_deliverable("job_del_001", "", "https://example.com")
        assert result.success is False

    def test_submit_deliverable_empty_url_fails(self):
        result = self.skill.submit_deliverable("job_del_001", "Content", "")
        assert result.success is False

    def test_submit_deliverable_contains_memo_hash(self):
        result = self.skill.submit_deliverable(
            "job_del_001",
            "Delivered content",
            "https://example.com/d",
        )
        assert "memo_hash" in result.data

    def test_submit_deliverable_next_step_is_escrow(self):
        result = self.skill.submit_deliverable(
            "job_del_001",
            "Delivered",
            "https://example.com",
        )
        assert "escrow" in result.data["next_step"]


# =============================================================================
# Job completion & payment
# =============================================================================

class TestACPJobCompletion:

    def setup_method(self):
        self.skill = ACPSkill()
        self.skill.accept_job(
            "job_comp_001",
            "iclone-train-agent-v1",
            "client_agent_xyz",
            VALID_REQUIREMENTS,
        )
        self.skill.submit_deliverable(
            "job_comp_001",
            "Delivered.",
            "https://example.com/d",
        )

    def test_complete_job_success(self):
        result = self.skill.complete_job("job_comp_001")
        assert result.success is True

    def test_complete_job_usdc_earned(self):
        result = self.skill.complete_job("job_comp_001")
        assert result.data["usdc_earned"] == 50.0

    def test_complete_job_status_is_completed(self):
        result = self.skill.complete_job("job_comp_001")
        assert result.data["status"] == JobStatus.COMPLETED

    def test_complete_job_not_delivered_fails(self):
        skill = ACPSkill()
        skill.accept_job(
            "job_nd_001",
            "iclone-train-agent-v1",
            "client",
            VALID_REQUIREMENTS,
        )
        result = skill.complete_job("job_nd_001")
        assert result.success is False

    def test_complete_nonexistent_job_fails(self):
        result = self.skill.complete_job("ghost_job")
        assert result.success is False


# =============================================================================
# Provider stats
# =============================================================================

class TestACPProviderStats:

    def test_stats_returns_success(self, skill):
        result = skill.get_provider_stats()
        assert result.success is True

    def test_stats_contains_provider_id(self, skill):
        result = skill.get_provider_stats()
        assert result.data["provider_id"] == "iclone-ai"

    def test_stats_initial_earnings_zero(self, skill):
        result = skill.get_provider_stats()
        assert result.data["total_usdc_earned"] == 0.0

    def test_stats_earnings_increase_after_completion(self, skill):
        skill.accept_job("j1", "iclone-crypto-research-v1", "client", {"target_asset_or_protocol": "VIRTUAL"})
        skill.submit_deliverable("j1", "Research done", "https://x.com")
        skill.complete_job("j1")
        result = skill.get_provider_stats()
        assert result.data["total_usdc_earned"] == 5.0

    def test_stats_reputation_standard(self, skill):
        result = skill.get_provider_stats()
        assert result.data["reputation_standard"] == "ERC-8004"
