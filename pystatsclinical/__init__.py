"""
PyStatsClinical: Clinical-trial and clinical-research statistical computing.

Part of the PyStatistics open-core ecosystem (alongside ``pystatistics`` and
``pystatsbio``). Provides clinical-specific methods built on the general
statistical layer.

Usage:
    from pystatsclinical import effect
    result = effect.risk_measures(15, 100, 30, 100)
"""

__version__ = "0.1.1"
__author__ = "Hai-Shuo"
__email__ = "contact@sgcx.org"

from pystatsclinical import effect

__all__ = [
    "__version__",
    "effect",
]
