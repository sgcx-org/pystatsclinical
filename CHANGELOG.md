# Changelog

## 0.2.0

### Added

- **`responder.responder_rate(values, threshold, *, direction, conf_level=0.95,
  correct=False)`** — new `pystatsclinical.responder` module. Dichotomizes a
  continuous or ordinal trial outcome into responder / non-responder against a
  pre-specified threshold and direction, and reports the responder rate with a
  confidence interval. Returns a `ResponderRateSolution` exposing
  `.n_responders`, `.n_total`, `.n_non_responders`, `.rate`, `.rate_ci`,
  `.criterion`, and `summary()`.
  - `direction` is a **required keyword** (`'ge'`, `'gt'`, `'le'`, `'lt'`).
    There is no universally correct direction — larger-is-better and
    smaller-is-better outcomes are both routine — so the function refuses to
    guess rather than silently deciding the analysis.
  - `correct` defaults to **`False`** (uncorrected Wilson score interval),
    deliberately differing from R's `prop.test()` default of `TRUE`. The
    responder rate is an estimation task rather than a test against a null,
    where Yates' continuity correction is over-conservative (Newcombe 1998);
    and the uncorrected interval is the same Wilson interval that underpins the
    Newcombe risk-difference interval in `effect.risk_measures`, so one
    proportion-interval convention now holds across the package. Pass
    `correct=True` for parity with R.
  - NaN values raise rather than being silently dropped: how missing outcomes
    are handled (non-responder imputation, LOCF, complete cases) is a protocol
    decision that changes the result. Impute or exclude before calling.
  - The confidence interval itself is not implemented here — it is delegated to
    `pystatistics.hypothesis.prop_test`.

### Changed (breaking)

- **`effect.RiskMeasures` is renamed `effect.RiskMeasuresSolution`** and is no
  longer a bare dataclass. It now wraps a frozen `RiskMeasuresParams` payload
  and exposes the same result metadata as the rest of the PyStatistics
  ecosystem: `.backend_name` (`'cpu'`), `.timing`, `.warnings`, `.info`, plus
  `summary()` and a Jupyter `_repr_html_`. Every measure remains available
  under its existing name (`.cer`, `.eer`, `.arr`, `.arr_ci`, `.rr`, `.rr_ci`,
  `.rrr`, `.nnt`, `.nnt_ci`, `.is_harm`, `.ci_spans_null`, `.conf_level`,
  `.rd_method`, `.label`), so only the type name and construction change.
  `RiskMeasuresParams` is exported for callers who want the raw payload.
  There is no deprecation shim — the package is pre-1.0.

- **`effect.risk_measures` now raises `pystatistics.core.exceptions.ValidationError`**
  instead of bare `ValueError` / `TypeError` for every input-validation failure
  (non-integer counts, negative counts, events exceeding arm size, empty arm,
  out-of-range `conf_level`, unknown `rd_method`, and CER = 0). `ValidationError`
  subclasses `ValueError`, so existing `except ValueError` handlers keep working;
  code catching `TypeError` for non-integer counts must be updated.

- **`effect.risk_measures` now reports non-fatal conditions via `.warnings`**
  rather than only implying them through the returned values. Two cases are
  surfaced and echoed in `summary()`: the Haldane-Anscombe 0.5 correction
  applied to the risk-ratio interval when the treated arm has zero events, and
  an ARR interval that includes zero (leaving the NNT/NNH interval unbounded
  above).

### Dependencies

- **Added a hard dependency on `pystatistics>=5.1`.** The package previously
  declared only numpy and scipy despite the ecosystem result and exception
  types now being required at import time.

### Internal

- Added a mypy override so `scipy.*` missing stubs no longer error under
  `strict`. The `scipy-stubs` package is not usable here — it requires
  PEP 695 `type` statements (Python >= 3.12) while this project targets 3.11.


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
