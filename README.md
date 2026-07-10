# Project Nurture

Project Nurture is a child nutrition intelligence platform for exploring child malnutrition risk across India and imagining how national survey insight could connect with field-level case tracking.

The project started as a college proof of concept and is being rebuilt into a more credible public health data product. Its current foundation uses India Standard DHS survey data from The DHS Program to generate a local, interactive nutrition dashboard. The longer-term vision is to pair this national context with private case-following workflows for children receiving support on the ground.

## Why This Exists

Child malnutrition is not only a national statistic. It is also a local operational problem: programs need to know where risk is concentrated, what kind of nutrition burden exists in each area, and which children need continued follow-up after intervention.

Project Nurture explores that bridge:

- **Survey intelligence** for broad population-level patterns
- **Decision support** for prioritizing attention and resources
- **Case tracking** for monitoring individual children over time

The current repository focuses on the survey intelligence layer.

## Current Capabilities

- Interactive India map built with Leaflet
- India DHS displaced GPS cluster visualization
- Smooth marker clustering for dense survey points
- Heatmap-style nutrition risk intensity
- National weighted nutrition indicators
- Highest-risk state summary panel
- Local Python pipeline for converting DHS files into dashboard-ready JSON
- Clear separation between restricted local data and code that can be shared publicly

Current child nutrition indicators include:

- stunting
- severe stunting
- wasting
- underweight
- overweight
- anemia
- mean height-for-age, weight-for-age, and weight-for-height z-scores

## Technical Overview

**Frontend**

- React
- Vite
- Chakra UI
- Leaflet
- leaflet.markercluster
- leaflet.heat
- Firebase authentication foundation

**Data/Pipeline**

- Python
- pandas
- NumPy
- pyshp
- India DHS Household Member Recode
- DHS displaced GPS cluster shapefile

The dashboard data is generated locally from approved DHS files and is not committed to the repository.

## Data Responsibility

DHS microdata is restricted. This repository does not include raw DHS files, generated microdata-derived extracts, or real child case records.

The project intentionally separates:

- **committable code and documentation**
- **local restricted research data**
- **future public/demo data**
- **future private operational case records**

Do not commit:

- `dhs_data/`
- generated DHS extracts
- raw child, household, woman, or cluster-level records
- real field case records
- private environment files

## Local DHS Pipeline

Expected local files:

- `dhs_data/IAPR7EDT/IAPR7EFL.DTA` - Household Member Recode (PR)
- `dhs_data/IAGE7AFL/IAGE7AFL.shp` - DHS GPS cluster shapefile

Generate the local dashboard extract from the repository root:

```bash
python python_backend/dhs_pipeline.py
```

This creates:

```text
project_nurture/public/generated/dhs_cluster_nutrition.json
```

The generated file is ignored by git because it is derived from restricted survey data.

Validate generated indicators against the official India DHS fact sheets:

```bash
python python_backend/validate_dhs_outputs.py
```

The validation report is written locally to:

```text
python_backend/outputs/dhs_validation_report.csv
```

That report is also ignored by git.

## Running Locally

Install and run the frontend:

```bash
cd project_nurture
npm install
npm run dev
```

Open:

```text
http://localhost:5173/
```

Set up the Python environment:

```bash
cd python_backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Roadmap

- [x] Replace synthetic map data with a DHS-derived local extract
- [x] Preserve marker clustering and heatmap map experience
- [x] Add national and state nutrition summary panel
- [x] Remove fake-data model and coordinate-generation workflow
- [x] Validate national and state-level indicators against official India DHS fact sheets
- [ ] Add filters for indicator, state, district, residence, wealth, sex, and age band
- [ ] Add state and district profile views
- [ ] Build a safe public/demo data mode for portfolio deployment
- [ ] Design private field case-tracking data model
- [ ] Add role-aware authentication and protected workflows
- [ ] Reframe ML around explainable risk, prioritization, and driver analysis

## Long-Term Vision

The intended end state is a platform where national survey data helps identify risk patterns, while field teams can privately monitor real cases, follow up over time, and understand whether care is improving a child’s nutrition trajectory.

Project Nurture is not a diagnostic tool. It is a data product for exploration, prioritization, and responsible public health decision support.
