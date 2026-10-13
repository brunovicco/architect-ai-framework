"""Deterministic sensitivity analysis over `engine.recommend()`.

For a given case, flips each boolean field on `ArchitectureCase` one at a
time and reports which flips change the recommendation - turning the
engine's output into a discussion instrument ("what would need to be
different for this answer to change?") instead of a single opaque verdict.

Pure and deterministic, like `engine.py`: no I/O, no model/LLM call, no
randomness. Kept as its own module rather than folded into `engine.py`
since it's a meta-analysis over `recommend()`, not a new decision rule.
"""

from dataclasses import dataclass

from .engine import recommend
from .models import ArchitectureCase, Recommendation

TRACKED_FIELDS: tuple[str, ...] = (
    "architecture_pattern",
    "reference_architecture",
    "entry_point",
    "integration_pattern",
    "review_placement",
    "feasibility_verdict",
)

FLIPPABLE_FIELDS: tuple[str, ...] = tuple(
    name for name, info in ArchitectureCase.model_fields.items()
    if info.annotation is bool
)


@dataclass(frozen=True)
class SensitivityFinding:
    """One `ArchitectureCase` field whose flip changes the recommendation.

    Attributes:
        field: The `ArchitectureCase` boolean field that was flipped.
        flipped_to: The value `field` was flipped to.
        changes: The `Recommendation` fields that changed as a result, each
            as (field name, old value, new value).
        warnings: All warnings for the hypothetical alternative, including conflicts.
        resolved_warnings: Baseline warnings no longer present in the alternative.
    """

    field: str
    flipped_to: bool
    changes: tuple[tuple[str, str, str], ...]
    warnings: tuple[str, ...] = ()
    resolved_warnings: tuple[str, ...] = ()


def analyze_sensitivity(
    case: ArchitectureCase, baseline: Recommendation | None = None
) -> list[SensitivityFinding]:
    """Flip each flippable boolean on `case` and report which flips change
    the recommendation.

    Args:
        case: The case to analyze. Never mutated.
        baseline: `recommend(case)`, if the caller already computed it (so
            this doesn't redundantly recompute it); computed internally if
            omitted.

    Returns:
        One `SensitivityFinding` per field whose flip changes at least one
        of `TRACKED_FIELDS` or its warnings, in `FLIPPABLE_FIELDS` order.
    """
    baseline = baseline if baseline is not None else recommend(case)
    findings: list[SensitivityFinding] = []
    for name in FLIPPABLE_FIELDS:
        current = getattr(case, name)
        flipped_case = case.model_copy(update={name: not current})
        flipped = recommend(flipped_case)
        changes = tuple(
            (tracked, getattr(baseline, tracked), getattr(flipped, tracked))
            for tracked in TRACKED_FIELDS
            if getattr(flipped, tracked) != getattr(baseline, tracked)
        )
        resolved = tuple(w for w in baseline.warnings if w not in flipped.warnings)
        if changes or flipped.warnings != baseline.warnings:
            findings.append(SensitivityFinding(
                field=name, flipped_to=not current, changes=changes,
                warnings=tuple(flipped.warnings), resolved_warnings=resolved,
            ))
    return findings
