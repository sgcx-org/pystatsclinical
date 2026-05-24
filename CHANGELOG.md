# Changelog

## 0.1.1

### Documentation
- Expanded the README to document the treatment-effect module
  (`effect.risk_measures`) with a usage example, and to list the full
  PyStatistics open-core ecosystem.


## 0.1.0

### Added
- `effect` subpackage with `effect.risk_measures(...)`: treatment-effect
  measures for a binary outcome from a two-arm trial — control/experimental
  event rates (CER/EER), absolute risk reduction (ARR) with a Newcombe or Wald
  confidence interval, risk ratio (RR) with the Katz log-method interval,
  relative risk reduction (RRR), and number needed to treat / harm (NNT/NNH)
  with the Altman (1998) interval. Fails loud on invalid counts and an
  undefined risk ratio (CER = 0).

First feature release, promoting the package from a reserved skeleton.
