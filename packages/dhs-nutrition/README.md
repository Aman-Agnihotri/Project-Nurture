# dhs-nutrition

`dhs-nutrition` computes survey-weighted child nutrition indicators (stunting,
wasting, underweight, overweight, anemia, mean z-scores) from any DHS Program
PR (household member) recode file, at national, admin1, and cluster levels,
with breakdowns by demographic segment (sex, residence, wealth, age band).

## Data responsibility

**This package never bundles, downloads, or redistributes DHS microdata.**
Users must register with the DHS Program and hold their own data-access
agreement before obtaining any PR recode or GPS cluster files. Outputs
derived from restricted microdata must be handled under that same agreement —
do not publish microdata-derived files.

## Install

From PyPI (once published):

```bash
pip install dhs-nutrition
```

From the monorepo:

```bash
pip install -e packages/dhs-nutrition
```

## Quickstart

```python
from dhs_nutrition import VariableMap, load_pr_recode, load_gps_clusters, compute_indicators, validate_against_factsheet

children = load_pr_recode("IAPR7EFL.DTA", variable_map=VariableMap.dhs7())
gps = load_gps_clusters("IAGE7AFL.shp")
result = compute_indicators(children, gps=gps)
result.to_json("nutrition.json", tier="restricted-local")
report = validate_against_factsheet(result, "state_factsheet.csv", level="admin1", tolerance_pp=0.15)
print(report.summary())
```

Admin1 validation requires complete region coverage in both directions; omitted
or unexpected regions fail the report. National validation requires exactly one
factsheet row and accepts the country's normal name in its `region` column.

## Command line

```bash
dhs-nutrition inspect --pr IAPR7EFL.DTA
dhs-nutrition compute --pr IAPR7EFL.DTA --gps IAGE7AFL.shp --out nutrition.json --tier restricted-local
dhs-nutrition validate --result nutrition.json --factsheet state_factsheet.csv --tolerance 0.15
```

## Related tools

- [rdhs](https://github.com/ropensci/rdhs) — R client for the DHS API.
- [DHS.rates](https://cran.r-project.org/package=DHS.rates) — R package for DHS survey indicators.
- [WHO anthro](https://www.who.int/tools/child-growth-standards/software) — WHO child growth standard tools.

This package focuses on Python-native, PR-recode weighted aggregation.

## License

MIT.
