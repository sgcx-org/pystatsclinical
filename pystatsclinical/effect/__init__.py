"""Treatment-effect measures for clinical trials.

Effect measures for a binary outcome from a two-arm trial: control and
experimental event rates, absolute and relative risk reduction, risk ratio,
and number needed to treat / harm, each with a confidence interval.

Validates against: R epiR / textbook worked examples (Altman 1998).
"""

from pystatsclinical.effect._common import RiskMeasuresParams, RiskMeasuresSolution
from pystatsclinical.effect._risk_measures import risk_measures

__all__ = [
    "RiskMeasuresParams",
    "RiskMeasuresSolution",
    "risk_measures",
]
