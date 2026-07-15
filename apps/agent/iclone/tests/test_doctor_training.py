"""
TDD — Doctor Training Test Suite
Validates iCLONE's academic research and scientific intelligence.
"""

import pytest
from agent.iclone.training.doctor_training import DoctorTraining


@pytest.fixture
def doctor():
    return DoctorTraining()


class TestResearchMethodology:

    def test_primary_sources_defined(self, doctor):
        assert len(doctor.RESEARCH_METHODOLOGY["primary_sources"]) >= 5

    def test_arxiv_is_first_source(self, doctor):
        assert "arXiv" in doctor.RESEARCH_METHODOLOGY["primary_sources"][0]

    def test_research_pipeline_eight_steps(self, doctor):
        assert len(doctor.RESEARCH_METHODOLOGY["research_pipeline"]) == 8

    def test_never_fabricate_rule_present(self, doctor):
        assert "NEVER" in doctor.RESEARCH_METHODOLOGY["never_fabricate"]

    def test_citation_formats_include_bibtex(self, doctor):
        assert "BibTeX" in doctor.RESEARCH_METHODOLOGY["citation_formats"]


class TestRelevantPapers:

    def test_six_research_domains(self, doctor):
        assert len(doctor.RELEVANT_PAPERS) >= 6

    def test_llm_security_domain_present(self, doctor):
        assert "llm_security" in doctor.RELEVANT_PAPERS

    def test_trading_domain_present(self, doctor):
        assert "trading_and_financial_ml" in doctor.RELEVANT_PAPERS

    def test_blockchain_domain_present(self, doctor):
        assert "blockchain_tokenomics" in doctor.RELEVANT_PAPERS

    def test_ist_sparse_attention_paper_known(self, doctor):
        paper = doctor.RELEVANT_PAPERS["sparse_attention_transformers"]["known_paper"]
        assert "2506.16640" in paper["arxiv"]
        assert "Martins" in paper["authors"]

    def test_ist_geers_paper_known(self, doctor):
        paper = doctor.RELEVANT_PAPERS["robotics_and_sensor_fusion"]["known_paper"]
        assert "IROS 2024" in paper["venue"]
        assert "ISR/IST" in paper["affiliation"]

    def test_llm_security_has_search_terms(self, doctor):
        domain = doctor.RELEVANT_PAPERS["llm_security"]
        assert len(domain["search_terms"]) >= 4


class TestISTStandards:

    def test_dissertation_has_correct_chapters(self, doctor):
        assert len(doctor.IST_STANDARDS["dissertation_structure"]) >= 8

    def test_abstract_template_four_sentences(self, doctor):
        template = doctor.IST_STANDARDS["abstract_template"]
        assert "4" in template

    def test_writing_rules_minimum_five(self, doctor):
        assert len(doctor.IST_STANDARDS["writing_rules"]) >= 5

    def test_evaluation_requires_ablation(self, doctor):
        assert "ablation" in doctor.IST_STANDARDS["evaluation_requirements"]["ablation"].lower()

    def test_evaluation_requires_baselines(self, doctor):
        assert "2" in doctor.IST_STANDARDS["evaluation_requirements"]["baselines"]

    def test_reproducibility_required(self, doctor):
        assert "reproducibility" in doctor.IST_STANDARDS["evaluation_requirements"]


class TestWritingQuality:

    def test_common_mistakes_defined(self, doctor):
        assert len(doctor.WRITING_QUALITY["common_mistakes"]) >= 4

    def test_precision_rule_demands_quantification(self, doctor):
        assert "quantif" in doctor.WRITING_QUALITY["precision"].lower() or "p<" in doctor.WRITING_QUALITY["precision"]


class TestSecurityRules:

    def test_rule_31_no_credentials_in_code(self, doctor):
        assert "os.environ" in doctor.DOCTOR_SECURITY_RULES["rule_31"]

    def test_rule_32_tee_placeholder(self, doctor):
        assert "EXAMPLE_ONLY" in doctor.DOCTOR_SECURITY_RULES["rule_32"]

    def test_rule_33_threat_model_first(self, doctor):
        assert "Threat Model" in doctor.DOCTOR_SECURITY_RULES["rule_33"]

    def test_no_fabrication_rule_present(self, doctor):
        assert "NEVER" in doctor.DOCTOR_SECURITY_RULES["no_fabrication"]


class TestResearchToACP:

    def test_pipeline_seven_steps(self, doctor):
        assert len(doctor.RESEARCH_TO_ACP["pipeline"]) == 7

    def test_high_value_offerings_defined(self, doctor):
        assert len(doctor.RESEARCH_TO_ACP["high_value_research_offerings"]) >= 4


class TestTrainingSession:

    def test_session_completes(self, doctor):
        result = doctor.run_session("test_doc_001")
        assert result["completed"] is True

    def test_session_has_insights(self, doctor):
        result = doctor.run_session("test_doc_002")
        assert result["insights_count"] >= 10

    def test_session_has_research_domains(self, doctor):
        result = doctor.run_session("test_doc_003")
        assert result["research_domains"] >= 5

    def test_session_has_ist_rules(self, doctor):
        result = doctor.run_session("test_doc_004")
        assert result["ist_rules_active"] >= 10

    def test_session_has_timestamp(self, doctor):
        result = doctor.run_session("test_doc_005")
        assert "timestamp" in result
