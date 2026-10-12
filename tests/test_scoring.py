from arquiteto.scoring import DEFAULT_WEIGHTS, normalized_score


def test_full_score_is_one():
    scores = {key: 5 for key in DEFAULT_WEIGHTS}
    assert normalized_score(scores) == 1.0


def test_mid_score_is_point_six():
    scores = {key: 3 for key in DEFAULT_WEIGHTS}
    assert normalized_score(scores) == 0.6
