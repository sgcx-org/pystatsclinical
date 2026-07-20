"""Responder analysis for clinical trial outcomes.

Dichotomizes a continuous or ordinal outcome into responder / non-responder
against a pre-specified threshold and direction, and reports the responder
rate with a confidence interval.

The proportion interval is delegated to ``pystatistics.hypothesis.prop_test``;
this module contributes only the clinical responder framing.
"""

from pystatsclinical.responder._common import (
    ResponderRateParams,
    ResponderRateSolution,
)
from pystatsclinical.responder._responder_rate import responder_rate

__all__ = [
    "ResponderRateParams",
    "ResponderRateSolution",
    "responder_rate",
]
