from arquiteto.engine import recommend
from arquiteto.models import ArchitectureCase


def test_known_path_prefers_workflow():
    result = recommend(ArchitectureCase(path_known=True))
    assert result.architecture_pattern == "Workflow"


def test_dynamic_execution_prefers_agent():
    result = recommend(ArchitectureCase(path_known=False, dynamic_next_steps=True, dynamic_tool_choice=True))
    assert result.architecture_pattern == "Agent"


def test_multi_agent_requires_separate_autonomy_and_dynamic_execution():
    result = recommend(ArchitectureCase(path_known=False, dynamic_next_steps=True, independent_autonomous_domains=True))
    assert result.architecture_pattern == "Multi-agent"
    assert result.warnings


def test_dynamic_data_prefers_api_tool():
    result = recommend(ArchitectureCase(needs_dynamic_data=True))
    assert result.integration_pattern == "API / Tool"
    assert any("source of truth" in x for x in result.information_strategy)


def test_high_impact_adds_fail_closed_and_idempotency():
    result = recommend(ArchitectureCase(high_impact_actions=True, irreversible_actions=True))
    controls = " ".join(result.controls).lower()
    ops = " ".join(result.operations).lower()
    assert "fail-closed" in controls
    assert "idempotency" in ops
