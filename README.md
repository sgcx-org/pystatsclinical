# PyStatsClinical

**Clinical-trial and clinical-research statistical computing for Python.**

> **Status: `0.1.0` — first module shipped.** The treatment-effect module is
> available now; more clinical-research methods are on the roadmap below.

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

## What's available now (0.1.0)

**Treatment-effect measures from a two-arm 2×2** — the canonical readout for a
binary outcome:

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

## Roadmap (candidates, not commitments)

- Responder analysis: responder rate with a confidence interval at a clinical
  threshold.
- Diagnostic accuracy: sensitivity, specificity, predictive values, likelihood
  ratios.
- Non-inferiority / equivalence testing and stratified (Mantel–Haenszel) effects.

## Installation

```bash
pip install pystatsclinical
```

## License

MIT © Hai-Shuo. Part of the [SGCX](https://sgcx.org) open-core ecosystem.
