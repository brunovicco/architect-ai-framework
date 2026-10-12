DEFAULT_WEIGHTS = {
    "Quality / task success": 5,
    "Latency": 4,
    "Cost": 3,
    "Risk / control": 5,
    "Auditability / predictability": 4,
    "Maintainability": 3,
    "Observability / debugging": 3,
    "Privacy / residency / compliance": 5,
    "Portability / lock-in": 3,
    "Fit with hard constraints": 5,
}


def normalized_score(scores: dict[str, int], weights: dict[str, int] | None = None) -> float:
    weights = weights or DEFAULT_WEIGHTS
    numerator = 0
    denominator = 0
    for criterion, weight in weights.items():
        value = scores.get(criterion, 0)
        numerator += weight * value
        denominator += weight * 5
    return numerator / denominator if denominator else 0.0
