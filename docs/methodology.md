# Project Nurture methodology

## Scope and data tiers

Project Nurture has two deliberately different analysis contexts. The local
research tier (T1) calculates survey-weighted indicators from a user-supplied
DHS Household Member Recode and may show displaced, restricted-local cluster
aggregates. The committed public demo tier (T2) contains only documented
placeholder district values and synthetic clusters. The public demo values are
not authoritative NFHS estimates.

## Child population and sample weighting

The `dhs-nutrition` implementation first restricts the PR recode to de facto
children (`hv103 == 1`) aged 0–59 completed months (`hc1` from 0 through 59,
inclusive). Each retained child's analysis weight is `hv005 / 1,000,000`.

For a weighted prevalence, the numerator is the sum of sample weights for
children who meet the indicator definition and the denominator is the sum of
sample weights for children with a valid measurement for that indicator. The
reported rate is `100 × numerator / denominator`. A zero denominator produces
no value rather than zero prevalence.

## Measurement validity and indicator definitions

The DHS anthropometry variables store z-scores multiplied by 100. HAZ (`hc70`),
WAZ (`hc71`), and WHZ (`hc72`) are separately valid when they are non-null and
less than the DHS sentinel boundary `9990`. A child can therefore contribute to
one anthropometric denominator and not another.

- Stunting is valid HAZ below −200 (−2 SD); severe stunting is below −300
  (−3 SD).
- Underweight is valid WAZ below −200; severe underweight is below −300.
- Wasting is valid WHZ below −200; severe wasting is below −300.
- Overweight is valid WHZ above +200 (+2 SD).
- Anemia eligibility requires selection for hemoglobin testing (`hv042 == 1`),
  age 6–59 months inclusive, an obtained measurement (`hc55 == 0`), and a coded
  anemia category `hc57` in `{1, 2, 3, 4}`. Among eligible children, anemia is
  `hc57` in `{1, 2, 3}` and severe anemia is `hc57 == 1`. The adjusted
  hemoglobin value `hc56` is not used in these categorical rules.

Weighted mean HAZ, WAZ, and WHZ use the valid population for the corresponding
z-score. The implementation sums `(stored z-score × sample weight)`, divides by
the valid-weight denominator, and then divides by 100 to return z-score units.
A zero denominator produces no mean.

## Phase 4 district percentile risk

The Phase 4 district composite reads only the committed T2
`project_nurture/public/demo/district_indicators.json`. For each of stunting,
underweight, and wasting, it performs the following calculation across all
included demo districts:

1. Sort conceptually from lower to higher prevalence and assign one-based
   average ranks. Tied values receive the average of the positions they occupy.
2. Map the observed average ranks to 0–100 with
   `100 × (rank − minimum rank) / (maximum rank − minimum rank)`. The observed
   minimum maps to exactly 0 and the observed maximum to exactly 100, including
   tied endpoint groups. If every district has the same value, every district
   receives the neutral percentile 50 because no ordering exists.
3. Calculate `0.45 × stunting percentile + 0.35 × underweight percentile +
   0.20 × wasting percentile`.

For example, values `[10, 20, 20, 40]` have average ranks
`[1, 2.5, 2.5, 4]` and percentiles `[0, 50, 50, 100]`.

The default weights are a transparent planning choice, not fitted coefficients:
stunting receives the greatest emphasis as the chronic-growth component,
underweight receives the next-largest share as a broader low-weight component,
and wasting receives a smaller but explicit acute-nutrition share. CLI weights
must be finite, non-negative, and sum to 1 within an absolute tolerance of
`1e-9`.

The artifact contains six sensitivity scenarios. Each component weight is
changed by −0.1 and +0.1 in turn, then all three weights are divided by their new
sum. A negative boundary is clipped to zero so otherwise valid custom CLI
weights remain usable; clipping is not reached by the defaults. Ranking
stability is the Spearman correlation between baseline and perturbed composite
scores. Spearman ranks use average tie ranks. If either ranking has zero
variance, the correlation is undefined and is stored as `null`.

### District and cluster scores are intentionally different

Public district choropleths and profile records replace the older raw-rate
`risk_score` in `district_indicators.json` with the Phase 4 percentile composite
from `district_risk.json`. Public state and national profile risk values are
unweighted means of the available district percentile composites.

Cluster, heat, priority, and local research-mode views continue to calculate
`0.45 × stunting rate + 0.35 × underweight rate + 0.20 × wasting rate` from
their filtered survey-weighted rates. They are not percentile-ranked against
the ten demo districts. This preserves research-mode behavior while preventing
the older district raw-rate score from being mislabeled as the Phase 4 district
composite.

## Limitations and responsible interpretation

- DHS and NFHS survey associations are cross-sectional and are not evidence of
  causal effects.
- Committed demo district values are placeholders, not authoritative NFHS
  estimates.
- Demo clusters and their coordinates are synthetic and do not represent real
  survey clusters or children.
- District percentile risk is relative only to the districts included in the
  current demo artifact. It is not an absolute clinical or program threshold,
  and it will change when the included districts or values change.
- Results are planning aids for exploration and prioritization, not diagnoses
  of a child, district, or population.
- The composite omits uncertainty intervals, survey-design variance, temporal
  change, service access, food security, morbidity, and other relevant context.

## Implementation audit trail

This document was checked against the following implementation locations on
2026-07-21:

- `packages/dhs-nutrition/src/dhs_nutrition/loaders.py`, lines 85–114: PR
  loading and the de facto 0–59-month filter.
- `packages/dhs-nutrition/src/dhs_nutrition/indicators.py`, lines 54–120:
  sample weights, validity gates, indicator numerators, and weighted z-score
  sums; lines 174–206: weighted rates and weighted mean z-scores.
- `python_backend/analytics/risk_methodology.py`, lines 35–44 and 61–166:
  components, default weights, validation tolerance, percentile/tie rules,
  Spearman behavior, and sensitivity perturbations; lines 169–244: input
  validation, component percentiles, composite scores, and output schema;
  lines 247–263: deterministic serialization and manifest registration.
- `project_nurture/src/lib/nutritionData.js`, lines 188–217: the existing
  filtered cluster/research weighted-rate composite retained by Phase 4.
- `project_nurture/src/lib/districtRisk.js`, lines 1–53: public district risk
  overlay and unweighted state/national district-composite rollups.

Line references describe the Phase 4 implementation at the time this document
was added and should be refreshed when those files change materially.
