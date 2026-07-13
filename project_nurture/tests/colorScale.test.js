import test from 'node:test';
import assert from 'node:assert/strict';

import { colorFor, noDataColor } from '../src/lib/colorScale.js';

test('nullish and invalid metric values use the no-data color', () => {
  assert.equal(colorFor(null, 'risk_score'), noDataColor);
  assert.equal(colorFor(undefined, 'risk_score'), noDataColor);
  assert.equal(colorFor('', 'risk_score'), noDataColor);
  assert.equal(colorFor('not-a-number', 'risk_score'), noDataColor);
});

test('the shared scale preserves the established metric thresholds', () => {
  assert.equal(colorFor(35, 'anemia_rate'), '#2f9e7e');
  assert.equal(colorFor(70, 'anemia_rate'), '#b42318');
  assert.equal(colorFor(4, 'severe_wasting_rate'), '#f0a202');
  assert.equal(colorFor(25, 'stunting_rate'), '#f0a202');
  assert.equal(colorFor(25, 'stunting_rate'), colorFor(25, 'stunting_rate'));
});
