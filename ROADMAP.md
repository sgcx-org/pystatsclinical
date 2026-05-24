# Roadmap — pystatsclinical

A working **checklist** of features that plausibly belong at the *clinical*
layer (clinical-trial / clinical-research / clinical-epidemiology). Tick items
off as they land, in roughly the way `pystatistics/docs/ROADMAP.md` tracks its
modules.

**This list is not a commitment.** It exists to capture *what kind of thing
belongs here* and in roughly what order we'd build it. We can re-order, drop, or
promote/demote items freely. Tiers are priority bands, not deadlines.

## Layer rules (the gate every item must pass)

- **Stay in this layer.** Only genuinely *clinical* methods. General statistics
  (tests, CIs, regression, survival fitting) live in `pystatistics`;
  biotech/pharma-lab methods in `pystatsbio`. Apply the
  "which-of-the-4-layers" test before adding anything.
- **Build on `pystatistics`** (CIs, proportions, KM/Cox, GLM) — don't
  reimplement general stats. The clinical contribution is the *framing*
  (effect measures, trial designs, diagnostic readouts), not the machinery.
- **Promotion rule:** if a mechanic is shared by ≥2 separate domains (e.g. TOST
  equivalence used by both clinical and finance), it's a candidate to promote to
  `pystatistics` rather than live here. See the *Ambiguous* section.
- Conventions: `pystatsbio` Coding Bible (fail loud, one job per module, tests
  first, deterministic), typed, ruff/mypy clean, ship with tests, bump version
  via the release flow.

## Tier 1 — self-contained, unmistakably clinical

- [ ] **Treatment-effect measures from a 2×2** — ARR, RR, RRR, NNT/NNH, OR, with
  CIs (Newcombe/Wald RD → NNT CI; Katz log RR CI). *v0.1.0 target — full spec in
  [FIRST_FEATURES.md](FIRST_FEATURES.md).*
- [ ] **Responder analysis** — threshold/direction → responder rate + Wilson CI
  (CI itself delegated to `pystatistics`). *See FIRST_FEATURES.md.*
- [ ] **Diagnostic test accuracy** — sensitivity, specificity, PPV, NPV,
  positive/negative likelihood ratios, diagnostic OR, with CIs, from a 2×2 of
  test-vs-truth.
- [ ] **Epidemiologic effect measures** — incidence rate, incidence-rate ratio,
  attributable risk / attributable fraction, standardized mortality/morbidity
  ratio (SMR), with CIs.

## Tier 2 — common clinical-trial readouts

- [ ] **Stratified pooled effects** — Mantel–Haenszel pooled OR/RR across strata
  (e.g. multi-center), with heterogeneity check.
- [ ] **Non-inferiority / equivalence framing** — NI margin tests and
  equivalence (TOST) for difference of proportions / means, with the
  margin-and-direction bookkeeping that makes it clinical.
- [ ] **Restricted mean survival time (RMST)** and difference-in-RMST between
  arms (consumes `pystatistics` KM).
- [ ] **Adverse-event analysis** — exposure-adjusted incidence rates, AE
  incidence proportions with CIs, per-arm comparison.

## Tier 3 — heavier / trial-design machinery

- [ ] **Trial sample size & power** — two-proportion, survival (log-rank /
  Schoenfeld), and NI-margin designs. *(Home is ambiguous — see below.)*
- [ ] **Group-sequential / interim analysis** — alpha-spending (O'Brien–Fleming,
  Pocock), boundary computation.
- [ ] **Bioequivalence** — TOST on log-transformed PK parameters (AUC, Cmax),
  90% CI on the geometric-mean ratio. *(Clinical vs pystatsbio — see below.)*
- [ ] **Meta-analysis** — fixed- and random-effects pooling, I²/τ²
  heterogeneity, forest-plot data. *(Home is ambiguous — see below.)*

## Ambiguous — discuss before building

These pass a "clinical-ish" sniff test but may belong elsewhere. Flagging so we
decide deliberately rather than grabbing them.

- **ROC / AUC** — arguably a general classifier-evaluation primitive
  (`pystatistics`?), but "diagnostic ROC" is squarely a clinical readout. Where?
- **Cohen's / weighted kappa, rater ICC** — general categorical-agreement stats?
  Or clinical (inter-rater reliability of clinical assessments)?
- **Cochran–Mantel–Haenszel *test statistic*** — the pooled *effect measure* is
  clinical, but the CMH χ² is a general stratified-categorical test. Split them?
- **TOST core** — the two-one-sided-tests machine is generic equivalence
  testing; clinical NI and bioequivalence both use it. **Promotion candidate**
  for `pystatistics`, with clinical wrappers here.
- **Sample size / power** — general stats, a domain concern, *and* (per SGC-Bio)
  possibly a standalone "Tools" surface. Decide the home before building.
- **Bioequivalence** — clinical-pharmacology; could live in `pystatsbio` (pharma
  lab) instead of clinical-trials. Which?
- **Meta-analysis** — evidence-synthesis; reasonable in `pystatistics` (generic)
  or here (clinical research). Pick one.
