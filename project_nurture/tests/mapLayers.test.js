import test from 'node:test';
import assert from 'node:assert/strict';

import { cleanupLeafletLayers } from '../src/lib/mapLayers.js';

const mockLayer = () => {
  const calls = { childOff: 0, off: 0, clear: 0, remove: 0 };
  return {
    calls,
    eachLayer(callback) { callback({ off: () => { calls.childOff += 1; } }); },
    off() { calls.off += 1; },
    clearLayers() { calls.clear += 1; },
    remove() { calls.remove += 1; },
  };
};

test('each mode-switch cleanup detaches handlers and removes its layer once', () => {
  const firstModeLayer = mockLayer();
  const secondModeLayer = mockLayer();

  cleanupLeafletLayers([firstModeLayer]);
  cleanupLeafletLayers([secondModeLayer]);

  for (const layer of [firstModeLayer, secondModeLayer]) {
    assert.deepEqual(layer.calls, { childOff: 1, off: 1, clear: 1, remove: 1 });
  }
});
