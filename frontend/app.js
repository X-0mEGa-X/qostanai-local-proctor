const $ = id => document.getElementById(id);
let active = false, mode = 'simulation', busy = false, pollBusy = false, frameUrl, lastEventKey = '';
let cancelStart = false;
const isDesktop = Boolean(window.desktop);
$('runtime').textContent = isDesktop ? 'LOCAL DESKTOP' : 'BROWSER PREVIEW · LIMITED PROTECTION';
function notice(message, error=false) { $('notice').textContent = message; $('notice').classList.toggle('error', error); }
async function api(path, body) {
  const response = await fetch('/api/'+path, body === undefined ? {} : {
    method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)
  });
  if (!response.ok) { const data=await response.json(); throw new Error(data.detail || 'Request failed'); }
  return response.status === 204 ? null : response.json();
}
function timeLabel(seconds) { return `${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(Math.floor(seconds%60)).padStart(2,'0')}`; }
async function signal(code) { if (active) { try { await api('security',{code}); } catch {} } }
async function release() { if (isDesktop) await window.desktop.setProtected(false); }
async function emergencyEnd() {
  cancelStart = true;
  await release();
  try { await api('stop',{}); active=false; notice('Emergency exit: session ended and protection released.'); }
  catch(error) { notice('Emergency exit requested. '+error.message,true); }
}
async function endSession() {
  if (busy) return;
  busy=true;
  try {
    await release();
    await api('stop',{});
    active=false;
    notice('Session ended. Protection released. Export the event report for human review.');
    await poll();
  } catch(error) { notice(error.message,true); }
  finally {busy=false;}
}
$('start').addEventListener('click', async () => {
  if (busy) return;
  busy=true;
  cancelStart=false;
  $('start').disabled=true;
  try {
    mode=$('mode').value;
    if (!$('consent').checked) throw new Error('Please confirm local monitoring consent before starting.');
    await api('start',{mode,consent:true,native_guard:$('native-guard').checked,camera_index:Number($('camera-index').value)});
    if(cancelStart){await api('stop',{});throw new Error('Start canceled by emergency exit. Protection released.');}
    active=true;
    if (isDesktop) await window.desktop.setProtected(true);
    notice(mode==='simulation' ? 'SIMULATION: all vision signals are scripted for rehearsal. This is not a live detection demonstration.' : 'Live monitoring started. Look straight at the screen for 20 valid frames to calibrate gaze and head pose.');
    await poll();
  } catch(error) { await release(); notice(error.message,true); }
  finally {busy=false; $('start').disabled=active;}
});
$('stop').addEventListener('click',endSession);
$('calibrate').addEventListener('click',async () => {
  try { await api('calibrate',{}); notice('Recalibrating: face the screen directly for 20 valid frames.'); }
  catch(error) {notice(error.message,true);}
});
$('export').addEventListener('click',async () => {
  try {
    const report=await api('report');
    const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));
    const link=document.createElement('a'); link.href=url; link.download=`proctor-${report.session_id}.json`; link.click();
    setTimeout(()=>URL.revokeObjectURL(url),5000);
  } catch(error) {notice(error.message,true);}
});
document.querySelectorAll('input[name="answer"]').forEach(input=>input.addEventListener('change',()=>{$('answer-state').textContent='Answer selected locally';}));
for (const name of ['copy','cut','paste']) document.addEventListener(name,event=>{if(active){event.preventDefault();signal('clipboard_blocked');}});
document.addEventListener('contextmenu',event=>{if(active) event.preventDefault();});
document.addEventListener('visibilitychange',()=>{if(document.hidden)signal('tab_hidden');});
window.addEventListener('blur',()=>signal('focus_lost'));
document.addEventListener('keydown',event=>{
  if(event.ctrlKey&&event.shiftKey&&event.key.toLowerCase()==='q'){event.preventDefault();signal('emergency_exit');emergencyEnd();return;}
  if(!active)return;
  if(((event.ctrlKey||event.metaKey)&&['c','v','x','t','n','l','r','w'].includes(event.key.toLowerCase()))||['PrintScreen','F12','F11'].includes(event.key)){
    event.preventDefault();signal('shortcut_blocked');
  }
});
if(isDesktop){window.desktop.onSecurityEvent(code=>{
  if(code==='backend_stopped'){active=false;release();notice('Backend stopped. Protection released. Restart the application.',true);return;}
  signal(code);
}); window.desktop.onEmergency(emergencyEnd);}
function renderEvents(events){
  const key=events.map(e=>e.id).join(','); if(key===lastEventKey)return; lastEventKey=key;
  if(!events.length){$('events').replaceChildren(); const div=document.createElement('div');div.className='empty-state';div.textContent='No signals to review. Sustained events will appear here.';$('events').append(div);return;}
  const rows=events.slice().reverse().map(event=>{
    const row=document.createElement('article');row.className=`event ${event.severity}`;
    const icon=document.createElement('span');icon.className='event-icon';icon.textContent='!';
    const content=document.createElement('div');const title=document.createElement('b');title.textContent=event.title;
    const detail=document.createElement('small');detail.textContent=`${event.source==='simulation'?'SIMULATED':'OBSERVED'} · ${event.code}${event.duration_s?' · '+event.duration_s+'s':''}`;
    content.append(title,detail);const time=document.createElement('time');time.textContent=timeLabel(event.elapsed_s);
    row.append(icon,content,time);return row;
  });$('events').replaceChildren(...rows);
}
async function poll(){
  if(pollBusy)return;pollBusy=true;
  try{
    const data=await api('status');const wasActive=active;active=data.active;mode=data.mode;
    if(wasActive&&!active){await release();notice(data.error||'Session ended. Protection released.',Boolean(data.error));}
    const obs=data.observation||{};
    $('start').disabled=active||busy;$('stop').disabled=!active;$('calibrate').disabled=!active||mode!=='live';$('export').disabled=!data.session_id;
    for(const id of ['mode','camera-index','native-guard','consent'])$(id).disabled=active;
    $('elapsed').textContent=timeLabel(data.elapsed_s);$('session-label').textContent=active?'SESSION '+data.session_id.slice(0,8).toUpperCase():data.session_id?'SESSION ENDED':'NO ACTIVE SESSION';
    $('mode-badge').textContent=active?(mode==='simulation'?'SIMULATION':'LIVE · ON DEVICE'):'STANDBY';
    $('faces').textContent=obs.face_count===undefined?'—':String(obs.face_count);$('face-caption').textContent=obs.face_count===1?'One face in frame':obs.face_count===0?'Presence signal requires review':obs.face_count>1?'Multiple faces - review':'Waiting for session';
    $('gaze').textContent=obs.gaze||'—';$('calibration').textContent=mode==='simulation'&&data.session_id?'Scripted gaze signal':obs.calibrated?'Relative to calibrated baseline':`Calibration: ${obs.calibration_samples||0}/20 frames`;
    $('phone').textContent=obs.phones===undefined?'—':obs.phones.length?'Visible':'Clear';$('event-count').textContent=data.events.length;
    $('signal-dot').classList.toggle('active',active);$('camera-status').textContent=!active?'CAMERA OFF':mode==='simulation'?'SCRIPTED SIGNALS · NO CAMERA':'LOCAL CAMERA';$('latency').textContent=`${data.latency_ms} ms inference`;
    $('model-state').textContent=Object.values(data.models).every(Boolean)?'✓ Local models ready':'Models missing · simulation available';
    $('protection-dot').textContent=active?'●':'○';$('protection-title').textContent=active?(data.native_guard?'Windows hook + '+(isDesktop?'isDesktop guard':'browser guard'):isDesktop?'Desktop guard active':'Browser guard only'):'Protection inactive';
    $('protection-detail').textContent=data.guard_error||'End the session or press Ctrl+Shift+Q to release protection. Managed OS policies are needed for full lockdown.';
    renderEvents(data.events);
    if(active&&mode==='live'){
      const response=await fetch('/api/frame');
      if(response.status===200){const url=URL.createObjectURL(await response.blob());if(frameUrl)URL.revokeObjectURL(frameUrl);frameUrl=url;$('camera').src=url;$('camera').hidden=false;$('camera-placeholder').hidden=true;}
    }else{
      $('camera').hidden=true;$('camera-placeholder').hidden=false;
      if(frameUrl){URL.revokeObjectURL(frameUrl);frameUrl=null;}
      $('placeholder-title').textContent=active?'Simulation in progress':'Ready when you are';
      $('placeholder-text').textContent=active?`Scripted signal: ${obs.face_count} face(s), ${obs.gaze}, ${obs.phones?.length||0} phone(s). Live detection needs a webcam.`:'Live frames stay in memory on this device.';
    }
    if(data.error)notice(data.error,true);
  }catch(error){await release();notice('Connection lost. Protection released. '+error.message,true);}
  finally{pollBusy=false;}
}
poll();setInterval(poll,700);
