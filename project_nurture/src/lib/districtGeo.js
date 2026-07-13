export const normalizeGeoName = value => String(value || '')
  .normalize('NFKC')
  .toLowerCase()
  .replaceAll('&', ' and ')
  .replace(/[^\p{L}\p{N}]+/gu, ' ')
  .trim()
  .replace(/\s+/g, ' ');

export const districtKey = values => {
  const state = values?.normalized_state_name || normalizeGeoName(values?.state_name);
  const district = values?.normalized_district_name || normalizeGeoName(values?.district_name);
  return `${state}|${district}`;
};

export const buildDistrictLookup = records => new Map(
  (records || []).map(record => [districtKey(record), record]),
);

export const districtForFeature = (feature, lookup) => lookup.get(
  districtKey(feature?.properties || {}),
);

export const fetchDistrictGeometry = async (url, fetchImpl = fetch) => {
  const response = await fetchImpl(url);
  if (!response.ok) {
    throw new Error(`District geometry request failed with status ${response.status}`);
  }
  const geometry = await response.json();
  if (geometry?.type !== 'FeatureCollection' || !Array.isArray(geometry.features)) {
    throw new Error('District geometry must be a GeoJSON FeatureCollection');
  }
  return geometry;
};

export const createGeometryLoader = (url, fetchImpl = fetch) => {
  let request = null;
  return () => {
    if (!request) request = fetchDistrictGeometry(url, fetchImpl);
    return request;
  };
};
