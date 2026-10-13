"""Tests for the deterministic sensitivity analysis in
`architect.sensitivity`.
"""

from architect.models import ArchitectureCase
from architect.sensitivity import TRACKED_FIELDS, analyze_sensitivity


def test_dynamic_tool_choice_is_sensitive_for_a_known_path_workflow():
    """Flipping dynamic_tool_choice on a plain Workflow case flips the
    architecture to Agent (and the reference architecture with it)."""
    case = ArchitectureCase(path_known=True)
    findings = analyze_sensitivity(case)
    finding = next(f for f in findings if f.field == "dynamic_tool_choice")
    assert finding.flipped_to is True
    changes = dict((field, (old, new)) for field, old, new in finding.changes)
    assert changes["architecture_pattern"] == ("Workflow", "Agent")
    assert changes["reference_architecture"][1] == "Agent (autonomous tool use)"


def test_deterministic_baseline_is_insensitive_to_architecture_pattern():
    """A deterministic_sufficient=True case never changes architecture_pattern
    by flipping an unrelated risk/review signal, even though that signal
    does change review_placement/feasibility_verdict."""
    case = ArchitectureCase(deterministic_sufficient=True, human_approval_required=True,
                             estimated_monthly_cost=100.0, monthly_cost_ceiling=500.0)
    findings = analyze_sensitivity(case)
    finding = next(f for f in findings if f.field == "human_approval_required")
    changed_fields = {field for field, _, _ in finding.changes}
    assert "architecture_pattern" not in changed_fields
    assert changed_fields <= set(TRACKED_FIELDS)


def test_changes_only_ever_name_tracked_fields():
    """No finding's changes ever reference a Recommendation field outside
    TRACKED_FIELDS (e.g. controls/warnings aren't single discrete values)."""
    case = ArchitectureCase(path_known=True, sensitive_data=True, high_impact_actions=True)
    findings = analyze_sensitivity(case)
    for finding in findings:
        for field, _, _ in finding.changes:
            assert field in TRACKED_FIELDS


def test_analyze_sensitivity_does_not_mutate_the_input_case():
    case = ArchitectureCase(path_known=True, dynamic_tool_choice=False)
    before = case.model_copy()
    analyze_sensitivity(case)
    assert case == before


def test_conflicting_scenario_retains_its_warning():
    case = ArchitectureCase(dynamic_tool_choice=True, bounded_known_tool_set=True)
    finding = next(f for f in analyze_sensitivity(case) if f.field == 'deterministic_sufficient')
    assert any('conflicts with autonomy signals' in w for w in finding.warnings)


def test_warning_only_changes_are_reported_and_resolved():
    case = ArchitectureCase(deterministic_sufficient=True, dynamic_tool_choice=True,
                            estimated_monthly_cost=200, monthly_cost_ceiling=100)
    finding = next(f for f in analyze_sensitivity(case) if f.field == 'dynamic_tool_choice')
    assert not finding.changes  # The budget already made this case infeasible.
    assert any('conflicts with autonomy signals' in w for w in finding.resolved_warnings)
    assert any('budget ceiling' in w for w in finding.warnings)


def test_research_example_keeps_agent_when_tool_catalog_changes():
    import json
    from pathlib import Path

    from architect.engine import recommend

    for suffix in ('', '.pt-br'):
        data = json.loads((Path(__file__).parents[1] / 'examples' / f'research_agent{suffix}.json').read_text())
        case = ArchitectureCase(**data['case'])
        assert case.dynamic_next_steps
        for bounded in (False, True):
            assert recommend(case.model_copy(update={'bounded_known_tool_set': bounded})).architecture_pattern == 'Agent'
        assert recommend(case.model_copy(update={'dynamic_next_steps': False})).architecture_pattern == 'Workflow'
