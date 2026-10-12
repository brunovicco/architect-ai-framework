"""Tests for the bilingual string tables in `architect.i18n`."""

from architect.i18n import LANGS, MODEL_CRITERIA, t


def test_model_criteria_has_nine_entries_including_explainability():
    """The model/provider comparison matrix has 9 criteria, including the
    explainability/fairness-auditability one added alongside the structural
    criteria (quality, latency, cost, context, structured output, privacy,
    rate limits, portability).
    """
    assert len(MODEL_CRITERIA) == 9
    assert "model_criterion_explainability_label" in MODEL_CRITERIA


def test_every_model_criterion_resolves_in_both_languages():
    """Every MODEL_CRITERIA key has a non-empty label in each supported language."""
    for key in MODEL_CRITERIA:
        for lang in LANGS:
            label = t(lang, key)
            assert label, f"{key} has no label for {lang}"
