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
let protectionRevision = 0, emergencyTask;

function rendererAvailable() { return window && !window.isDestroyed() && !window.webContents.isDestroyed() && !window.webContents.isCrashed(); }
function send(code) { if (rendererAvailable()) window.webContents.send('security-event', code); }
function protect(enabled) {
  protectionRevision++;
  protectedMode = enabled;
  if (!window || window.isDestroyed()) return;
  window.setKiosk(enabled);
  window.setAlwaysOnTop(enabled);
  window.setResizable(!enabled);
  send(enabled ? 'desktop_guard_started' : 'desktop_guard_stopped');
}
async function backendRequest(endpoint, body, timeout = 4500) {
  const cookies = await window.webContents.session.cookies.get({url: ORIGIN, name: 'proctor_session'});
  if (!cookies.length) throw new Error('Local session cookie unavailable');
  const response = await fetch(`${ORIGIN}/api/${endpoint}`, {
    method: body === undefined ? 'GET' : 'POST',
    headers: {Cookie: `proctor_session=${cookies[0].value}`, Origin: ORIGIN, 'Content-Type': 'application/json'},
    body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(timeout)
  });
  if (!response.ok) throw new Error(`Backend request failed (${response.status})`);
  return response.json();
}
function emergency() {
  send('emergency_exit');
  protect(false);
  if (rendererAvailable()) window.webContents.send('emergency-exit');
  // Main-process recovery does not depend on renderer JavaScript being responsive.
  if (!emergencyTask && backend && backend.exitCode === null && !backend.killed) {
    emergencyTask = (async () => {
      try { await backendRequest('security', {code:'emergency_exit'}, 1000); } catch {}
      try { await backendRequest('stop', {}); }
      catch { if (backend && backend.exitCode === null) backend.kill(); }
    })().finally(() => { emergencyTask = null; });
  }
  return emergencyTask || Promise.resolve();
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
      send('backend_stopped');
    }
  });
  for (let i=0; i<100; i++) {
    if (launchError) throw launchError;
    if (backend.exitCode !== null) throw new Error(`Backend failed: ${backendLog}`);
    try { const response = await fetch(`${ORIGIN}/health`, {signal: AbortSignal.timeout(500)}); if (response.ok) return; } catch {}
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
    ipcMain.handle('set-protected', async (event, enabled) => {
      if (event.sender !== window.webContents) return false;
      if (!enabled) { protect(false); return false; }
      const revision = ++protectionRevision;
      const status = await backendRequest('status');
      if (status.active && revision === protectionRevision) protect(true);
      return protectedMode;
    });
    window.webContents.on('unresponsive', emergency);
    ipcMain.handle('emergency-stop', event => event.sender === window.webContents ? emergency() : undefined);
    window.webContents.on('render-process-gone', emergency);
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
        document.getElementById('start').click();
        await new Promise(r=>setTimeout(r,1000));
        const restarted=await fetch('/api/status').then(r=>r.json());
        document.dispatchEvent(new KeyboardEvent('keydown',{key:'q',ctrlKey:true,shiftKey:true,bubbles:true}));
        await new Promise(r=>setTimeout(r,1200));
        document.getElementById('start').click();
        document.dispatchEvent(new KeyboardEvent('keydown',{key:'q',ctrlKey:true,shiftKey:true,bubbles:true}));
        await new Promise(r=>setTimeout(r,1200));
        const report=await fetch('/api/report').then(r=>r.json());
        return {active:status.active, mode:status.mode, codes:status.events.map(e=>e.code), reportSession:report.session_id,
          title:document.title, desktopBridge:Boolean(window.desktop), runtime:document.getElementById('runtime').textContent,
          modelState:document.getElementById('model-state').textContent, eventCount:document.getElementById('event-count').textContent,
          ended:!report.active, restartWorks:restarted.active, stopDisabled:document.getElementById('stop').disabled};
      })()`);
      fs.mkdirSync(path.join(ROOT, 'output/qa'), {recursive:true});
      // Exercise the actual Export button and Electron download, not just the API.
      const downloadPath = path.join(ROOT, 'output/qa/exported-report.json');
      const downloaded = new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Report download timed out')), 5000);
        window.webContents.session.once('will-download', (_event, item) => {
          item.setSavePath(downloadPath);
          item.once('done', (_event, state) => {
            clearTimeout(timer);
            if (state === 'completed') resolve(JSON.parse(fs.readFileSync(downloadPath, 'utf8')));
            else reject(new Error(`Report download ${state}`));
          });
        });
      });
      await window.webContents.executeJavaScript("document.getElementById('export').click()");
      const exported = await downloaded;
      result.downloadValid = exported.session_id === result.reportSession && !exported.active && Boolean(exported.ended_at);
      // End-session recovery still works if the renderer's stop request fails.
      await window.webContents.executeJavaScript(`(async () => {
        document.getElementById('start').click();
        await new Promise(r=>setTimeout(r,900));
        window.smokeOriginalFetch=window.fetch;
        window.fetch=(url,...args)=>String(url)==='/api/stop'?Promise.reject(new Error('Injected page request failure')):window.smokeOriginalFetch(url,...args);
        document.getElementById('stop').click();
        await new Promise(r=>setTimeout(r,900));
        window.fetch=window.smokeOriginalFetch;
        delete window.smokeOriginalFetch;
      })()`);
      await emergencyTask;
      result.stopRequestFailureReleased = !(await backendRequest('status')).active && !protectedMode;
      // A crashed renderer cannot run the page's emergency handler.
      await backendRequest('start', {mode:'simulation', consent:true});
      protect(true);
      const crashed = new Promise(resolve => window.webContents.once('render-process-gone', resolve));
      window.webContents.forcefullyCrashRenderer();
      await crashed;
      await emergencyTask;
      const afterCrash = await backendRequest('status');
      result.rendererCrashReleased = !afterCrash.active && !protectedMode && !afterCrash.native_guard;
      await window.loadURL(ORIGIN);
      await new Promise(resolve => setTimeout(resolve, 900));
      fs.writeFileSync(path.join(ROOT, 'output/qa/electron-smoke.json'), JSON.stringify(result, null, 2));
      fs.writeFileSync(path.join(ROOT, 'output/qa/desktop.png'), (await window.webContents.capturePage()).toPNG());
      await window.webContents.executeJavaScript('window.scrollTo(0, document.body.scrollHeight)');
      await new Promise(resolve=>setTimeout(resolve,200));
      fs.writeFileSync(path.join(ROOT, 'output/qa/desktop-bottom.png'), (await window.webContents.capturePage()).toPNG());
      console.log(JSON.stringify(result));
      if (result.runtime !== 'LOCAL DESKTOP' || result.modelState.includes('Checking') || !result.ended || !result.restartWorks || !result.stopDisabled || !result.codes.includes('phone_visible') || !result.downloadValid || !result.rendererCrashReleased || !result.stopRequestFailureReleased) throw new Error('Desktop UI smoke check failed');
      app.quit();
    }
  } catch (error) {
    quitting = true;
    protect(false);
    globalShortcut.unregisterAll();
    if (backend) backend.kill();
    console.error(error.message);
    if (!SMOKE) dialog.showErrorBox('Could not start Local Proctor', error.message);
    app.exit(1);
  }
});
app.on('window-all-closed', () => app.quit());
app.on('before-quit', () => { quitting = true; protectedMode = false; globalShortcut.unregisterAll(); if (backend) backend.kill(); });
