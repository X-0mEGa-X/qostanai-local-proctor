// Timed human actions with server-side per-frame metadata, never image recording.
if (new URLSearchParams(window.location.search).has('validate')) {
  $('validation-panel').hidden = false;
  $('mode').value = 'live';
  const actions = {
    normal:'Use the screen normally for 60 seconds. Read the sample question and blink naturally. Keep phones out of view.',
    phone:'Show a phone clearly in the camera view for 8 seconds. Keep your face visible. This is a visibility test.',
    raised_phone:'Raise the phone near the laptop screen, visibly inside the webcam image, for 8 seconds. Keep your face visible. Do not take a photo.',
    down:'Look down for 8 seconds, then return to the screen. Keep your face within the camera view.',
    left:'Look to YOUR left for 8 seconds, then return to the screen. The preview image does not define left/right.',
    right:'Look to YOUR right for 8 seconds, then return to the screen. The preview image does not define left/right.',
    absence:'Move fully out of the camera view for 8 seconds, then return. No other person should be in frame.',
    second_face:'Have the second consenting person enter the webcam view for 8 seconds while you remain visible, then leave.'
  };
  let currentState, guidePolling = false, guideBusy = false;
  function showSelection() {
    $('second-consent-row').hidden = $('trial-scenario').value !== 'second_face';
    if (!['countdown','measuring'].includes(currentState)) $('trial-instruction').textContent = actions[$('trial-scenario').value];
  }
  $('trial-scenario').addEventListener('change', showSelection);
  $('trial-start').addEventListener('click', async () => {
    if(guideBusy)return; guideBusy=true; $('trial-start').disabled=true;
    try { await api('trial', {scenario:$('trial-scenario').value, second_person_consents:$('second-consent').checked}); }
    catch(error){notice(error.message,true);}
    finally {guideBusy=false;await guidePoll();}
  });
  async function confirm(completed) {
    if(guideBusy)return;guideBusy=true;
    try {
      const confirmed=await api('trial/confirm',{completed,notes:$('trial-notes').value});
      $('trial-notes').value='';$('second-consent').checked=false;
      if(confirmed.current.assessable && $('trial-scenario').selectedIndex < 7) $('trial-scenario').selectedIndex++;
      showSelection();
    }catch(error){notice(error.message,true);}
    finally{guideBusy=false;await guidePoll();}
  }
  $('trial-confirm').addEventListener('click',()=>confirm(true));
  $('trial-incomplete').addEventListener('click',()=>confirm(false));
  async function guidePoll() {
    if(guidePolling)return;guidePolling=true;
    try {
      // This observer must not extend the protection watchdog if the main UI stalls.
      const data=await api('status?heartbeat=false');
      const trial=data.validation.current;
      currentState=trial?.state;
      const running=['countdown','measuring'].includes(currentState);
      $('trial-start').disabled=guideBusy||!data.active||data.mode!=='live'||!data.observation.calibrated||running||currentState==='awaiting_confirmation';
      $('trial-scenario').disabled=running||currentState==='awaiting_confirmation';
      $('trial-confirmation').hidden=currentState!=='awaiting_confirmation';
      $('trial-confirm').disabled=guideBusy;$('trial-incomplete').disabled=guideBusy;
      if(running){
        $('trial-state').textContent=currentState==='countdown'?`GET READY · ${data.validation.remaining_s}s`:`DO NOW · ${data.validation.remaining_s}s left`;
        $('trial-instruction').textContent=currentState==='countdown'?'Stay centered. Keep the phone out of view and the second person outside the frame. Wait for DO NOW.':actions[trial.scenario];
      }else{
        $('trial-state').textContent=currentState==='awaiting_confirmation'?'DONE · confirm what happened':!data.active?'Start a live session first':!data.observation.calibrated?'Look straight ahead · calibrating':'Ready for the selected trial';
        showSelection();
      }
      if(trial){
        const evidence=trial.assessable?`Missed event types: ${trial.missed_event_types.join(', ')||'none'}. Unexpected alerts: ${trial.unexpected_event_count} (${trial.unexpected_event_types.join(', ')||'none'}); review with your notes.`:'Not assessed: confirmation, valid timing and samples with no gap over 2 seconds are required.';
        const warnings=[trial.early_signal?'Expected signal appeared before the cue. Note whether you acted early or the detector was wrong, then repeat.':'',trial.interrupted?'Session interrupted this trial.':''].filter(Boolean).join(' ');
        $('trial-result').textContent=`Trial ${trial.number}: ${trial.scenario}. ${trial.processed_frames} processed frames. Largest sample gap: ${trial.max_sample_gap_s}s. Processing p50/p95: ${trial.processing_ms_p50??'—'} / ${trial.processing_ms_p95??'—'} ms. Gaze counts: ${JSON.stringify(trial.gaze_counts)}. ${evidence} ${warnings}`;
      }
    }catch(error){$('trial-state').textContent='Test connection unavailable';$('trial-start').disabled=true;}
    finally{guidePolling=false;}
  }
  guidePoll();setInterval(guidePoll,400);
}
