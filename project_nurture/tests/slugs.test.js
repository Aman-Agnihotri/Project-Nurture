import test from 'node:test';
import assert from 'node:assert/strict';

import { buildSlugLookup, stateForDashboardQuery, toSlug } from '../src/lib/slugs.js';

test('slug normalization handles punctuation, ampersands, whitespace, and Unicode marks', () => {
  assert.equal(toSlug(' NCT of Delhi! '), 'nct-of-delhi');
  assert.equal(toSlug('A &   B'), 'a-and-b');
  assert.equal(toSlug('Puduchérry'), 'puducherry');
});

test('three state collisions remain distinct and reversible', () => {
  const records = ['A & B', 'A and B', 'A--and B'].map((state_name, index) => ({
    state_name,
    district_name: `District ${index}`,
  }));
  const lookup = buildSlugLookup(records);

  assert.equal(lookup.stateBySlug.size, 3);
  assert.deepEqual([...lookup.stateBySlug.keys()], ['a-and-b', 'a-and-b-2', 'a-and-b-3']);
});

test('district collisions are unique within their state', () => {
  const records = ['D & E', 'D and E', 'D--and E'].map(district_name => ({
    state_name: 'Example State',
    district_name,
  }));
  const lookup = buildSlugLookup(records);

  assert.equal(lookup.districtBySlug.size, 3);
  assert.ok(lookup.districtBySlug.has('example-state/d-and-e-3'));
});

test('dashboard query validation uses artifact state slugs', () => {
  const states = [{ state_name: 'NCT of Delhi', state_slug: 'nct-of-delhi' }];
  assert.equal(stateForDashboardQuery(states, 'nct-of-delhi'), states[0]);
  assert.equal(stateForDashboardQuery(states, 'unknown'), null);
});
