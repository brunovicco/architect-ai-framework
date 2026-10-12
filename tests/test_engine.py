"""Tests for the decision rules in `architect.engine.recommend` and its
private per-field helper functions.
"""

from architect.engine import recommend
from architect.models import ArchitectureCase


def test_known_path_prefers_workflow():
    """A known execution path recommends Workflow."""
    result = recommend(ArchitectureCase(path_known=True))
    assert result.architecture_pattern == "Workflow"


def test_dynamic_execution_prefers_agent():
    """Dynamic next-steps/tool-choice (without independent domains) recommends Agent."""
    result = recommend(ArchitectureCase(
        path_known=False, dynamic_next_steps=True, dynamic_tool_choice=True))
    assert result.architecture_pattern == "Agent"


def test_multi_agent_requires_separate_autonomy_and_dynamic_execution():
    """Independent autonomous domains plus dynamic execution recommends
    Multi-agent and raises a warning to validate the added complexity.
    """
    result = recommend(ArchitectureCase(
        path_known=False, dynamic_next_steps=True, independent_autonomous_domains=True))
    assert result.architecture_pattern == "Multi-agent"
    assert result.warnings


def test_dynamic_data_prefers_api_tool():
    """Dynamic data needs recommend API/Tool integration, with a source-of-truth rationale."""
    result = recommend(ArchitectureCase(needs_dynamic_data=True))
    assert result.integration_pattern == "API/Tool"
    assert any("source of truth" in x for x in result.information_strategy)


def test_high_impact_adds_fail_closed_and_idempotency():
    """High-impact/irreversible actions add fail-closed controls and idempotency operations."""
    result = recommend(ArchitectureCase(
        high_impact_actions=True, irreversible_actions=True))
    controls = " ".join(result.controls).lower()
    ops = " ".join(result.operations).lower()
    assert "fail-closed" in controls
    assert "idempotency" in ops


def test_high_impact_splits_controls_into_input_output_authorization():
    """High-impact actions get distinct input-screening, output-screening and authorization controls."""
    result = recommend(ArchitectureCase(high_impact_actions=True))
    controls = " ".join(result.controls)
    assert "Input screening:" in controls
    assert "Output screening:" in controls
    assert "Authorization:" in controls


# Entry point


def test_multi_client_reuse_prefers_protocol_server():
    """Multi-client reuse need recommends a protocol server entry point."""
    result = recommend(ArchitectureCase(reusable_across_multiple_clients=True))
    assert result.entry_point == "Protocol server for multi-client reuse"


def test_engineering_tool_prefers_agentic_coding_assistant():
    """An engineering-tool use case recommends an agentic coding assistant entry point."""
    result = recommend(ArchitectureCase(is_engineering_tool=True))
    assert result.entry_point == "Agentic coding assistant (CLI/IDE)"


def test_custom_experience_prefers_direct_api_sdk():
    """A custom user experience need recommends direct API/SDK integration."""
    result = recommend(ArchitectureCase(needs_custom_user_experience=True))
    assert result.entry_point == "Direct API/SDK integration"


def test_default_entry_point_is_hosted_chat():
    """With no entry-point signal set, the default entry point is hosted chat/web UI."""
    result = recommend(ArchitectureCase())
    assert result.entry_point == "Hosted chat/web UI"


# Reference architecture


def test_multi_agent_maps_to_orchestrator_workers():
    """Multi-agent architecture maps to the orchestrator-workers reference architecture."""
    result = recommend(ArchitectureCase(
        path_known=False, dynamic_next_steps=True, independent_autonomous_domains=True))
    assert result.reference_architecture == "Orchestrator-workers"


def test_agent_with_engineering_tool_maps_to_coding_agent():
    """An Agent architecture for an engineering tool maps to the coding-agent reference architecture."""
    result = recommend(ArchitectureCase(
        dynamic_tool_choice=True, is_engineering_tool=True))
    assert result.reference_architecture == "Coding agent"


def test_agent_without_engineering_tool_maps_to_autonomous_tool_use():
    """An Agent architecture outside engineering maps to autonomous tool use."""
    result = recommend(ArchitectureCase(dynamic_tool_choice=True))
    assert result.reference_architecture == "Agent (autonomous tool use)"


