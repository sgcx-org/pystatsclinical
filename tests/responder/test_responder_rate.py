"""Tests for responder.responder_rate: normal, edge, and failure cases."""

import dataclasses

import numpy as np
import pytest
from pystatistics.core.exceptions import ValidationError
from pystatistics.hypothesis import prop_test

from pystatsclinical import responder

CHANGES = [55.0, 62.0, 41.0, 78.0, 50.0, 12.0]


# ---------------------------------------------------------------------------
# Normal cases
# ---------------------------------------------------------------------------

def test_ge_counts_threshold_as_responder():
    # >= 50 -> 55, 62, 78, 50 are responders; 41 and 12 are not.
    r = responder.responder_rate(CHANGES, 50.0, direction="ge")
    assert r.n_responders == 4
    assert r.n_total == 6
    assert r.n_non_responders == 2
    assert r.rate == pytest.approx(4 / 6)


def test_gt_excludes_the_boundary_value():
    # > 50 drops the subject sitting exactly on the threshold.
    r = responder.responder_rate(CHANGES, 50.0, direction="gt")
    assert r.n_responders == 3


def test_le_and_lt_invert_the_direction():
    # Smaller-is-better framing, e.g. a symptom score.
    assert responder.responder_rate(CHANGES, 50.0, direction="le").n_responders == 3
    assert responder.responder_rate(CHANGES, 50.0, direction="lt").n_responders == 2


def test_interval_is_delegated_to_prop_test_uncorrected_by_default():
    r = responder.responder_rate(CHANGES, 50.0, direction="ge")
    expected = prop_test(4, 6, conf_level=0.95, correct=False).conf_int
    assert r.rate_ci[0] == pytest.approx(float(expected[0]))
    assert r.rate_ci[1] == pytest.approx(float(expected[1]))
    assert r.correct is False


def test_correct_true_matches_prop_test_corrected_and_is_wider():
    plain = responder.responder_rate(CHANGES, 50.0, direction="ge")
    corrected = responder.responder_rate(CHANGES, 50.0, direction="ge", correct=True)
    expected = prop_test(4, 6, conf_level=0.95, correct=True).conf_int
    assert corrected.rate_ci[0] == pytest.approx(float(expected[0]))
    assert corrected.rate_ci[1] == pytest.approx(float(expected[1]))
    # Yates' correction is conservative: the corrected interval is wider.
    width = lambda s: s.rate_ci[1] - s.rate_ci[0]  # noqa: E731
    assert width(corrected) > width(plain)


def test_conf_level_is_honoured():
    narrow = responder.responder_rate(CHANGES, 50.0, direction="ge", conf_level=0.80)
    wide = responder.responder_rate(CHANGES, 50.0, direction="ge", conf_level=0.99)
    assert wide.rate_ci[0] < narrow.rate_ci[0]
    assert wide.rate_ci[1] > narrow.rate_ci[1]


def test_accepts_numpy_array_and_ints():
    r = responder.responder_rate(np.array([1, 2, 3, 4]), 3, direction="ge")
    assert r.n_responders == 2


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_zero_responders_gives_rate_zero_and_warns():
    r = responder.responder_rate([1.0, 2.0, 3.0], 100.0, direction="ge")
    assert r.n_responders == 0
    assert r.rate == 0.0
    assert r.rate_ci[0] == pytest.approx(0.0)
    assert any("no subject" in w for w in r.warnings)


def test_all_responders_gives_rate_one_and_warns():
    r = responder.responder_rate([1.0, 2.0, 3.0], 0.0, direction="ge")
    assert r.rate == 1.0
    assert r.rate_ci[1] == pytest.approx(1.0)
    assert any("every subject" in w for w in r.warnings)


def test_single_subject_is_allowed():
    r = responder.responder_rate([5.0], 1.0, direction="ge")
    assert r.n_responders == 1
    assert r.n_total == 1


def test_negative_threshold_works_for_change_from_baseline():
    # A reduction of at least 20 points, encoded as a negative change.
    r = responder.responder_rate([-25.0, -30.0, -5.0, 4.0], -20.0, direction="le")
    assert r.n_responders == 2


def test_criterion_renders_the_clinical_rule():
    r = responder.responder_rate(CHANGES, 50.0, direction="ge")
    assert r.criterion == "value >= 50"
    assert responder.responder_rate(CHANGES, 3.5, direction="lt").criterion == (
        "value < 3.5"
    )


# ---------------------------------------------------------------------------
# Solution envelope (CONVENTIONS C1)
# ---------------------------------------------------------------------------

def test_returns_solution_with_uniform_metadata():
    r = responder.responder_rate(CHANGES, 50.0, direction="ge")
    assert isinstance(r, responder.ResponderRateSolution)
    assert r.backend_name == "cpu"
    assert r.timing is None
    assert isinstance(r.warnings, tuple)
    assert r.info["method"] == "responder_rate"
    assert r.info["continuity_correction"] is False
    assert r.info["direction"] == "ge"


def test_summary_and_repr_html():
    r = responder.responder_rate(CHANGES, 50.0, direction="ge")
    text = r.summary()
    assert "Responder Analysis" in text
    assert "Wilson score" in text
    assert r._repr_html_().startswith("<pre>")


def test_params_payload_is_frozen():
    r = responder.responder_rate(CHANGES, 50.0, direction="ge")
    params = r._result.params
    assert isinstance(params, responder.ResponderRateParams)
    with pytest.raises(dataclasses.FrozenInstanceError):
        params.rate = 0.99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Failure cases
# ---------------------------------------------------------------------------

def test_missing_direction_is_a_type_error_not_a_silent_default():
    # direction is keyword-only and required — guessing it would decide the
    # analysis silently.
    with pytest.raises(TypeError):
        responder.responder_rate(CHANGES, 50.0)  # type: ignore[call-arg]


def test_unknown_direction_raises():
    with pytest.raises(ValidationError, match="direction"):
        responder.responder_rate(CHANGES, 50.0, direction="above")  # type: ignore[arg-type]


def test_empty_values_raises():
    with pytest.raises(ValidationError, match="non-empty"):
        responder.responder_rate([], 50.0, direction="ge")


def test_nan_raises_rather_than_being_dropped():
    with pytest.raises(ValidationError, match="NaN"):
        responder.responder_rate([1.0, float("nan"), 3.0], 2.0, direction="ge")


def test_two_dimensional_values_raise():
    with pytest.raises(ValidationError, match="one-dimensional"):
        responder.responder_rate([[1.0, 2.0], [3.0, 4.0]], 2.0, direction="ge")


def test_non_numeric_values_raise():
    with pytest.raises(ValidationError, match="numeric"):
        responder.responder_rate(["a", "b"], 2.0, direction="ge")


def test_bad_conf_level_raises():
    with pytest.raises(ValidationError, match="conf_level"):
        responder.responder_rate(CHANGES, 50.0, direction="ge", conf_level=1.5)


def test_non_finite_threshold_raises():
    with pytest.raises(ValidationError, match="finite"):
        responder.responder_rate(CHANGES, float("inf"), direction="ge")


def test_non_numeric_threshold_raises():
    with pytest.raises(ValidationError, match="real number"):
        responder.responder_rate(CHANGES, "50", direction="ge")  # type: ignore[arg-type]
