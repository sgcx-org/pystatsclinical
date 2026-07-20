# PyStatsClinical Conventions (adopt-and-extend)

This document governs the **pystatsclinical public API**. It does not restate the
law from scratch — it **adopts the pystatistics constitution as binding** and adds
a small set of clinical-specific amendments (C-series) for this library's domain
(treatment-effect measures, trial readouts, diagnostic accuracy, clinical
epidemiology).

## 0. Adoption

The binding base is **`pystatistics/CONVENTIONS.md`**. Everything in it applies
to pystatsclinical verbatim: the naming law S0–S6, the selector taxonomy, the
backend & precision convention, the result-object conventions
(`…Solution` wrapping `Result[…Params]`, `core.result.SolutionReprMixin`), the
exception conventions, and amendments **A1–A15**.

**A15 is the load-bearing amendment for this package.** Clinical methods are
overwhelmingly *framing over general statistics* — the domain contribution is the
effect measure, the trial design, and the interpretation, not the estimation. The
underlying intervals, tests, and survival machinery come from PyStatistics.

When this document and the base disagree, **this document wins for
pystatsclinical**; where this document is silent, the base governs. Like the base,
this document is **self-amending**: a new ambiguity is resolved once, here, as a
numbered amendment (C-series), not re-litigated per occurrence.

Reuse, don't fork: pystatsclinical imports `pystatistics.core.exceptions`,
`pystatistics.core.result`, and `pystatistics.core.compute.backend` rather than
defining its own parallels. One hierarchy across the ecosystem.

---

## pystatsclinical amendments (C-series)

### C1 — Every public return is a `…Solution`

`RiskMeasures` (`effect/_common.py`) is currently a bare frozen dataclass with a
hand-rolled `summary()`. It becomes **`RiskMeasuresSolution`**, wrapping a frozen
`RiskMeasuresParams` payload in `core.result.Result` and exposing the uniform
metadata accessors (`.backend_name`, `.timing`, `.warnings`, `.info`), `summary()`,
and `_repr_html_` via `SolutionReprMixin`. The existing `summary()` text folds
into the envelope rather than being replaced. CPU-only results report
`backend_name='cpu'`.

Nested `{estimate, ci}` value objects that appear as *fields* of a Solution stay
lightweight frozen dataclasses — the envelope is for top-level public returns.

### C2 — Exceptions come from `pystatistics.core.exceptions`

No bare `raise ValueError` / `raise TypeError` for validation. The current
`effect/_risk_measures.py` raises six `ValueError` and two `TypeError`; all become
`ValidationError`. Iterative non-convergence (when any arrives) →
`ConvergenceError`. Domain-specific exceptions subclass the correct base, never
`ValueError` directly.

### C3 — Dependency peg

`pyproject.toml` currently declares **no `pystatistics` dependency at all** (only
numpy and scipy) — the package cannot honor A15 without it. It declares
**`pystatistics>=5.1`**.

### C4 — What delegates, and what is genuinely clinical (A15 applied)

Delegates upstream:

- **Proportion inference** — `hypothesis.prop_test`. The single-proportion Wilson
  helper `_wilson` in `effect/_risk_measures.py` overlaps it; prefer the upstream
  primitive where it can return the bounds the composition needs.
- **Restricted mean survival time (RMST)** and any survival readout — `survival`
  (Kaplan–Meier), never a local KM.
- **Multiple-testing correction** — `hypothesis.p_adjust`.

Stays local — the clinical contribution:

- The **Newcombe** hybrid-score risk-difference interval, the **Katz** log risk-ratio
  interval, and the **Altman** NNT interval derived by inverting the ARR CI. These
  are clinical compositions *built on* proportion inference, not a general
  estimator wearing a clinical hat.
- NNT/NNH sign bookkeeping, responder framing, non-inferiority margin logic.

Not a violation: `scipy.stats.norm.ppf` for a z-quantile (A15).

**TOST** is a promotion candidate, not local work: the two-one-sided-tests engine
is generic equivalence testing used by both clinical non-inferiority and
bioequivalence. It goes upstream, with clinical wrappers here.

### C5 — The pystatsbio boundary (RULED — do not re-litigate)

