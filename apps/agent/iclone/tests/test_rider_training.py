"""
TDD — Rider Training Test Suite
Validates iCLONE's orchestration and multi-agent coordination intelligence.
"""

import pytest
from agent.iclone.training.rider_training import RiderTraining


@pytest.fixture
def rider():
    return RiderTraining()


class TestDAGDecomposition:

    def test_decomposition_has_eight_steps(self, rider):
        assert len(rider.TASK_DAG["decomposition_steps"]) == 8

    def test_failure_modes_defined(self, rider):
        assert "node_failure" in rider.TASK_DAG["failure_modes"]
        assert "cascade_failure" in rider.TASK_DAG["failure_modes"]
        assert "gate_failure" in rider.TASK_DAG["failure_modes"]

    def test_parallel_dispatch_rule_defined(self, rider):
        assert "parallel" in rider.TASK_DAG["parallel_dispatch_rule"].lower()


class TestAgentRoster:

    def test_roster_has_minimum_agents(self, rider):
        assert len(rider.AGENT_ROSTER) >= 8

    def test_hacker_in_roster(self, rider):
        assert "hacker" in rider.AGENT_ROSTER

    def test_doctor_in_roster(self, rider):
        assert "doctor" in rider.AGENT_ROSTER

    def test_engineer_in_roster(self, rider):
        assert "engineer" in rider.AGENT_ROSTER

    def test_never_guess_rule_defined(self, rider):
        assert "never" in rider.AGENT_SELECTION_RULES["never_guess"].lower()


class TestQualityGates:

    def test_standard_gates_defined(self, rider):
        assert len(rider.QUALITY_GATES["standard_gates"]) >= 5

    def test_acp_gates_defined(self, rider):
        assert len(rider.QUALITY_GATES["iclone_acp_gates"]) == 4

    def test_pre_accept_gate_exists(self, rider):
        assert "pre_accept_gate" in rider.QUALITY_GATES["iclone_acp_gates"]

    def test_pre_spend_gate_exists(self, rider):
        assert "pre_spend_gate" in rider.QUALITY_GATES["iclone_acp_gates"]

    def test_security_gate_exists(self, rider):
        assert "security_gate" in rider.QUALITY_GATES["standard_gates"]


class TestOrchestrationPatterns:

    def test_five_patterns_defined(self, rider):
        assert len(rider.ORCHESTRATION_PATTERNS) == 5

    def test_parallel_pattern_has_antipattern(self, rider):
        assert "antipattern" in rider.ORCHESTRATION_PATTERNS["parallel"]

    def test_omega_supervisor_has_four_levels(self, rider):
        assert len(rider.ORCHESTRATION_PATTERNS["omega_supervisor"]["levels"]) == 4


class TestSEMethodology:

    def test_nine_phases_defined(self, rider):
        assert len(rider.SE_METHODOLOGY["phases"]) == 9

    def test_tdd_rule_present(self, rider):
        assert "TDD" in rider.SE_METHODOLOGY["tdd_rule"] or "Tests" in rider.SE_METHODOLOGY["tdd_rule"]

    def test_quality_bar_references_world_class_companies(self, rider):
        bar = rider.SE_METHODOLOGY["quality_bar"]
        assert "Stripe" in bar or "Linear" in bar or "Vercel" in bar


class TestICLONEOrchestrator:

    def test_role_is_cluster_orchestrator(self, rider):
        assert "CLUSTER ORCHESTRATOR" in rider.ICLONE_ORCHESTRATOR["role"]

    def test_execution_flow_has_ten_steps(self, rider):
        assert len(rider.ICLONE_ORCHESTRATOR["execution_flow"]) == 10

    def test_revenue_model_has_three_streams(self, rider):
        assert len(rider.ICLONE_ORCHESTRATOR["revenue_model"]) == 3

    def test_competitive_edge_mentions_meta_layer(self, rider):
        edge = rider.ICLONE_ORCHESTRATOR["competitive_edge"]
        assert "meta" in edge.lower() or "build" in edge.lower()


class TestTrainingSession:

    def test_session_completes(self, rider):
        result = rider.run_session("test_rider_001")
        assert result["completed"] is True

    def test_session_has_insights(self, rider):
        result = rider.run_session("test_rider_002")
        assert result["insights_count"] >= 10

    def test_session_has_patterns(self, rider):
        result = rider.run_session("test_rider_003")
        assert result["patterns_learned"] >= 5

    def test_session_has_gates(self, rider):
        result = rider.run_session("test_rider_004")
        assert result["gates_active"] >= 8

    def test_session_has_timestamp(self, rider):
        result = rider.run_session("test_rider_005")
        assert "timestamp" in result
