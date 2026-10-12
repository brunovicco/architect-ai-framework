from arquiteto.engine import recommend
from arquiteto.models import ArchitectureCase


def test_model_strategy_is_provider_neutral():
    result = recommend(ArchitectureCase())
    text = " ".join(result.model_strategy).lower()
    assert "quality" in text
    assert "latency" in text
    assert "privacy" in text
    assert "lock-in" in text


def test_tool_protocol_is_not_tied_to_model_provider():
    result = recommend(ArchitectureCase(many_external_capabilities=True))
    assert result.integration_pattern == "Tool Protocol / MCP"
