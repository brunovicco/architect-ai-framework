from arquiteto.engine import recommend
from arquiteto.exporters import to_markdown
from arquiteto.models import ArchitectureCase, DecisionPlan


def test_markdown_contains_core_sections():
    case = ArchitectureCase(name="Demo", business_problem="Reduce review time")
    plan = DecisionPlan(case=case, recommendation=recommend(case))
    md = to_markdown(plan)
    assert "# Architecture Decision Plan — Demo" in md
    assert "## T — Trust & Controls" in md
    assert "## E — Evaluation" in md
