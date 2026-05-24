"""Result type for treatment-effect measures from a 2x2 clinical readout."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskMeasures:
    """Treatment-effect measures for a binary outcome from a two-arm trial.

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

    @property
    def label(self) -> str:
        """'NNT' when the treatment is beneficial, 'NNH' when harmful."""
        return "NNH" if self.is_harm else "NNT"

    def summary(self) -> str:
        """Human-readable summary of all measures."""
        pct = f"{self.conf_level:.0%}"
        lines = [
            "Treatment-Effect Measures (2x2)",
            "=" * 50,
            f"CER (control)      : {self.cer:.4f}",
            f"EER (treated)      : {self.eer:.4f}",
            f"ARR                : {self.arr:.4f} "
            f"({pct} CI: {self.arr_ci[0]:.4f}–{self.arr_ci[1]:.4f}) "
            f"[{self.rd_method}]",
            f"RR                 : {self.rr:.4f} "
            f"({pct} CI: {self.rr_ci[0]:.4f}–{self.rr_ci[1]:.4f}) [Katz]",
            f"RRR                : {self.rrr:.4f}",
            f"{self.label:<19}: {self.nnt:.2f} "
            f"({pct} CI: {self.nnt_ci[0]:.2f}–{self.nnt_ci[1]:.2f})",
        ]
        return "\n".join(lines)
