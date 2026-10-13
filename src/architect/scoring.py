"""Weighted trade-off scoring for comparing architecture options.

This module has no opinion on which option should win - it only normalizes
a set of per-criterion scores (1-5) into a single 0-1 figure using a weight
map. Hard constraints are expected to override a high aggregate score; users must manually exclude ineligible options. Neither this function nor
the UI infers eligibility from free-text constraints.
"""

DEFAULT_WEIGHTS = {
    "Quality/task success": 5,
    "Latency": 4,
    "Cost": 3,
    "Risk/control": 5,
    "Auditability/predictability": 4,
    "Maintainability": 3,
    "Observability/debugging": 3,
    "Privacy/residency/compliance": 5,
    "Portability/lock-in": 3,
    "Fit with hard constraints": 5,
}


def normalized_score(scores: dict[str, int], weights: dict[str, int] | None = None) -> float:
    """Compute a weighted, normalized score for one architecture option.

    Args:
        scores: Per-criterion scores (typically 1-5) for a single option,
            keyed by criterion name. A criterion missing from this mapping
            scores 0.
        weights: Per-criterion weights, keyed by the same criterion names.
            Defaults to `DEFAULT_WEIGHTS` when not supplied.

    Returns:
        The weighted score as a fraction of the maximum possible weighted
        score (0.0-1.0), or 0.0 if `weights` is empty.
    """
    weights = weights or DEFAULT_WEIGHTS
    numerator = 0
    denominator = 0
    for criterion, weight in weights.items():
        value = scores.get(criterion, 0)
        numerator += weight * value
        denominator += weight * 5
    return numerator/denominator if denominator else 0.0
