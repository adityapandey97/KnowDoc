import test from 'node:test';
import assert from 'node:assert';
import { formatBytes, formatDate } from '../utils/formatters.js';

test('formatBytes formats file sizes accurately', () => {
  assert.strictEqual(formatBytes(0), '0 Bytes');
  assert.strictEqual(formatBytes(1024), '1 KB');
  assert.strictEqual(formatBytes(1024 * 1024 * 5), '5 MB');
});

test('formatDate formats ISO dates to readable strings', () => {
  const formatted = formatDate('2026-11-01T00:00:00.000Z');
  assert.ok(formatted.includes('2026'));
});

