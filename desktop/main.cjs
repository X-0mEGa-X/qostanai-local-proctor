const {app, BrowserWindow, Menu, ipcMain, globalShortcut, dialog} = require('electron');
const {spawn} = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');
const {shouldBlock, allowedNavigation} = require('./policy.cjs');
const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.env.PROCTOR_PORT || 8765);
const ORIGIN = `http://127.0.0.1:${PORT}`;
const SMOKE = process.argv.includes('--smoke-test');
let window, backend, protectedMode = false, quitting = false, backendLog = '';

function send(code) { if (window && !window.isDestroyed()) window.webContents.send('security-event', code); }
function protect(enabled) {
  protectedMode = enabled;
  if (!window || window.isDestroyed()) return;
  window.setKiosk(enabled);
  window.setAlwaysOnTop(enabled);
  window.setResizable(!enabled);
  send(enabled ? 'desktop_guard_started' : 'desktop_guard_stopped');
}
function emergency() {
  send('emergency_exit');
  protect(false);
  if (window && !window.isDestroyed()) window.webContents.send('emergency-exit');
}

async function launchBackend() {
  const python = process.env.PROCTOR_PYTHON || path.join(ROOT, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  if (!fs.existsSync(python)) throw new Error('Run scripts/setup.ps1 first. Python virtual environment is missing.');
  // Refuse to attach to an unrelated process already occupying the port.
  try { await fetch(`${ORIGIN}/health`, {signal: AbortSignal.timeout(500)}); throw new Error(`Port ${PORT} is already in use. Stop the old backend first.`); }
  catch (error) { if (error.message.includes('already in use')) throw error; }
  backend = spawn(python, ['-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', String(PORT)],
    {cwd: ROOT, windowsHide: true, env: {...process.env, PYTHONIOENCODING: 'utf-8'}});
  let launchError;
  backend.on('error', error => { launchError = error; });
  for (const stream of [backend.stdout, backend.stderr]) stream.on('data', data => { backendLog = (backendLog + data.toString()).slice(-4000); });
  backend.on('exit', () => {
    if (window && !window.isDestroyed() && !quitting) {
      emergency();
      window.webContents.send('security-event', 'backend_stopped');
    }
  });
  for (let i=0; i<100; i++) {
    if (launchError) throw launchError;
    if (backend.exitCode !== null) throw new Error(`Backend failed: ${backendLog}`);
    try { const response = await fetch(`${ORIGIN}/health`); if (response.ok) return; } catch {}
    await new Promise(resolve => setTimeout(resolve, 150));
  }
  throw new Error(`Backend did not start: ${backendLog}`);
}

app.whenReady().then(async () => {
  Menu.setApplicationMenu(null);
  try {
    await launchBackend();
    window = new BrowserWindow({width: 1440, height: 960, minWidth: 1100, minHeight: 760, show: !SMOKE,
      backgroundColor: '#101817', title: 'Qostanai Local Proctor',
      webPreferences: {preload: path.join(__dirname, 'preload.cjs'), nodeIntegration: false, contextIsolation: true, sandbox: true}});
    if (SMOKE) window.webContents.on('console-message', event => { if (event.level >= 2) console.log('Renderer:', event.message); });
    window.webContents.session.setPermissionRequestHandler((_webContents, _permission, callback) => callback(false));
    window.webContents.setWindowOpenHandler(() => { send('window_blocked'); return {action:'deny'}; });
    window.webContents.on('will-navigate', (event, url) => { if (!allowedNavigation(url, ORIGIN)) { event.preventDefault(); send('navigation_blocked'); } });
    window.webContents.on('will-redirect', (event, url) => { if (!allowedNavigation(url, ORIGIN)) event.preventDefault(); });
    window.webContents.on('before-input-event', (event, input) => {
      if (protectedMode && shouldBlock(input)) { event.preventDefault(); if (input.type === 'keyDown') send('shortcut_blocked'); }
    });
    window.on('blur', () => { if (protectedMode) send('focus_lost'); });
    window.on('close', event => { if (protectedMode && !quitting) { event.preventDefault(); send('shortcut_blocked'); } });
    ipcMain.handle('set-protected', (event, enabled) => { if (event.sender === window.webContents) protect(enabled); return protectedMode; });
    // Always reserved for recovery, including when exam mode is active.
    const registered = globalShortcut.register('CommandOrControl+Shift+Q', emergency);
    if (!registered) throw new Error('Emergency exit shortcut unavailable. Close conflicting apps before starting.');
    await window.loadURL(ORIGIN);
    if (SMOKE) {
      const result = await window.webContents.executeJavaScript(`(async () => {
        const call = (path, body) => fetch(path,{method:'POST', headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json());
        document.getElementById('consent').checked=true;
        document.getElementById('start').click();
        await new Promise(r=>setTimeout(r,11000));
        const status=await fetch('/api/status').then(r=>r.json());
        document.dispatchEvent(new KeyboardEvent('keydown',{key:'q',ctrlKey:true,shiftKey:true,bubbles:true}));
        await new Promise(r=>setTimeout(r,1200));
        const report=await fetch('/api/report').then(r=>r.json());
        return {active:status.active, mode:status.mode, codes:status.events.map(e=>e.code), reportSession:report.session_id,
          title:document.title, desktopBridge:Boolean(window.desktop), runtime:document.getElementById('runtime').textContent,
          modelState:document.getElementById('model-state').textContent, eventCount:document.getElementById('event-count').textContent,
          ended:!report.active, stopDisabled:document.getElementById('stop').disabled};
      })()`);
      fs.mkdirSync(path.join(ROOT, 'output/qa'), {recursive:true});
      fs.writeFileSync(path.join(ROOT, 'output/qa/electron-smoke.json'), JSON.stringify(result, null, 2));
      fs.writeFileSync(path.join(ROOT, 'output/qa/desktop.png'), (await window.webContents.capturePage()).toPNG());
      await window.webContents.executeJavaScript('window.scrollTo(0, document.body.scrollHeight)');
      await new Promise(resolve=>setTimeout(resolve,200));
      fs.writeFileSync(path.join(ROOT, 'output/qa/desktop-bottom.png'), (await window.webContents.capturePage()).toPNG());
      console.log(JSON.stringify(result));
      if (result.runtime !== 'LOCAL DESKTOP' || result.modelState.includes('Checking') || !result.ended || !result.stopDisabled || !result.codes.includes('phone_visible')) throw new Error('Desktop UI smoke check failed');
      app.quit();
    }
  } catch (error) {
    console.error(error.message);
    if (!SMOKE) dialog.showErrorBox('Could not start Local Proctor', error.message);
    app.exit(1);
  }
});
app.on('window-all-closed', () => app.quit());
app.on('before-quit', () => { quitting = true; protectedMode = false; globalShortcut.unregisterAll(); if (backend) backend.kill(); });
