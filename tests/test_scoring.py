"""Tests for the weighted trade-off scoring in `architect.scoring`."""

from architect.scoring import DEFAULT_WEIGHTS, normalized_score


def test_full_score_is_one():
    """A perfect 5/5 on every criterion normalizes to 1.0."""
    scores = {key: 5 for key in DEFAULT_WEIGHTS}
    assert normalized_score(scores) == 1.0


def test_mid_score_is_point_six():
    """A flat 3/5 on every criterion normalizes to 0.6."""
    scores = {key: 3 for key in DEFAULT_WEIGHTS}
    assert normalized_score(scores) == 0.6