`pystatsbio` is, in practice, already the clinical-trial statistics package: it
ships trial design and power (`power_superiority_mean`, `power_noninf_mean`,
`power_noninf_prop`, `power_equiv_mean`, `power_crossover_be`, `power_logrank`,
`power_cluster`, and more), diagnostic accuracy, epidemiological measures,
standardization, Mantel–Haenszel, and meta-analysis. Its own keywords include
`clinical-trials`.

**Ruling:** the bio/clinical distinction is an *audience and presentation*
boundary, not a computational one. A biostatistician and a clinician computing an
NNT run identical arithmetic; what differs is vocabulary, defaults, and framing —
which belongs in the **application** layer (SGC-Clinical), not in a second
statistics library. Therefore:

1. **Nothing here duplicates pystatsbio.** The following are **not built in this
   package** — they exist upstream and stay there:

   | Capability | Lives in |
   |---|---|
   | Diagnostic accuracy, ROC/AUC, optimal cutoff | `pystatsbio.diagnostic` |
   | 2×2 epi measures (RR/OR/RD, AFe, PAF) | `pystatsbio.epi.epi_2by2` |
   | Standardization, SMR/SIR (person-time) | `pystatsbio.epi.rate_standardize` |
   | Mantel–Haenszel pooled OR/RR, CMH | `pystatsbio.epi.mantel_haenszel` |
   | Meta-analysis, Q / I² / τ² | `pystatsbio.meta` |
   | Trial sample size & power (all designs) | `pystatsbio.power` |
   | Bioequivalence design/power (PK) | `pystatsbio.power_crossover_be` |

2. **Nothing promotes to PyStatistics.** Risk ratios, odds ratios, NNT and
   attributable fractions are *epidemiology*, not general statistics — a quant or
   a physicist never computes them. A15's promotion clause covers a **general**
   mechanic; a mechanic shared by two *health* domains is not one. Pushing epi
   vocabulary into the base library would dilute its identity (base Rule 8
   corollary: *"X involves statistics, therefore X belongs in pystatistics"* is
   not a valid reasoning chain).

3. **No dependency on pystatsbio.** The genuinely-clinical set below leans on
   `pystatistics` (survival, proportions) or is self-contained. A consuming
   application imports both libraries; this package does not.

**What is genuinely clinical, and therefore in scope here** — the trial-readout
layer that has no upstream equivalent:

- Two-arm **treatment-effect measures** with trial framing (CER/EER, ARR, RRR,
  NNT/NNH with Altman intervals) — *shipped*
- **Responder analysis** (threshold/direction → responder rate)
- **Non-inferiority / equivalence *analysis*** — margin tests and TOST at analysis
  time. Distinct from `pystatsbio.power`, which sizes such trials but does not
  analyze them.
- **Restricted mean survival time (RMST)** and difference-in-RMST
- **Adverse-event analysis** — exposure-adjusted incidence, per-arm comparison
- **Group-sequential / interim analysis** — alpha-spending boundaries

**On the one overlap that already ships:** `risk_measures` computes RR and a risk
difference that `pystatsbio.epi.epi_2by2` also computes. This is deliberate and
stays — and the justification is stronger than framing alone: **the two functions
track different reference standards.**

- `epi_2by2` declares *"Validates against: R `epiR::epi.2by2()`"* and therefore
  uses epiR's methods — a **Wald** risk-difference interval and a log RR interval.
- `risk_measures` tracks the clinical-trial literature — **Newcombe** (1998)
  hybrid-score for the risk difference, **Katz** for RR, and **Altman** (1998) for
  the NNT interval by inversion.

Neither is wrong; each is faithful to the reference its audience expects. Do
**not** "fix" one to match the other — changing `epi_2by2`'s intervals would break
its R parity, which is a core promise of that package. Two reference lineages for
two audiences is precisely why these packages are separate rather than merged.

### C6 — First-pass scope discipline

The first pass implements **Tier 1 of `ROADMAP.md` only**. Items in the roadmap's
*"Ambiguous — discuss before building"* section stay parked and are not decided by
implementation. Sample-size/power in particular has an unsettled home and is not
built here on a session's initiative.
