import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

import {
  buildDistrictLookup,
  createGeometryLoader,
  districtForFeature,
} from '../src/lib/districtGeo.js';

const fixtureUrl = new URL(
  '../../python_backend/tests/fixtures/synthetic_districts.geojson',
  import.meta.url,
);

test('geometry loader fetches and validates a FeatureCollection only once', async () => {
  let calls = 0;
  const geometry = { type: 'FeatureCollection', features: [] };
  const loader = createGeometryLoader('/districts.geojson', async () => {
    calls += 1;
    return { ok: true, status: 200, json: async () => geometry };
  });

  const [first, second] = await Promise.all([loader(), loader()]);
  assert.equal(calls, 1);
  assert.equal(first, geometry);
  assert.equal(second, geometry);
});

test('geometry loader rejects a missing public artifact', async () => {
  const loader = createGeometryLoader('/missing.geojson', async () => ({
    ok: false,
    status: 404,
  }));
  await assert.rejects(loader(), /status 404/);
});

test('synthetic fixture polygons match normalized district records', async () => {
  const geometry = JSON.parse(await readFile(fixtureUrl, 'utf8'));
  const preparedFeatures = geometry.features.map(feature => ({
    ...feature,
    properties: {
      state_name: feature.properties.STATE
        || feature.properties.st_name
        || feature.properties.state_name,
      district_name: feature.properties.DISTRICT
        || feature.properties.dist_name
        || feature.properties.district_name,
    },
  }));
  const lookup = buildDistrictLookup([
    { state_name: 'Bihar', district_name: 'Demo District B1' },
    { state_name: 'Madhya Pradesh', district_name: 'Demo District M1' },
  ]);

  assert.equal(districtForFeature(preparedFeatures[0], lookup)?.district_name, 'Demo District B1');
  assert.equal(districtForFeature(preparedFeatures[1], lookup)?.district_name, 'Demo District M1');
  assert.equal(districtForFeature(preparedFeatures[2], lookup), undefined);
});
