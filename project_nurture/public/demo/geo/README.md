# India district boundaries (maintainer input required)

`india_districts.geojson` is intentionally not committed. Obtain an openly
licensed India district boundary GeoJSON (for example, a suitably licensed
Datameet-derived source), then review its licence, required attribution, and
permitted redistribution before putting it in this repository.

Keep the reviewed source and its attribution notes with the maintainer's local
records. Simplify a copy to no more than 2 MB before preparing it, for example:

```text
mapshaper source.geojson -simplify 5% keep-shapes -o format=geojson simplified.geojson
```

Prepare it only after that review:

```text
python python_backend/prepare_geojson.py simplified.geojson --license-reviewed
```

The command writes this directory's `india_districts.geojson`, reports matched
and unmatched names against the committed demo fact-sheet input, and updates
the public data manifest. Review every unmatched name, extend
`python_backend/data/district_crosswalk.csv` with verified aliases where
appropriate, rerun the command, then review the artifact, manifest, and data
changelog before committing. The app shows a graceful notice until this file is
provided.
