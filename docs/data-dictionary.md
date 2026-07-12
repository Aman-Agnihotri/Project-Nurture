# Project Nurture data dictionary

## Scope and data tiers

This document defines schema version `1.0` emitted by
`dhs_nutrition.result.IndicatorResult.to_json`. It describes structure and
field meaning only; it does not contain DHS microdata or real survey-derived
values.

- **Restricted-local (T1):** outputs generated from a user's DHS PR recode and
  GPS files. Never commit or redistribute these files.
- **Public/demo (T2):** published aggregates and clearly labelled synthetic
  clusters. The Phase 1 demo artifact remains in the legacy schema until its
  planned regeneration.

The frontend feature-detects `schema_version: "1.0"` and normalizes this schema
to its legacy in-memory dashboard shape.

## Top-level object

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `schema_version` | string | yes | Literal `"1.0"`. |
| `tier` | string | yes | Data-handling tier supplied by the caller, normally `restricted-local`. |
| `generated_at` | ISO-8601 string | yes | UTC generation time; deterministic when `SOURCE_DATE_EPOCH` is set. |
| `package_version` | string | yes | Version of `dhs-nutrition` that wrote the file. |
| `source_files` | object | yes | Input basenames mapped to lowercase SHA-256 digests. Paths are never stored. A GPS shapefile records the consumed `.shp`, `.shx`, and `.dbf` components separately. |
| `levels` | object | yes | Requested national, admin1, and/or cluster indicator tables. |
| `segments` | object | yes | Requested breakdown tables represented as column arrays plus positional rows. |
| `meta` | object | no | Caller-supplied non-sensitive metadata. The India consumer uses the fields described below. |

All floating-point values are rounded to six decimal places. NaN and positive
or negative infinity are serialized as JSON `null`. Object keys are sorted for
deterministic output.

## Indicator fields

These fields occur on each object in `levels`. Rates are percentages in the
range 0–100 or `null` when the relevant weighted denominator is zero. Mean
z-scores are in z-score units, not the recode's ×100 storage units.

| Field | Type | Definition |
|---|---|---|
| `child_count` | integer | Unweighted number of de-facto children aged 0–59 months. |
| `haz_valid_n` | integer | Children with a non-null HAZ value below the DHS `9990` sentinel boundary. |
| `waz_valid_n` | integer | Children with a non-null WAZ value below `9990`. |
| `whz_valid_n` | integer | Children with a non-null WHZ value below `9990`. |
| `anemia_valid_n` | integer | Children aged 6–59 months selected and measured for hemoglobin with anemia category 1–4. |
| `stunting_rate` | number/null | Weighted percentage with HAZ < −2.00. |
| `severe_stunting_rate` | number/null | Weighted percentage with HAZ < −3.00. |
| `underweight_rate` | number/null | Weighted percentage with WAZ < −2.00. |
| `severe_underweight_rate` | number/null | Weighted percentage with WAZ < −3.00. |
| `wasting_rate` | number/null | Weighted percentage with WHZ < −2.00. |
| `severe_wasting_rate` | number/null | Weighted percentage with WHZ < −3.00. |
| `overweight_rate` | number/null | Weighted percentage with WHZ > 2.00. |
| `anemia_rate` | number/null | Weighted percentage with anemia category 1, 2, or 3 among anemia-valid children. |
| `severe_anemia_rate` | number/null | Weighted percentage with anemia category 1 among anemia-valid children. |
| `mean_haz` | number/null | Weighted mean height-for-age z-score. |
| `mean_waz` | number/null | Weighted mean weight-for-age z-score. |
| `mean_whz` | number/null | Weighted mean weight-for-height z-score. |

Weights use the DHS household sample weight divided by 1,000,000. Exact recode
variables come from the active `VariableMap`; the DHS-7 defaults are documented
in the package README and indicator module.

## `levels`

### `levels.national`

A single object containing only the indicator fields above.

### `levels.admin1`

An array of objects containing all indicator fields plus:

| Field | Type | Meaning |
|---|---|---|
| `admin1_code` | integer | DHS admin1/state/region code from the PR recode. |
| `admin1_name` | string/null | Value label associated with `admin1_code`. |

### `levels.cluster`

An array of mapped survey-cluster objects. PR clusters without a usable GPS
record are omitted.

| Field | Type | Meaning |
|---|---|---|
| `cluster_id` | integer | DHS cluster number used to join PR and GPS inputs. |
| `dhs_id` | string | GPS dataset cluster identifier. |
| `admin1_code` | integer | Admin1 code from the GPS file. |
| `admin1_name` | string/null | Admin1 name from the GPS file. |
| `admin2_name` | string/null | DHS region/district label from the GPS file. |
| `residence` | string | `Urban` or `Rural` from the GPS file. |
| `latitude` | number | DHS-displaced cluster latitude. |
| `longitude` | number | DHS-displaced cluster longitude. |

The remaining fields are the indicator fields listed above. Altitude and raw
GPS attributes are deliberately not exported.

## `segments`

Each requested level has this compact representation:

```json
{
  "columns": ["cluster_id", "sex", "wealth", "age_band", "child_count"],
  "rows": [[101, "Female", "Poorer", "6-23 months", 4]]
}
```

`columns` defines the position and meaning of every value in each `rows`
array. Depending on the requested level, the first key is absent (national),
`admin1_code`, or `cluster_id`. It is followed by the requested subset of:

- `sex`: PR recode value label.
- `residence`: PR recode urban/rural value label.
- `wealth`: PR recode wealth value label.
- `age_band`: `0-5 months`, `6-23 months`, or `24-59 months`.

Segment tables contain the five unweighted count fields plus weighted sums used
to derive rates safely after filtering:

- denominators: `haz_den_w`, `waz_den_w`, `whz_den_w`, `anemia_den_w`;
- binary numerators: `stunted_w`, `severely_stunted_w`, `underweight_w`,
  `severely_underweight_w`, `wasted_w`, `severely_wasted_w`, `overweight_w`,
  `anemia_w`, `severe_anemia_w`;
- weighted z-score sums: `haz_z_w`, `waz_z_w`, `whz_z_w`.

Rates are not stored on segment rows. Consumers must sum numerator and
denominator fields across selected rows before dividing; averaging percentages
would be incorrect.

## India consumer metadata

`python_backend/india_pipeline.py` supplies these optional `meta` fields:

| Field | Meaning |
|---|---|
| `survey` | Human-readable survey name and period. |
| `label_maps` | Admin1, residence, wealth, and sex code-to-label maps. |
| `filter_dimensions` | Available sex, wealth, and age-band filter labels. |
| `privacy_note` | Required reminder that the generated extract is restricted-local. |
| `unit` | Human-readable cluster unit description. |

No absolute source path, username, household identifier, child-level record,
or undisplaced coordinate is permitted anywhere in the exported schema.
