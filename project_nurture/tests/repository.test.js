import test from 'node:test';
import assert from 'node:assert/strict';

import {
  DOCS_PATH,
  REPO_URL,
  repositoryDocumentUrl,
} from '../src/lib/repository.js';

test('methodology link is built from reusable repository and docs constants', () => {
  assert.equal(REPO_URL, 'https://github.com/Aman-Agnihotri/Project-Nurture');
  assert.equal(DOCS_PATH, 'docs');
  assert.equal(
    repositoryDocumentUrl('methodology.md'),
    'https://github.com/Aman-Agnihotri/Project-Nurture/blob/main/docs/methodology.md',
  );
});
