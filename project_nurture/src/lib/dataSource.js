/**
 * Tiered dashboard data loader.
 *
 * Data tiers touched:
 * - Tier 1 (restricted-local): the researcher-generated `generated/dhs_cluster_nutrition.json`
 *   extract, produced locally from restricted DHS microdata. Never bundled or committed.
 * - Tier 2 (demo): the committed `demo/demo_cluster_nutrition.json` synthetic artifact, used
 *   as a public-safe fallback when the Tier 1 extract is not present.
 *
 * This module only reads these files at runtime via fetch; it never imports or bundles either
 * JSON artifact directly.
 *
 * Dual-schema support: the Tier 1 extract may be either the legacy (pre-dhs-nutrition)
 * dashboard shape or the `dhs-nutrition` package's v1.0 `IndicatorResult.to_json` shape
 * (`schema_version: "1.0"`, `levels`/`segments`/`meta`). `normalizeV1` reshapes the v1.0
 * payload into the legacy shape the rest of the app consumes, so downstream code (and the
 * Tier 2 demo artifact, which stays in the legacy shape) only ever sees one schema.
 */

const GENERATED_PATH = 'generated/dhs_cluster_nutrition.json';
const DEMO_PATH = 'demo/demo_cluster_nutrition.json';
const DISTRICT_INDICATORS_PATH = 'demo/district_indicators.json';

/**
 * Compute the composite risk score from stunting/underweight/wasting rates.
 * Mirrors the legacy pipeline's weighting (45% stunting, 35% underweight, 20% wasting).
 *
 * @param {object} record - Record with stunting_rate, underweight_rate, wasting_rate.
 * @returns {number|null} Weighted risk score, or null if any input rate is missing.
 */
function riskScore(record) {
  const { stunting_rate: stunting, underweight_rate: underweight, wasting_rate: wasting } =
    record || {};
  if (
    typeof stunting !== 'number' ||
    typeof underweight !== 'number' ||
    typeof wasting !== 'number'
  ) {
    return null;
  }
  return 0.45 * stunting + 0.35 * underweight + 0.2 * wasting;
}

/**
 * Classify cluster sample quality from the valid HAZ sample size.
 * Mirrors the legacy pipeline's thresholds.
 *
 * @param {number} hazValidN - Count of children with a valid HAZ measurement.
 * @returns {'stable'|'limited'|'sparse'} Sample quality bucket.
 */
function sampleQuality(hazValidN) {
  if (hazValidN >= 10) return 'stable';
  if (hazValidN >= 5 && hazValidN <= 9) return 'limited';
  return 'sparse';
}

/**
 * Reshape a `dhs-nutrition` v1.0 dashboard payload into the legacy dashboard shape.
 * Payloads that are not schema_version "1.0" (including the legacy shape itself) are
 * returned unchanged.
 *
 * @param {object} data - Parsed dashboard JSON.
 * @returns {object} Legacy-shaped dashboard data.
 */
function normalizeV1(data) {
  if (data?.schema_version !== '1.0') return data;

  const national = data.levels?.national || {};
  const states = (data.levels?.admin1 || []).map(({ admin1_code, admin1_name, ...rest }) => ({
    state_code: admin1_code,
    state_name: admin1_name,
    ...rest,
    risk_score: riskScore(rest),
  }));
  const clusters = (data.levels?.cluster || []).map(
    ({ admin1_code, admin1_name, admin2_name, residence, ...rest }) => ({
      ...rest,
      state_code_gps: admin1_code,
      state_name: admin1_name,
      district_name: admin2_name,
      urban_rural_gps: residence,
      risk_score: riskScore(rest),
      sample_quality: sampleQuality(rest.haz_valid_n),
    }),
  );

  return {
    metadata: {
      schema_version: data.schema_version,
      tier: data.tier,
      generated_at: data.generated_at,
      source_files: data.source_files,
      filter_dimensions: data.meta?.filter_dimensions || {},
      label_maps: data.meta?.label_maps || {},
    },
    national: { ...national, risk_score: riskScore(national) },
    states,
    clusters,
    cluster_segment_columns: data.segments?.cluster?.columns || [],
    cluster_segments: data.segments?.cluster?.rows || [],
  };
}

/**
 * Load dashboard data, preferring the local Tier 1 research extract and falling back to the
 * committed Tier 2 demo artifact when the extract is not present or fails to load.
 *
 * @param {string} baseUrl - Application base URL (e.g. `import.meta.env.BASE_URL`).
 * @returns {Promise<{ data: object, tier: string }>} Parsed dashboard data and its tier; demo-path
 *   loads always report tier "demo", regardless of the artifact's own metadata.
 * @throws {Error} If both the generated extract and the demo artifact fail to load.
 */
export async function loadDashboardData(baseUrl) {
  const generatedUrl = `${baseUrl}${GENERATED_PATH}`;
  const demoUrl = `${baseUrl}${DEMO_PATH}`;

  try {
    const response = await fetch(generatedUrl, { cache: 'no-store' });
    if (!response.ok) {
      throw new Error('Generated extract missing');
    }
    const data = normalizeV1(await response.json());
    return { data, tier: data?.metadata?.tier || 'restricted-local' };
  } catch {
    // Expected on the demo-tier deployment path; fall through to the demo artifact.
  }

  const demoResponse = await fetch(demoUrl);
  if (demoResponse.ok) {
    const data = normalizeV1(await demoResponse.json());
    return { data, tier: 'demo' };
  }

  throw new Error(
    `Unable to load dashboard data from either "${generatedUrl}" or "${demoUrl}".`,
  );
}

/** Load the public-only district profile artifact without touching T1 data. */
export async function loadDistrictIndicators(baseUrl) {
  const response = await fetch(`${baseUrl}${DISTRICT_INDICATORS_PATH}`);
  if (!response.ok) throw new Error('District indicators unavailable');
  return response.json();
}
