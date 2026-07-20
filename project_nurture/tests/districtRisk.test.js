import test from 'node:test';
import assert from 'node:assert/strict';

import { applyDistrictRisk } from '../src/lib/districtRisk.js';
import { addDerivedIndicators } from '../src/lib/nutritionData.js';

const indicators = {
  metadata: { tier: 'demo' },
  districts: [
    { district_slug: 'one', state_slug: 'state-a', risk_score: 12 },
    { district_slug: 'two', state_slug: 'state-a', risk_score: 24 },
    { district_slug: 'missing', state_slug: 'state-b', risk_score: 36 },
  ],
  states: [
    { state_slug: 'state-a', risk_score: 18 },
    { state_slug: 'state-b', risk_score: 36 },
  ],
  national: { risk_score: 24 },
};

const risk = {
  schema_version: '1.0',
  metadata: { placeholder_status: 'Demo placeholders.' },
  districts: [
    {
      district_slug: 'one', composite_score: 80,
      stunting_percentile: 100, underweight_percentile: 75, wasting_percentile: 50,
    },
    {
      district_slug: 'two', composite_score: 40,
      stunting_percentile: 50, underweight_percentile: 25, wasting_percentile: 0,
    },
  ],
};

test('district percentile risk replaces the older rate composite and rebuilds rollups', () => {
  const merged = applyDistrictRisk(indicators, risk);

  assert.equal(merged.districts[0].risk_score, 80);
  assert.equal(merged.districts[1].risk_score, 40);
  assert.equal(merged.districts[2].risk_score, null);
  assert.equal(merged.states[0].risk_score, 60);
  assert.equal(merged.states[1].risk_score, null);
  assert.equal(merged.national.risk_score, 60);
  assert.equal(merged.metadata.risk_methodology, 'phase-4-district-percentile');
  assert.equal(indicators.districts[0].risk_score, 12);
});

test('cluster and research-mode risk remains the weighted-rate composite', () => {
  const clusterSummary = addDerivedIndicators({
    stunted_w: 4, haz_den_w: 10, severely_stunted_w: 1, haz_z_w: -1200,
    underweight_w: 3, waz_den_w: 10, severely_underweight_w: 1, waz_z_w: -900,
    wasted_w: 2, whz_den_w: 10, severely_wasted_w: 1, overweight_w: 0,
    whz_z_w: -600, anemia_w: 0, anemia_den_w: 0, severe_anemia_w: 0,
  });

  assert.equal(clusterSummary.risk_score, 32.5);
});

test('an invalid risk artifact is rejected instead of being mislabeled', () => {
  assert.throws(() => applyDistrictRisk(indicators, { districts: [] }), /schema_version 1.0/);
});
