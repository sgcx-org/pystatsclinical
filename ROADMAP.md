# Roadmap — pystatsclinical

A working **checklist** of features that belong at the *clinical trial readout*
layer. Tick items off as they land.

**This list is not a commitment.** It captures *what kind of thing belongs here*
and roughly in what order we'd build it. Tiers are priority bands, not deadlines.

## Scope (read this before adding anything)

This package is **deliberately small**. `pystatsbio` is already, in practice, the
clinical-trial statistics library — it owns trial design and power, diagnostic
accuracy, epidemiological measures, standardization, Mantel–Haenszel, and
meta-analysis. The bio/clinical split is an *audience* boundary, not a
computational one, and it is served at the application layer (SGC-Clinical), not
by reimplementing statistics here.

The binding rules are in **[`pystatsclinical/CONVENTIONS.md`](pystatsclinical/CONVENTIONS.md)**,
which adopts the PyStatistics constitution (including **A15** — domain packages
delegate general estimation upstream). **C5 is the one to read before adding a
roadmap item**: it lists what lives in `pystatsbio` and is therefore out of scope
here, and it is a ruling, not an open question.

Quick test for a new item: *does `pystatsbio` or `pystatistics` already do this?*
If yes, it does not go here. If it's a general estimator, it comes from
`pystatistics`. What's left — the two-arm trial readout, framed for a clinical
audience — is this package.

## Tier 1 — core trial readouts

- [x] **Treatment-effect measures from a 2×2** — CER/EER, ARR, RR, RRR, NNT/NNH
  with Newcombe/Katz/Altman intervals. *Shipped in 0.1.0.*
- [x] **Responder analysis** — threshold/direction → responder rate, with the
  proportion interval delegated to `pystatistics.hypothesis.prop_test`.
  *Shipped in 0.2.0 as `responder.responder_rate`.*

  **Ruled:** the responder rate reports the **uncorrected** interval by default
  (`correct=False`, diverging from `prop_test`'s `correct=True`), exposed in the
  signature. Rationale: estimation rather than testing against a null, where
  Yates' correction is over-conservative (Newcombe 1998); and the uncorrected
  interval is the same Wilson interval already underpinning the Newcombe
  risk-difference interval in `effect.risk_measures`, so one proportion-interval
  convention holds package-wide.

  **Note for future work:** `prop_test(...).estimate` is a *dict* (`{'p': ...}`),
  not a bare float as recorded here previously, and `.conf_int` is an ndarray
  typed as optional. `responder_rate` reads `.conf_int` and computes the rate
  itself, so the discrepancy does not affect it.

## Tier 2 — analysis-time trial machinery

- [ ] **Non-inferiority / equivalence analysis** — NI margin tests and TOST for
  differences of proportions and means, with the margin-and-direction bookkeeping
  that makes it clinical. *Distinct from `pystatsbio.power`, which sizes these
  trials but does not analyze them — confirm the boundary when building.*
- [ ] **Restricted mean survival time (RMST)** — RMST and difference-in-RMST
  between arms, consuming `pystatistics.survival` (Kaplan–Meier). Never a local KM.
- [ ] **Adverse-event analysis** — exposure-adjusted incidence rates, AE incidence
  proportions with intervals, per-arm comparison.

## Tier 3 — interim analysis

- [ ] **Group-sequential / interim analysis** — alpha-spending
  (O'Brien–Fleming, Pocock), boundary computation. No upstream equivalent.

## Open questions (decide before building, do not resolve by writing code)

- **TOST core** — the two-one-sided-tests engine is *generic* equivalence testing,
  unlike the epi measures. It is a legitimate promotion candidate for
  `pystatistics.hypothesis`, with a clinical NI wrapper here. Decide the home
  before implementing the Tier-2 NI item.
- **Cohen's / weighted kappa, rater ICC** — inter-rater agreement. Neither
  `pystatsbio` nor `pystatistics` ships it, so it is genuinely unclaimed; but it
  is arguably general categorical agreement rather than clinical. Decide the home.
- **Bioequivalence analysis** — TOST on log-transformed PK parameters. `pystatsbio`
  owns PK/NCA *and* the BE design power (`power_crossover_be`), so the analysis
  most likely belongs there too, next to the data it consumes. Leaning bio; confirm
  before anyone builds it here.

## Explicitly out of scope

Do not add these; they ship in `pystatsbio` (see CONVENTIONS C5 for the table):
diagnostic accuracy and ROC/AUC, 2×2 epidemiological measures, standardization and
SMR, Mantel–Haenszel and CMH, meta-analysis, and trial sample-size/power for every
design.
