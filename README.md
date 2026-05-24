# PyStatsClinical

**Clinical-trial and clinical-research statistical computing for Python.**

> **Status: early / reserved (`0.0.1`).** This package reserves the
> `pystatsclinical` name within the **PyStatistics open-core ecosystem** and will
> grow into a full clinical-research statistics library. The public API is
> forthcoming.

PyStatsClinical is part of the open-core PyStatistics family:

| Package | Layer |
|---|---|
| [`pystatistics`](https://github.com/sgcx-org/pystatistics) | Fundamental, general statistics |
| [`pystatsbio`](https://github.com/sgcx-org/pystatsbio) | Biotech / pharma statistics |
| **`pystatsclinical`** | Clinical-trial / clinical-research statistics |

Like its siblings, it builds on `pystatistics` for the general statistical layer
and adds methods specific to clinical research.

## Planned scope (candidates, not commitments)

- Treatment-effect readouts from a 2×2: number-needed-to-treat (NNT),
  absolute/relative risk reduction.
- Responder analysis: responder rate with confidence interval at a clinical
  threshold.
- Clinical-trial missing-data helpers (e.g. LOCF / BOCF imputation).

## Installation

```bash
pip install pystatsclinical
```

## License

MIT © Hai-Shuo. Part of the [SGCX](https://sgcx.org) open-core ecosystem.
