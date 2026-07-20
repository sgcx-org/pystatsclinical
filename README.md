# PyStatsClinical

**Clinical-trial and clinical-research statistical computing for Python.**

> **Status: `0.2.0` — early but usable.** Treatment-effect measures and
> responder analysis are available now; more clinical-research methods are on
> the roadmap below.

PyStatsClinical is part of the open-core PyStatistics family:

| Package | Layer |
|---|---|
| [`pystatistics`](https://github.com/sgcx-org/pystatistics) | Fundamental, general statistics |
| [`pystatsbio`](https://github.com/sgcx-org/pystatsbio) | Biotech / pharma statistics |
| **`pystatsclinical`** | Clinical-trial / clinical-research statistics |
| [`pystatsgenomic`](https://github.com/sgcx-org/pystatsgenomic) | Genomics / computational-biology statistics |
| [`pystatsfinance`](https://github.com/sgcx-org/pystatsfinance) | Financial / quantitative statistics |
| [`pystatsinsurance`](https://github.com/sgcx-org/pystatsinsurance) | Actuarial / insurance statistics |

Like its siblings, it builds on `pystatistics` for the general statistical layer
and adds methods specific to clinical research.

## What's available now

### Treatment-effect measures from a two-arm 2×2

The canonical readout for a binary outcome:

```python
from pystatsclinical import effect

r = effect.risk_measures(
    treated_events=15, treated_n=100,
    control_events=30, control_n=100,
)
print(r.summary())
```

`risk_measures` reports the control and experimental event rates (CER, EER),
the absolute risk reduction (ARR) with a Newcombe or Wald confidence interval,
the risk ratio (RR) with the Katz log-method interval, the relative risk
reduction (RRR), and the number needed to treat / harm (NNT/NNH) with the
Altman (1998) interval. It fails loud on invalid counts and on an undefined risk
ratio (CER = 0).

### Responder analysis

Turn a continuous or ordinal outcome into a responder rate using a
pre-specified threshold:

```python
from pystatsclinical import responder

changes = [55.0, 62.0, 41.0, 78.0, 50.0, 12.0]
r = responder.responder_rate(changes, threshold=50.0, direction="ge")
print(r.summary())
print(r.n_responders, "of", r.n_total)
```

`direction` is required — `"ge"` / `"gt"` when larger values are better (e.g.
at least 50% improvement) and `"le"` / `"lt"` when smaller values are better
(e.g. a pain score of 3 or less). There is no safe default, so the function
asks rather than guessing.

The interval defaults to the uncorrected Wilson score interval
(`correct=False`); pass `correct=True` for Yates' continuity correction, which
matches R's `prop.test()` default. Missing (NaN) outcomes raise rather than
being dropped, since the choice of imputation rule changes the result — impute
or exclude before calling.

### Result objects

Every analysis returns a `…Solution` object with a uniform surface: the
computed measures as attributes, plus `summary()` for a printable report,
`.warnings` for non-fatal issues worth reporting alongside the numbers,
`.info` for the method settings used, and a rich display in Jupyter.

## Roadmap (candidates, not commitments)

- Non-inferiority / equivalence analysis at readout time.
- Restricted mean survival time (RMST) and difference-in-RMST.
- Adverse-event analysis: exposure-adjusted incidence and per-arm comparison.
- Group-sequential / interim analysis with alpha-spending boundaries.

Diagnostic accuracy, epidemiological 2×2 measures, Mantel–Haenszel, and trial
sample-size/power live in [`pystatsbio`](https://github.com/sgcx-org/pystatsbio)
and are intentionally not duplicated here.

## Installation

```bash
pip install pystatsclinical
```

## License

MIT © Hai-Shuo. Part of the [SGCX](https://sgcx.org) open-core ecosystem.
