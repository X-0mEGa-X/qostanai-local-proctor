const BLOCKED_KEYS = new Set(['c', 'v', 'x', 'l', 't', 'n', 'r', 'w']);
function shouldBlock(input) {
  const key = String(input.key).toLowerCase();
  if (input.control && input.shift && key === 'q') return false;
  return ((input.control || input.meta) && BLOCKED_KEYS.has(key)) ||
    (input.alt && ['tab', 'f4', 'escape'].includes(key)) ||
    ['printscreen', 'f11', 'f12'].includes(key);
}
function allowedNavigation(url, origin) {
  try { return new URL(url).origin === origin && new URL(url).pathname === '/'; }
  catch { return false; }
}
module.exports = {shouldBlock, allowedNavigation};
