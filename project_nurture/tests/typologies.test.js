import test from 'node:test';
import assert from 'node:assert/strict';

import { colorStops, noDataColor } from '../src/lib/colorScale.js';
import { mapMetricOptions } from '../src/lib/nutritionData.js';
import {
  applyDistrictTypologies,
  typologyColorFor,
  typologyLegendData,
  typologyPalette,
} from '../src/lib/typologies.js';

const artifact = {
  schema_version: '1.0',
  metadata: { placeholder_status: 'Demo placeholder typologies.' },
  districts: [
    { district_slug: 'one', typology_id: 'typology-2' },
    { district_slug: 'two', typology_id: 'typology-1' },
  ],
  typologies: [
    { id: 'typology-1', label: 'High stunting', description: 'First profile.' },
    { id: 'typology-2', label: 'Low wasting', description: 'Second profile.' },
  ],
};

test('typology assignments join by district_slug with categorical colors', () => {
  const data = applyDistrictTypologies({ districts: [
    { district_slug: 'one', district_name: 'One' },
    { district_slug: 'two', district_name: 'Two' },
  ] }, artifact);

  assert.equal(data.districts[0].typology_label, 'Low wasting');
  assert.equal(data.districts[0].typology_color, typologyPalette[1]);
  assert.equal(typologyColorFor(data.districts[0]), typologyPalette[1]);
  assert.equal(data.districts[1].typology_label, 'High stunting');
  assert.equal(data.metadata.typology_placeholder_status, 'Demo placeholder typologies.');
});

test('categorical legend preserves every artifact typology and color', () => {
  assert.deepEqual(typologyLegendData(artifact), [
    {
      id: 'typology-1', label: 'High stunting', description: 'First profile.',
      color: typologyPalette[0],
    },
    {
      id: 'typology-2', label: 'Low wasting', description: 'Second profile.',
      color: typologyPalette[1],
    },
  ]);
});

test('missing assignments use gray and invalid artifacts fail safely', () => {
  const data = applyDistrictTypologies({ districts: [{ district_slug: 'missing' }] }, artifact);
  assert.equal(data.districts[0].typology_id, null);
  assert.equal(typologyColorFor(data.districts[0]), noDataColor);
  assert.throws(() => typologyLegendData({}), /schema_version 1.0/);
});

test('typology is choropleth-only and categorical colors differ from the numeric scale', () => {
  assert.equal(mapMetricOptions('choropleth').at(-1).key, 'typology');
  assert.ok(mapMetricOptions('clusters').every(option => option.key !== 'typology'));
  assert.ok(mapMetricOptions('heat').every(option => option.key !== 'typology'));
  assert.ok(typologyPalette.every(color => !colorStops.includes(color)));
});
