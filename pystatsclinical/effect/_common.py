"""Result types for treatment-effect measures from a 2x2 clinical readout.

The computed outputs live in a frozen ``RiskMeasuresParams`` payload; the
public return is ``RiskMeasuresSolution``, which wraps a
``core.result.Result[RiskMeasuresParams]`` so every clinical result exposes the
same ``.backend_name`` / ``.timing`` / ``.warnings`` / ``.info`` metadata and
Jupyter ``_repr_html_`` as the rest of the ecosystem (CONVENTIONS C1).

Split convention (the reference implementation for the sibling packages):
anything the Solution promises as a *typed* property lives in ``Params``.
``info`` mirrors the method-identifying subset for uniform, cross-package
introspection and is never the sole home of anything the public API promises —
so a caller never has to reach into an untyped dict to read a documented value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pystatistics.core.result import Result, SolutionReprMixin


@dataclass(frozen=True)
class RiskMeasuresParams:
    """Computed treatment-effect measures for a binary outcome, two-arm trial.

    All rates are event rates (probability of the event of interest). The
    event is whatever the trial counts (e.g. death, relapse); when the event
    is undesirable, a positive ``arr`` means the treatment is beneficial.

    Attributes
    ----------
    cer : float
        Control event rate = control_events / control_n.
    eer : float
        Experimental (treated) event rate = treated_events / treated_n.
    arr : float
        Absolute risk reduction = CER - EER. Positive when the treated arm
        has fewer events than control.
    arr_ci : tuple of float
        Confidence interval for the ARR (lower, upper).
    rr : float
        Risk ratio = EER / CER.
    rr_ci : tuple of float
        Confidence interval for the RR (lower, upper), Katz log method.
    rrr : float
        Relative risk reduction = 1 - RR.
    nnt : float
        Number needed to treat = 1 / |ARR|. When ``arr`` is negative this is
        the number needed to harm (see ``is_harm``).
    nnt_ci : tuple of float
        Confidence interval for the NNT, derived from the ARR CI (Altman 1998).
        When the ARR CI spans zero the interval is unbounded above and
        reported as (point estimate, inf); see ``ci_spans_null``.
    is_harm : bool
        True when ARR < 0, i.e. the figure is a number needed to harm (NNH).
    ci_spans_null : bool
        True when the ARR CI includes zero (no significant difference); in
        that case the NNT CI is not a simple finite interval.
    conf_level : float
        Confidence level used for all intervals.
    rd_method : str
        Method used for the risk-difference (ARR) CI: 'newcombe' or 'wald'.
    """

    cer: float
    eer: float
    arr: float
    arr_ci: tuple[float, float]
    rr: float
    rr_ci: tuple[float, float]
    rrr: float
    nnt: float
    nnt_ci: tuple[float, float]
    is_harm: bool
    ci_spans_null: bool
    conf_level: float
    rd_method: str


class RiskMeasuresSolution(SolutionReprMixin):
    """Public result of ``risk_measures`` — wraps ``Result[RiskMeasuresParams]``.

    Exposes every measure as a read-only property plus the uniform
    ``.backend_name`` / ``.timing`` / ``.warnings`` / ``.info`` metadata and a
    Jupyter ``_repr_html_`` (via :class:`SolutionReprMixin`).
    """

    def __init__(self, result: Result[RiskMeasuresParams]) -> None:
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

    # --- Measures (from the payload) ---
    @property
    def cer(self) -> float:
        return self._result.params.cer

    @property
    def eer(self) -> float:
        return self._result.params.eer

    @property
    def arr(self) -> float:
        return self._result.params.arr

    @property
    def arr_ci(self) -> tuple[float, float]:
        return self._result.params.arr_ci

    @property
    def rr(self) -> float:
        return self._result.params.rr

    @property
    def rr_ci(self) -> tuple[float, float]:
        return self._result.params.rr_ci

    @property
    def rrr(self) -> float:
        return self._result.params.rrr

    @property
    def nnt(self) -> float:
        return self._result.params.nnt

    @property
    def nnt_ci(self) -> tuple[float, float]:
        return self._result.params.nnt_ci

    @property
    def is_harm(self) -> bool:
        return self._result.params.is_harm

    @property
    def ci_spans_null(self) -> bool:
        return self._result.params.ci_spans_null

    @property
    def conf_level(self) -> float:
        return self._result.params.conf_level

    @property
    def rd_method(self) -> str:
        return self._result.params.rd_method

    @property
    def label(self) -> str:
        """'NNT' when the treatment is beneficial, 'NNH' when harmful."""
        return "NNH" if self.is_harm else "NNT"

    def summary(self) -> str:
        """Human-readable summary of all measures."""
        p = self._result.params
        pct = f"{p.conf_level:.0%}"
        lines = [
            "Treatment-Effect Measures (2x2)",
            "=" * 50,
            f"CER (control)      : {p.cer:.4f}",
            f"EER (treated)      : {p.eer:.4f}",
            f"ARR                : {p.arr:.4f} "
            f"({pct} CI: {p.arr_ci[0]:.4f}–{p.arr_ci[1]:.4f}) "
            f"[{p.rd_method}]",
            f"RR                 : {p.rr:.4f} "
            f"({pct} CI: {p.rr_ci[0]:.4f}–{p.rr_ci[1]:.4f}) [Katz]",
            f"RRR                : {p.rrr:.4f}",
            f"{self.label:<19}: {p.nnt:.2f} "
            f"({pct} CI: {p.nnt_ci[0]:.2f}–{p.nnt_ci[1]:.2f})",
        ]
        lines.extend(f"Note: {w}" for w in self.warnings)
        return "\n".join(lines)

    def __repr__(self) -> str:
        p = self._result.params
        return (
            f"RiskMeasuresSolution(ARR={p.arr:.4f}, RR={p.rr:.4f}, "
            f"{self.label}={p.nnt:.2f})"
        )
