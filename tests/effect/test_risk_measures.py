"""Tests for effect.risk_measures: normal, edge, and failure cases."""

import math

import pytest

from pystatsclinical import effect


# ---------------------------------------------------------------------------
# Normal cases
# ---------------------------------------------------------------------------

def test_textbook_point_estimates():
    # CER = 30/100 = 0.30, EER = 15/100 = 0.15
    r = effect.risk_measures(15, 100, 30, 100)
    assert r.cer == pytest.approx(0.30)
    assert r.eer == pytest.approx(0.15)
    assert r.arr == pytest.approx(0.15)
    assert r.rr == pytest.approx(0.5)
    assert r.rrr == pytest.approx(0.5)
    assert r.nnt == pytest.approx(1.0 / 0.15)
    assert r.is_harm is False
    assert r.label == "NNT"


def test_katz_rr_ci_matches_hand_computation():
    # SE(log RR) = sqrt(1/15 - 1/100 + 1/30 - 1/100) = sqrt(0.08)
    r = effect.risk_measures(15, 100, 30, 100)
    assert r.rr_ci[0] == pytest.approx(0.28717, abs=1e-4)
    assert r.rr_ci[1] == pytest.approx(0.87042, abs=1e-4)


def test_wald_rd_and_nnt_ci_match_hand_computation():
    r = effect.risk_measures(15, 100, 30, 100, rd_method="wald")
    # ARR = 0.15, SE = sqrt(0.3*0.7/100 + 0.15*0.85/100) = 0.0580947
    assert r.arr_ci[0] == pytest.approx(0.036136, abs=1e-5)
    assert r.arr_ci[1] == pytest.approx(0.263864, abs=1e-5)
    # NNT CI is the inverted, sorted ARR CI
    assert r.nnt_ci[0] == pytest.approx(1.0 / 0.263864, abs=1e-3)
    assert r.nnt_ci[1] == pytest.approx(1.0 / 0.036136, abs=1e-3)
    assert r.ci_spans_null is False


def test_newcombe_default_brackets_point_estimate():
    r = effect.risk_measures(15, 100, 30, 100)
    assert r.rd_method == "newcombe"
    assert r.arr_ci[0] < r.arr < r.arr_ci[1]
    assert r.arr_ci[0] > 0  # significant benefit
    assert math.isfinite(r.nnt_ci[0]) and math.isfinite(r.nnt_ci[1])


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_harm_path_reports_nnh():
    # Treated arm worse than control -> ARR < 0 -> NNH
    r = effect.risk_measures(30, 100, 15, 100)
    assert r.arr == pytest.approx(-0.15)
    assert r.rr == pytest.approx(2.0)
    assert r.is_harm is True
    assert r.label == "NNH"
    assert r.nnt == pytest.approx(1.0 / 0.15)


def test_zero_treated_events_rr_zero_with_finite_ci():
    # EER = 0 -> RR = 0, RRR = 1; CI uses continuity correction, stays finite.
    r = effect.risk_measures(0, 100, 20, 100)
    assert r.rr == 0.0
    assert r.rrr == 1.0
    assert math.isfinite(r.rr_ci[0]) and math.isfinite(r.rr_ci[1])
    assert r.rr_ci[0] >= 0.0


def test_non_significant_ci_spans_null():
    # Nearly identical arms -> ARR CI straddles zero -> unbounded NNT CI.
    r = effect.risk_measures(50, 100, 51, 100)
    assert r.arr_ci[0] < 0 < r.arr_ci[1]
    assert r.ci_spans_null is True
    assert r.nnt_ci[1] == math.inf


def test_summary_is_string():
    r = effect.risk_measures(15, 100, 30, 100)
    assert isinstance(r.summary(), str)
    assert "ARR" in r.summary()


# ---------------------------------------------------------------------------
# Failure cases
# ---------------------------------------------------------------------------

def test_events_exceed_n_raises():
    with pytest.raises(ValueError, match="cannot exceed"):
        effect.risk_measures(150, 100, 30, 100)


def test_negative_count_raises():
    with pytest.raises(ValueError, match="non-negative"):
        effect.risk_measures(-1, 100, 30, 100)


def test_empty_arm_raises():
    with pytest.raises(ValueError, match="must be positive"):
        effect.risk_measures(0, 0, 30, 100)


def test_zero_cer_raises():
    with pytest.raises(ValueError, match="undefined"):
        effect.risk_measures(10, 100, 0, 100)


def test_bad_conf_level_raises():
    with pytest.raises(ValueError, match="conf_level"):
        effect.risk_measures(15, 100, 30, 100, conf_level=1.5)


def test_bad_rd_method_raises():
    with pytest.raises(ValueError, match="rd_method"):
        effect.risk_measures(15, 100, 30, 100, rd_method="bogus")


def test_non_int_count_raises():
    with pytest.raises(TypeError):
        effect.risk_measures(15.0, 100, 30, 100)
