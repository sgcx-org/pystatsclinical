# First Features — pystatsclinical

This package is currently a **reserved `0.0.1` skeleton**. This file specifies the
first 1–2 features a future session should implement to turn it into a real
`0.1.0` (the "harden later" step of SGC-Bio roadmap item B-3).

## Ground rules (read first)

- **Stay in this layer.** Only implement things that are genuinely *clinical*
  (clinical-trial / clinical-research). General statistics belong in
  `pystatistics`; biotech/pharma methods in `pystatsbio`. Apply the
  "which-of-the-4-layers" test before adding anything. If a function isn't
  specifically clinical, it does NOT go here.
- **Build on `pystatistics`** for the general statistical layer (CIs, tests);
  don't reimplement general stats. Add `pystatistics` as a dependency when the
  first feature needs it.
- **Follow `pystatsbio`'s conventions** — same packaging (hatchling), the Coding
  Bible (`CLAUDE.md` there: fail loud, one job per module, tests first,
  deterministic), typed, ruff/mypy clean.
- **Ship with tests** (normal / edge / failure) and bump to `0.1.0` via the
  release flow once landed.

## Feature 1 (primary): treatment-effect measures from a 2×2

The canonical clinical-trial readout for a binary outcome.

- Suggested API: `risk_measures(treated_events, treated_n, control_events,
  control_n, *, conf_level=0.95) -> RiskMeasures`
- Compute:
  - CER (control event rate), EER (experimental event rate)
  - **ARR** = CER − EER (absolute risk reduction)
  - **RR** = EER / CER, **RRR** = 1 − RR
  - **NNT** = 1 / ARR (report NNH when ARR < 0)
  - Confidence intervals: risk-difference CI (Newcombe or Wald) → CI for NNT
    (Altman 1998); RR CI via the Katz log method.
- Result object fields: `cer, eer, arr, arr_ci, rr, rr_ci, rrr, nnt, nnt_ci,
  summary`.
- Failure behavior (fail loud): reject negative counts, events > n, empty arms,
  and CER = 0 (RR undefined) with explicit errors.
- References: Altman DG, "Confidence intervals for the number needed to treat,"
  BMJ 1998; Katz log method for RR CIs.
- Tests: a textbook 2×2 with known ARR/RR/NNT; ARR-sign / NNH path; the
  failure cases above.

## Feature 2 (optional secondary): responder analysis

- Suggested API: `responder_analysis(values, threshold, *, direction=">=",
  conf_level=0.95) -> ResponderResult`
- Proportion of subjects meeting a clinical response threshold, with a Wilson CI.
- Note: the *proportion CI* itself is general stats — prefer calling
  `pystatistics` for it; the clinical contribution here is the responder framing
  (threshold/direction → responder rate).
