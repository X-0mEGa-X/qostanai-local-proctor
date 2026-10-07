const test = require('node:test');
const assert = require('node:assert/strict');
const {shouldBlock, allowedNavigation} = require('../desktop/policy.cjs');
test('exam shortcuts are blocked while recovery shortcut remains allowed', () => {
  assert.equal(shouldBlock({key:'c', control:true}), true);
  assert.equal(shouldBlock({key:'Tab', alt:true}), true);
  assert.equal(shouldBlock({key:'PrintScreen'}), true);
  assert.equal(shouldBlock({key:'q', control:true, shift:true}), false);
  assert.equal(shouldBlock({key:'a'}), false);
});
test('navigation allows only the exact exam origin and page', () => {
  const origin = 'http://127.0.0.1:8765';
  assert.equal(allowedNavigation(origin+'/', origin), true);
  for (const url of ['https://example.com/', origin+'/api/report', 'javascript:alert(1)', 'http://127.0.0.1:8766/'])
    assert.equal(allowedNavigation(url, origin), false);
});
