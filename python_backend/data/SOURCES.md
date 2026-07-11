# Data Sources — `python_backend/data/`

## Placeholder status

The values in `nfhs5_district_factsheet.csv` are **PLACEHOLDERS (sentinels)**,
not real-world estimates. All indicator values are obviously-round numbers
chosen only to exercise the demo pipeline (e.g. map rendering, cluster
synthesis, dashboard summaries). District names are literal placeholders
(`Demo District B1`, `Demo District M2`, etc.) and do not correspond to real
administrative districts.

Before this demo can be treated as representing published statistics, the
maintainer must transcribe official NFHS-5 district fact-sheet values,
row by row, replacing every placeholder with a sourced figure.

## Citation template

When transcribing real values, cite each district fact sheet using this
template:

```
IIPS and ICF. National Family Health Survey (NFHS-5), 2019-21: District Fact Sheet, <District>, <State>. Mumbai: IIPS. <URL>. Accessed <YYYY-MM-DD>.
```

## Centroid coordinates

The `centroid_lat` / `centroid_lon` values in the CSV are approximate,
demo-only inputs used to place synthetic clusters on the map. They are
**not** survey coordinates and do not represent verified district centroids.
Replace them with accurate district centroid coordinates from an authoritative
geographic source when moving beyond the demo tier.

## Data tier note

This folder (`python_backend/data/`) is tier **T2** (public/demo inputs).
Never place NFHS-5 microdata, DHS microdata, or any content from `dhs_data/`
in this folder.
