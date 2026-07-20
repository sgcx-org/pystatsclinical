"""Responder analysis: threshold + direction -> responder rate with an interval.

A responder analysis dichotomizes a continuous or ordinal trial outcome (a
change from baseline, a symptom score, a percent reduction) into responder /
non-responder using a pre-specified threshold, then reports the responder rate
with a confidence interval.

The clinical contribution here is only the *framing* — the threshold-and-
direction bookkeeping that turns outcome values into counts. The proportion
interval itself is delegated upstream to
``pystatistics.hypothesis.prop_test`` (CONVENTIONS A15/C4); no interval is
implemented in this module.
"""

from __future__ import annotations

import math
from typing import Any, Literal

import numpy as np
from pystatistics.core.exceptions import ValidationError
from pystatistics.core.result import Result
from pystatistics.hypothesis import prop_test

from pystatsclinical.responder._common import ResponderRateParams, ResponderRateSolution

Direction = Literal["ge", "gt", "le", "lt"]

_DIRECTIONS: dict[str, Any] = {
    "ge": np.greater_equal,
    "gt": np.greater,
    "le": np.less_equal,
    "lt": np.less,
}


def responder_rate(
    values: Any,
    threshold: float,
    *,
    direction: Direction,
    conf_level: float = 0.95,
    correct: bool = False,
) -> ResponderRateSolution:
    """Responder rate for one arm, from outcome values and a response threshold.

    Parameters
    ----------
    values : array-like of float
        Outcome value per subject (e.g. change from baseline, percent
        reduction, final score). Must be one-dimensional and non-empty, and
        must not contain NaN — see Raises.
    threshold : float
        The pre-specified response threshold.
    direction : {'ge', 'gt', 'le', 'lt'}
        How a value is compared against the threshold to count as a response.
        Use 'ge'/'gt' when larger values are better (e.g. >= 50% improvement)
        and 'le'/'lt' when smaller values are better (e.g. pain score <= 3).
        Required — there is no universally correct direction, and guessing one
        would silently decide the analysis.
    conf_level : float
        Confidence level for the responder-rate interval. Must be in (0, 1).
    correct : bool
        Whether to apply Yates' continuity correction to the interval.
        Defaults to **False**, deliberately diverging from the
        ``pystatistics.hypothesis.prop_test`` default of ``True``. Two reasons:
        the responder rate is an estimation task rather than a test against a
        null, where the continuity-corrected interval is over-conservative
        (Newcombe 1998); and the uncorrected interval is the Wilson score
        interval that already underpins the Newcombe risk-difference interval
        in :func:`pystatsclinical.effect.risk_measures`, so one proportion-
        interval convention holds across this package. Pass ``correct=True``
        for parity with R's ``prop.test()`` default.

    Returns
    -------
    ResponderRateSolution
        Responder counts and rate with its interval, plus the uniform
        ``.backend_name`` / ``.timing`` / ``.warnings`` / ``.info`` metadata
        and ``summary()``.

    Raises
    ------
    ValidationError
        If ``values`` is empty, not one-dimensional, non-numeric, or contains
        NaN; if ``threshold`` is not finite; if ``direction`` is unknown; or if
        ``conf_level`` is outside (0, 1).

    Notes
    -----
    NaN values raise rather than being dropped. How missing outcomes are
    handled in a responder analysis (non-responder imputation, LOCF, complete
    cases) is a protocol decision that changes the result, so this function
    refuses to make it silently — impute or exclude before calling.

    Examples
    --------
    >>> from pystatsclinical import responder
    >>> changes = [55.0, 62.0, 41.0, 78.0, 50.0, 12.0]
    >>> r = responder.responder_rate(changes, 50.0, direction="ge")
    >>> r.n_responders
    4
    """
    if direction not in _DIRECTIONS:
        raise ValidationError(
            f"direction must be one of 'ge', 'gt', 'le', 'lt', got {direction!r}"
        )
    if not 0.0 < conf_level < 1.0:
        raise ValidationError(f"conf_level must be in (0, 1), got {conf_level}")
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool):
        raise ValidationError(
            f"threshold must be a real number, got {type(threshold).__name__}"
        )
    if not math.isfinite(threshold):
        raise ValidationError(f"threshold must be finite, got {threshold}")

    try:
        arr = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"values must be numeric array-like: {exc}") from exc

    if arr.ndim != 1:
        raise ValidationError(
            f"values must be one-dimensional, got {arr.ndim} dimensions"
        )
    if arr.size == 0:
        raise ValidationError("values must be non-empty")
    if np.isnan(arr).any():
        n_nan = int(np.isnan(arr).sum())
        raise ValidationError(
            f"values contains {n_nan} NaN value(s); responder analysis requires "
            "an explicit missing-data rule (e.g. non-responder imputation) — "
            "impute or exclude before calling"
        )

    n_total = int(arr.size)
    n_responders = int(_DIRECTIONS[direction](arr, threshold).sum())

    # A15/C4: the proportion interval is delegated, never implemented here.
    upstream = prop_test(
        n_responders, n_total, conf_level=conf_level, correct=correct
    )
    conf_int = upstream.conf_int
    if conf_int is None:
        # Defensive: prop_test types conf_int as optional. Every call this
        # module makes requests an interval, so None means the upstream
        # contract changed — fail loud rather than emit a fabricated interval.
        raise ValidationError(
            "pystatistics.hypothesis.prop_test returned no confidence interval "
            f"for {n_responders}/{n_total} at conf_level={conf_level}"
        )
    lower, upper = (float(v) for v in conf_int)

    warnings: list[str] = []
    if n_responders == 0:
        warnings.append("no subject met the responder criterion")
    elif n_responders == n_total:
        warnings.append("every subject met the responder criterion")

    params = ResponderRateParams(
        n_responders=n_responders,
        n_total=n_total,
        rate=n_responders / n_total,
        rate_ci=(lower, upper),
        threshold=float(threshold),
        direction=direction,
        conf_level=conf_level,
        correct=correct,
    )
    result = Result(
        params=params,
        info={
            "method": "responder_rate",
            "conf_level": conf_level,
            "direction": direction,
            "threshold": float(threshold),
            "ci_method": "prop_test",
            "continuity_correction": correct,
        },
        timing=None,
        backend_name="cpu",
        warnings=tuple(warnings),
    )
    return ResponderRateSolution(result)
