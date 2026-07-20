"""
PyStatsClinical: Clinical-trial and clinical-research statistical computing.

Part of the PyStatistics open-core ecosystem (alongside ``pystatistics`` and
``pystatsbio``). Provides clinical-specific methods built on the general
statistical layer.

Usage:
    from pystatsclinical import effect, responder
    result = effect.risk_measures(15, 100, 30, 100)
    rate = responder.responder_rate(changes, 50.0, direction="ge")
"""

__version__ = "0.2.0"
__author__ = "Hai-Shuo"
__email__ = "contact@sgcx.org"

from pystatsclinical import effect, responder

__all__ = [
    "__version__",
    "effect",
    "responder",
]
