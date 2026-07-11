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
 */

const GENERATED_PATH = 'generated/dhs_cluster_nutrition.json';
const DEMO_PATH = 'demo/demo_cluster_nutrition.json';

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
    const data = await response.json();
    return { data, tier: data?.metadata?.tier || 'restricted-local' };
  } catch {
    // Expected on the demo-tier deployment path; fall through to the demo artifact.
  }

  const demoResponse = await fetch(demoUrl);
  if (demoResponse.ok) {
    const data = await demoResponse.json();
    return { data, tier: 'demo' };
  }

  throw new Error(
    `Unable to load dashboard data from either "${generatedUrl}" or "${demoUrl}".`,
  );
}
