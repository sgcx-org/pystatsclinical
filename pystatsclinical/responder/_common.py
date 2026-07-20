"""Result types for responder analysis.

Follows the same Params/Solution split as ``effect/_common.py`` (CONVENTIONS
C1): the computed outputs live in a frozen ``ResponderRateParams`` payload and
the public return ``ResponderRateSolution`` wraps a
``core.result.Result[ResponderRateParams]``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pystatistics.core.result import Result, SolutionReprMixin


@dataclass(frozen=True)
class ResponderRateParams:
    """Computed responder rate for a single arm.

    Attributes
    ----------
    n_responders : int
        Number of subjects meeting the responder criterion.
    n_total : int
        Number of subjects evaluated (after any exclusions by the caller).
    rate : float
        Responder rate = n_responders / n_total.
    rate_ci : tuple of float
        Confidence interval for the responder rate (lower, upper), from
        ``pystatistics.hypothesis.prop_test``.
    threshold : float
        The responder threshold applied to the outcome values.
    direction : str
        Comparison used to classify a responder: 'ge', 'gt', 'le', or 'lt'.
    conf_level : float
        Confidence level used for the interval.
    correct : bool
        Whether Yates' continuity correction was applied to the interval.
    """

    n_responders: int
    n_total: int
    rate: float
    rate_ci: tuple[float, float]
    threshold: float
    direction: str
    conf_level: float
    correct: bool


class ResponderRateSolution(SolutionReprMixin):
    """Public result of ``responder_rate`` — wraps ``Result[ResponderRateParams]``.

    Exposes every output as a read-only property plus the uniform
    ``.backend_name`` / ``.timing`` / ``.warnings`` / ``.info`` metadata and a
    Jupyter ``_repr_html_`` (via :class:`SolutionReprMixin`).
    """

    def __init__(self, result: Result[ResponderRateParams]) -> None:
        self._result = result

    # --- Metadata (from the Result envelope) ---
    @property
    def backend_name(self) -> str:
        return self._result.backend_name

    @property
    def timing(self) -> dict[str, float] | None:
        return self._result.timing

    @property
    def warnings(self) -> tuple[str, ...]:
        return self._result.warnings

    @property
    def info(self) -> dict[str, Any]:
        return self._result.info

    # --- Outputs (from the payload) ---
    @property
    def n_responders(self) -> int:
        return self._result.params.n_responders

    @property
    def n_total(self) -> int:
        return self._result.params.n_total

    @property
    def n_non_responders(self) -> int:
        """Number of subjects not meeting the responder criterion."""
        p = self._result.params
        return p.n_total - p.n_responders

    @property
    def rate(self) -> float:
        return self._result.params.rate

    @property
    def rate_ci(self) -> tuple[float, float]:
        return self._result.params.rate_ci

    @property
    def threshold(self) -> float:
        return self._result.params.threshold

    @property
    def direction(self) -> str:
        return self._result.params.direction

    @property
    def conf_level(self) -> float:
        return self._result.params.conf_level

    @property
    def correct(self) -> bool:
        return self._result.params.correct

    @property
    def criterion(self) -> str:
        """Human-readable responder rule, e.g. 'value >= 50'."""
        symbol = {"ge": ">=", "gt": ">", "le": "<=", "lt": "<"}[self.direction]
        return f"value {symbol} {self.threshold:g}"

    def summary(self) -> str:
        """Human-readable summary of the responder analysis."""
        p = self._result.params
        pct = f"{p.conf_level:.0%}"
        method = "Wilson score" + (", continuity-corrected" if p.correct else "")
        lines = [
            "Responder Analysis",
            "=" * 50,
            f"Criterion          : {self.criterion}",
            f"Responders         : {p.n_responders} / {p.n_total}",
            f"Responder rate     : {p.rate:.4f} "
            f"({pct} CI: {p.rate_ci[0]:.4f}–{p.rate_ci[1]:.4f}) [{method}]",
        ]
        lines.extend(f"Note: {w}" for w in self.warnings)
        return "\n".join(lines)

    def __repr__(self) -> str:
        p = self._result.params
        return (
            f"ResponderRateSolution(rate={p.rate:.4f}, "
            f"{p.n_responders}/{p.n_total})"
        )