def test_workflow_with_many_capabilities_maps_to_routing():
    """A Workflow with many external capabilities maps to the routing reference architecture."""
    result = recommend(ArchitectureCase(
        path_known=True, many_external_capabilities=True))
    assert result.reference_architecture == "Routing"


def test_workflow_document_extraction_maps_to_document_processing_pipeline():
    """A Workflow needing structured document extraction maps to a document processing pipeline."""
    result = recommend(ArchitectureCase(
        path_known=True, needs_document_knowledge=True, structured_output=True))
    assert result.reference_architecture == "Document processing pipeline"


def test_plain_workflow_maps_to_chaining():
    """A Workflow with no other signal maps to the chaining reference architecture."""
    result = recommend(ArchitectureCase(path_known=True))
    assert result.reference_architecture == "Chaining"


def test_augmented_llm_with_document_knowledge_maps_to_rag_pipeline():
    """An Augmented LLM needing document knowledge maps to a RAG pipeline."""
    result = recommend(ArchitectureCase(
        path_known=False, needs_document_knowledge=True))
    assert result.reference_architecture == "RAG pipeline"


def test_plain_augmented_llm_maps_to_single_call():
    """An Augmented LLM with no other signal maps to a single augmented call."""
    result = recommend(ArchitectureCase(path_known=False))
    assert result.reference_architecture == "Single augmented call"


# Review placement


def test_irreversible_actions_require_pre_action_approval():
    """Irreversible actions always require pre-action approval."""
    result = recommend(ArchitectureCase(irreversible_actions=True))
    assert result.review_placement == "Pre-action approval"


def test_high_impact_without_confidence_requires_pre_action_approval():
    """High-impact actions without a calibrated confidence score require pre-action approval."""
    result = recommend(ArchitectureCase(high_impact_actions=True))
    assert result.review_placement == "Pre-action approval"


def test_high_impact_with_calibrated_confidence_allows_sampled_review():
    """High-impact actions with a calibrated confidence score only need sampled review."""
    result = recommend(ArchitectureCase(
        high_impact_actions=True, has_calibrated_confidence_score=True))
    assert result.review_placement == "Sampled review"


def test_sensitive_data_alone_gets_post_action_audit():
    """Sensitive data with no higher-risk signal gets a post-action audit."""
    result = recommend(ArchitectureCase(sensitive_data=True))
    assert result.review_placement == "Post-action audit"


def test_no_risk_signals_need_no_review():
    """With no risk signal set, no review is needed."""
    result = recommend(ArchitectureCase())
    assert result.review_placement == "No review needed"


# Feasibility verdict


def test_feasibility_not_assessed_without_cost_inputs_or_warnings():
    """With no cost estimate/ceiling and no warnings, the verdict is "Not assessed"."""
    result = recommend(ArchitectureCase())
    assert result.feasibility_verdict == "Not assessed"


def test_feasibility_as_scoped_when_cost_within_ceiling_and_no_warnings():
    """A cost estimate within the ceiling and no warnings yields "Feasible as scoped"."""
    result = recommend(ArchitectureCase(
        estimated_monthly_cost=100.0, monthly_cost_ceiling=500.0))
    assert result.feasibility_verdict == "Feasible as scoped"


def test_feasibility_not_feasible_when_cost_exceeds_ceiling():
    """A cost estimate exceeding the ceiling yields "Not feasible as scoped" and a warning."""
    result = recommend(ArchitectureCase(
        estimated_monthly_cost=600.0, monthly_cost_ceiling=500.0))
    assert result.feasibility_verdict == "Not feasible as scoped"
    assert any("budget ceiling" in w for w in result.warnings)


def test_feasibility_with_constraints_when_warnings_present():
    """An otherwise-feasible case with an open warning yields "Feasible with constraints"."""
    result = recommend(
        ArchitectureCase(path_known=False, dynamic_next_steps=True,
                         independent_autonomous_domains=True)
    )
    assert result.feasibility_verdict == "Feasible with constraints"
