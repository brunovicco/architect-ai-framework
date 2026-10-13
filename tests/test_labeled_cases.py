"""Checks `architect.engine.recommend` against the hand-labeled reference
suite in `cases.py` and reports the agreement rate on failure.

A mismatch here is either a rule regression or a case whose label needs
updating (with a stated reason) to match an intentional rule change - never
a silent one-line assert tweak.
"""

from cases import LABELED_CASES

from architect.engine import recommend


def evaluate_cases(cases, predict=recommend):
    mismatches = []
    failed_cases = 0
    for labeled in cases:
        before = len(mismatches)
        result = predict(labeled.case)
        if result.architecture_pattern != labeled.expected_architecture_pattern:
            mismatches.append(
                f"{labeled.name}: expected architecture_pattern={labeled.expected_architecture_pattern!r}, "
                f"got {result.architecture_pattern!r} ({labeled.reason})"
            )
        if result.reference_architecture != labeled.expected_reference_architecture:
            mismatches.append(
                f"{labeled.name}: expected reference_architecture={labeled.expected_reference_architecture!r}, "
                f"got {result.reference_architecture!r} ({labeled.reason})"
            )
        if labeled.expected_entry_point is not None and result.entry_point != labeled.expected_entry_point:
            mismatches.append(
                f"{labeled.name}: expected entry_point={labeled.expected_entry_point!r}, "
                f"got {result.entry_point!r} ({labeled.reason})"
            )

        failed_cases += len(mismatches) > before

    return failed_cases, mismatches


def test_engine_agrees_with_labeled_reference_suite():
    failed_cases, mismatches = evaluate_cases(LABELED_CASES)
    total = len(LABELED_CASES)
    agreement_rate = (total - failed_cases) / total
    assert not mismatches, (
        f"{failed_cases} disagreeing cases out of {total} "
        f"({len(mismatches)} field mismatches; case agreement {agreement_rate:.0%}):\n"
        + "\n".join(mismatches)
    )


def test_multiple_field_mismatches_count_as_one_failed_case():
    def incorrect_first_case(case):
        result = recommend(case)
        if case is LABELED_CASES[0].case:
            return result.model_copy(update={
                "architecture_pattern": "Agent", "reference_architecture": "Coding agent",
            })
        return result

    failed_cases, details = evaluate_cases(LABELED_CASES, incorrect_first_case)
    assert failed_cases == 1
    assert len(details) == 2
    assert (len(LABELED_CASES) - failed_cases) / len(LABELED_CASES) == 0.95
