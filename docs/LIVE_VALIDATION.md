# Guided live validation

This procedure records event and timing metadata without saving camera footage. The test uses each participant's own left/right direction. A result remains unconfirmed until the participant reports completing the action. Synthetic checks must not be presented as human measurements.

## Vision trials

Start the local service and open `http://127.0.0.1:8765/?validate=1`. Browser mode allows communication during vision testing and has limited protection. Choose Live, leave Windows key protection unchecked, consent and start the session. Look normally at the screen until the 20-frame calibration finishes.

For every trial, return to one face, centered gaze and no phone. Wait three seconds before clicking **Start trial**. Stay neutral during the five-second countdown. Perform the selected action only at **DO NOW**, hold it until **DONE**, then return to normal. Confirm whether you completed the action, and add factual notes about delays or unexpected behavior.

| Trial | Action after the cue | Duration | Expected event |
| --- | --- | ---: | --- |
| Normal | Read the screen normally, blinking naturally, without a phone | 60 s | No vision alerts; record every unexpected one |
| Phone | Hold a clearly visible phone while keeping your face visible | 8 s | `phone_visible`; raised-phone may also appear depending on position |
| Raised phone | Raise the phone near the laptop screen while it remains visible to the webcam | 8 s | `phone_visible` and `phone_raised`; no photography claim |
| Down | Look down, keeping your face within view | 8 s | `look_down`, with down gaze labels |
| Left | Look to your own left | 8 s | `look_side`, with left gaze labels |
| Right | Look to your own right | 8 s | `look_side`, with right gaze labels |
| Absence | Move fully out of view with nobody else in frame | 8 s | `no_face` |
| Second person | A second consenting person enters while you remain visible | 8 s | `multiple_faces`; the second-person consent checkbox is required |

If the second person is unavailable, leave that scenario untested. After a missed or reversed result, record it before repeating. Do not silently recalibrate or tune thresholds to turn that same trial into a success. A follow-up can separate eye-only motion from head turns, using notes to identify the condition.

## Ending and protection release

End the vision session and export its report before starting another session. Check that the preview disappears and the camera indicator turns off. Report any delay or failure; software status alone does not prove physical closure.

For a separate desktop protection trial, the standalone backend must first stop so Electron can launch its own service. Launch with `scripts/start.ps1`. Consent and start a live session with the optional Windows guard enabled. Test **End & release protection** and **Ctrl+Shift+Q** in separate sessions. Confirm that the camera closes, the desktop is usable and normally restricted keys work again. Keep Ctrl+Alt+Delete available as the OS recovery route. A browser-only test does not establish desktop or native-hook behavior.

## Recorded evidence and limitations

The existing `data/<session-id>.json` report now includes `validation.trials`. Numeric/categorical samples contain relative time, processing time, face count, gaze label, pose/iris deltas and phone/raised counts. They contain no images, video, audio or face landmark arrays. Data remains outside Git. The detector's save, crop, text-output and display options are explicitly disabled.

Processing median/p95 covers capture through JPEG encoding for measured iterations. Cue-to-event delay includes human reaction and the configured duration threshold; it is not exact physical action-to-alert latency. Trial frame rate describes this small measured interval. Do not infer population accuracy from it.

After confirmation, the report lists missing required event types and unexpected event types for review. Unexpected does not automatically mean false: participant notes, transitions and accommodations still need interpretation. Gaze label counts and the expected-label fraction help detect reversed directions; they are not calibrated eye-tracker accuracy. Interrupted trials, missing samples, any sample gap over two seconds (including start/end coverage) and expected signals appearing before the cue remain inconclusive, with their observations retained. Recalibration is blocked while a trial counts down or measures.

`python scripts/read_live_status.py` reads metadata only and does not extend the UI heartbeat watchdog. It never requests camera frames. Complete private reports can be inspected locally; publish only an agreed anonymized aggregate.

## Current human results

No participant trial has been completed or confirmed as of the preparation of this guide. Phone, raised phone, down/left/right, absence, second-face and physical release outcomes are pending. Do not copy synthetic test outcomes into these results.
