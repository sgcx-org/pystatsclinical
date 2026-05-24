"""Treatment-effect measures from a two-arm binary outcome (2x2 readout).

Computes the canonical clinical-trial effect measures for a binary outcome:
control/experimental event rates, absolute and relative risk reduction, the
risk ratio, and the number needed to treat (or harm), each with a confidence
interval.

References
----------
Altman DG. "Confidence intervals for the number needed to treat." BMJ 1998;
317:1309-1312.
Katz D et al. "Obtaining confidence intervals for the risk ratio in cohort
studies." Biometrics 1978; 34:469-474.
Newcombe RG. "Interval estimation for the difference between independent
proportions." Stat Med 1998; 17:873-890.
"""

from __future__ import annotations

import math
from typing import Literal

# scipy supplies only the standard-normal inverse-CDF used for the intervals.
from scipy import stats

from pystatsclinical.effect._common import RiskMeasures


def _validate_arm(events: int, n: int, arm: str) -> None:
    """Validate a single arm's event count and size (fail loud)."""
    if not isinstance(events, int) or isinstance(events, bool):
        raise TypeError(f"{arm}_events must be an int, got {type(events).__name__}")
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(f"{arm}_n must be an int, got {type(n).__name__}")
    if n <= 0:
        raise ValueError(f"{arm}_n must be positive, got {n}")
    if events < 0:
        raise ValueError(f"{arm}_events must be non-negative, got {events}")
    if events > n:
        raise ValueError(
            f"{arm}_events ({events}) cannot exceed {arm}_n ({n})"
        )


def _wilson(x: float, n: float, z: float) -> tuple[float, float]:
    """Wilson score interval for a single proportion."""
    phat = x / n
    denom = 1.0 + z * z / n
    center = phat + z * z / (2.0 * n)
    margin = z * math.sqrt(phat * (1.0 - phat) / n + z * z / (4.0 * n * n))
    return (center - margin) / denom, (center + margin) / denom


def _rd_ci_newcombe(
    cer: float, eer: float, control_n: int, treated_n: int, z: float,
) -> tuple[float, float]:
    """Newcombe hybrid-score CI for the risk difference ARR = CER - EER."""
    l1, u1 = _wilson(cer * control_n, control_n, z)
    l2, u2 = _wilson(eer * treated_n, treated_n, z)
    rd = cer - eer
    lower = rd - math.sqrt((cer - l1) ** 2 + (u2 - eer) ** 2)
    upper = rd + math.sqrt((u1 - cer) ** 2 + (eer - l2) ** 2)
    return lower, upper


def _rd_ci_wald(
    cer: float, eer: float, control_n: int, treated_n: int, z: float,
) -> tuple[float, float]:
    """Wald CI for the risk difference ARR = CER - EER."""
    rd = cer - eer
    se = math.sqrt(
        cer * (1.0 - cer) / control_n + eer * (1.0 - eer) / treated_n
    )
    return rd - z * se, rd + z * se


def _rr_ci_katz(
    treated_events: int, treated_n: int,
    control_events: int, control_n: int,
    rr: float, z: float,
) -> tuple[float, float]:
    """Katz log-method CI for the risk ratio RR = EER / CER.

    SE(log RR) = sqrt(1/a - 1/n1 + 1/c - 1/n2), with a = treated_events,
    n1 = treated_n, c = control_events, n2 = control_n. When the treated arm
    has zero events the log method is undefined, so a Haldane-Anscombe 0.5
    correction is applied to all four cells for the SE only; the RR point
    estimate is left unchanged.
    """
    if rr == 0.0:
        # Treated events are zero -> log(RR) is -inf. Apply 0.5 correction
        # to all four cells of the 2x2 for the interval only.
        a = treated_events + 0.5
        n1 = treated_n + 1.0
        c = control_events + 0.5
        n2 = control_n + 1.0
        rr_for_ci = (a / n1) / (c / n2)
        log_se = math.sqrt(1.0 / a - 1.0 / n1 + 1.0 / c - 1.0 / n2)
        log_rr = math.log(rr_for_ci)
    else:
        log_se = math.sqrt(
            1.0 / treated_events - 1.0 / treated_n
            + 1.0 / control_events - 1.0 / control_n
        )
        log_rr = math.log(rr)
    return math.exp(log_rr - z * log_se), math.exp(log_rr + z * log_se)


