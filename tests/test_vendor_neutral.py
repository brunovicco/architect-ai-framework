"""Guards the engine's vendor-neutrality contract: no engine output may
name a specific model vendor or product.
"""

from architect.engine import recommend
from architect.models import ArchitectureCase


def test_model_strategy_is_provider_neutral():
    """model_strategy talks about selection criteria, not vendor names."""
    result = recommend(ArchitectureCase())
    text = " ".join(result.model_strategy).lower()
    assert "quality" in text
    assert "latency" in text
    assert "privacy" in text
    assert "lock-in" in text


def test_tool_protocol_is_not_tied_to_model_provider():
    """The tool-protocol integration pattern names a generic protocol, not a vendor."""
    result = recommend(ArchitectureCase(many_external_capabilities=True))
    assert result.integration_pattern == "Tool Protocol/MCP"