def _nnt_ci(
    arr: float, arr_lower: float, arr_upper: float,
) -> tuple[tuple[float, float], bool]:
    """NNT CI by inverting the ARR CI (Altman 1998).

    Returns the (lower, upper) NNT interval and whether the ARR CI spans zero.
    When it spans zero the NNT is unbounded above; the interval is reported as
    (point estimate, inf).
    """
    nnt = 1.0 / abs(arr) if arr != 0.0 else math.inf
    if arr_lower > 0.0:
        return (1.0 / arr_upper, 1.0 / arr_lower), False
    if arr_upper < 0.0:
        return (1.0 / abs(arr_lower), 1.0 / abs(arr_upper)), False
    return (nnt, math.inf), True


def risk_measures(
    treated_events: int,
    treated_n: int,
    control_events: int,
    control_n: int,
    *,
    conf_level: float = 0.95,
    rd_method: Literal["newcombe", "wald"] = "newcombe",
) -> RiskMeasures:
    """Treatment-effect measures for a binary outcome from a two-arm trial.

    Parameters
    ----------
    treated_events, treated_n : int
        Number of events and total subjects in the experimental (treated) arm.
    control_events, control_n : int
        Number of events and total subjects in the control arm.
    conf_level : float
        Confidence level for all intervals. Must be in (0, 1).
    rd_method : {'newcombe', 'wald'}
        CI method for the risk difference (ARR). 'newcombe' (default) is the
        hybrid-score method and has better coverage; 'wald' is the simple
        normal-approximation interval.

    Returns
    -------
    RiskMeasures
        CER, EER, ARR (+CI), RR (+CI), RRR, and NNT/NNH (+CI).

    Raises
    ------
    TypeError
        If any count is not an int.
    ValueError
        If a count is negative, events exceed the arm size, an arm is empty,
        conf_level is out of range, rd_method is unknown, or CER = 0 (the risk
        ratio is undefined).
    """
    if not 0.0 < conf_level < 1.0:
        raise ValueError(f"conf_level must be in (0, 1), got {conf_level}")
    if rd_method not in ("newcombe", "wald"):
        raise ValueError(
            f"rd_method must be 'newcombe' or 'wald', got {rd_method!r}"
        )
    _validate_arm(treated_events, treated_n, "treated")
    _validate_arm(control_events, control_n, "control")

    cer = control_events / control_n
    eer = treated_events / treated_n
    if cer == 0.0:
        raise ValueError(
            "control event rate (CER) is 0; the risk ratio is undefined"
        )

    arr = cer - eer
    rr = eer / cer
    rrr = 1.0 - rr

    z = float(stats.norm.ppf((1.0 + conf_level) / 2.0))

    if rd_method == "newcombe":
        arr_lower, arr_upper = _rd_ci_newcombe(cer, eer, control_n, treated_n, z)
    else:
        arr_lower, arr_upper = _rd_ci_wald(cer, eer, control_n, treated_n, z)

    rr_lower, rr_upper = _rr_ci_katz(
        treated_events, treated_n, control_events, control_n, rr, z
    )
    nnt_ci, spans_null = _nnt_ci(arr, arr_lower, arr_upper)

    return RiskMeasures(
        cer=cer,
        eer=eer,
        arr=arr,
        arr_ci=(arr_lower, arr_upper),
        rr=rr,
        rr_ci=(rr_lower, rr_upper),
        rrr=rrr,
        nnt=1.0 / abs(arr) if arr != 0.0 else math.inf,
        nnt_ci=nnt_ci,
        is_harm=arr < 0.0,
        ci_spans_null=spans_null,
        conf_level=conf_level,
        rd_method=rd_method,
    )
