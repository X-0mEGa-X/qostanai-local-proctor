# Release review - 8 October 2026

## Evidence found and preserved

The main checkout began clean at commit `1083d9b`. Fetching GitHub found only `main`, with no new teammate branches or pull requests. At audit start, all 30 local JSON reports were simulation reports, with zero guided trials or human confirmations. Those reports are software-run artifacts, not 30 participant trials. No human observations were supplied in this conversation.

The other local GPT task, titled `open it`, inspected the checkout at `C:/Users/Admin/Documents/GitHub/qostanai-local-proctor`. It reported no human webcam or physical shortcut results. Its history does not identify it as Member 2. That checkout is at `6964155` and contains an unrelated staged `.vscode/launch.json` plus a static HTML preview. Both were preserved. Its QA checklist says Not run. No teammate result or presentation existed to merge. No other person's GPT account was accessed.

The captain and Codex now own all former Member 3 duties. Member 2 retains QA and demo operation. No third person or completed handoff is assumed.

## Reproduced defects and corrections

1. **Delayed stop ended a restarted session.** The API ignored the supplied old session ID. A regression started A, stopped A, started B, then sent A's delayed stop. B incorrectly ended. Stop/security requests now require an originating session ID and ignore stale IDs. Electron binds emergency recovery to the protected session and waits for pending recovery before a new UI start. The API and Electron regressions pass.
2. **A stalled trial could be reported as assessable.** One sample at the beginning of a 60-second normal trial, followed by status-only completion and human confirmation, returned `assessable=true`. Reports now mark any gap over two seconds inconclusive, including gaps at the beginning/end. Missing-event and unexpected-event assessments remain null for such trials, while observations remain available.
3. **Recalibration could change a running measurement.** The API now rejects recalibration during a countdown or measurement. The trial must finish before a new baseline can be requested.

Additional failure-path tests confirmed existing cleanup behavior: unavailable camera, failed frame read, model load failure and camera cleanup exception release the fake guard, save an inactive error report, permit a fresh session and preserve the old report. No detection thresholds or gaze signs were changed without human evidence.

## Checks run after corrections

| Category | Actual result | Limits |
| --- | --- | --- |
| Automated Python | 26 tests passed | Synthetic observations and fake hardware; no real webcam |
| Automated Node | 2 policy tests passed | Shortcut decisions, not physical key interception |
| API integration | Passed once after the session-ID fix | Scripted phone events, cookie/origin/consent checks, ended saved/exported report, restart, stale stop and stale security isolation |
| Electron integration | Passed once after all code changes | Actual UI, simulation, valid downloaded JSON, release, restart, canceled start, failed page stop, forced renderer crash, delayed main-process emergency and stale stop |
| Model execution, historical | Both models executed on one generated 640x480 blank frame, returning zero faces/phones | Executability only; not human detection performance |
| Windows hook, historical | Registered, stopped, thread exited | No physical guarded-key tests |
| Human webcam trials | 0 documented/confirmed | Phone, raised phone, neutral, gaze, absence and second-face outcomes unknown |
| Physical Windows shortcuts | 0 documented trials | Interception and physical emergency release unknown |

An initial API regression failed before the fix. A first Node invocation used an incorrect test filename; the corrected `node --test tests/desktop.test.cjs` ran both tests successfully. Electron printed a Chromium diagnostic during its intentional renderer crash; all assertions passed and the process exited successfully.

Device: captain's i5-1135G7 2.40 GHz, approximately 8 GB RAM (7.7 GiB reported), Windows 11 Home Single Language 10.0.26200. Camera model and lighting are unknown. Electron smoke used simulation with the native Windows hook unchecked on separate port 8767. API used port 8766. This audit did not open the webcam, save footage or upload footage. No live latency, FPS, false-alert rate, accuracy or reviewer-time improvement was measured.

## Presentation claim audit

| Slide | Claim and evidence | Boundary |
| --- | --- | --- |
| 1 | Case 3 problem and assigned roles, from case summary and user's instruction | Project title used; personal names/team registration identity still need the captain's check |
| 2 | Requirement mapping to vision, rules, desktop policy and report code | Photography proof, outside-app lockdown and human validation explicitly incomplete |
| 3 | Loopback API, local models, RAM preview and JSON metadata | Guided numeric samples and notes are also stored; no footage recorded |
| 4 | 26 Python and 2 Node tests, API/Electron results above; actual simulation screenshot | Zero recorded human trials; no accuracy or live-latency claim |
| 5 | Five volunteers, two laptops, 20 minutes as proposed pilot parameters | No pilot completed or agreed; benefits are hypotheses |
| 6 | Coarse gaze, phone-position heuristic, incomplete lockdown, external models/libraries and AI assistance | No custom detector training, certification or university adoption claimed |

The six-slide PDF and editable PPTX are in `submission/`. `PITCH.md` contains the timed script and judging map; `JURY_QA.md` contains defensible answers; `PILOT_PLAN.md` contains the operational proposal and primary Microsoft sources. All six PPTX slides were rendered and visually inspected. The PPTX package/layout checks passed with no findings. The PDF contains six rendered slide pages. It is a presentation copy; text and diagrams remain editable in the PPTX. Native PowerPoint playback and a timed human rehearsal still need checking.

## Human release gate

1. Run the guided LIVE matrix: normal 60 seconds, phone, raised phone, down, participant-left/right, absence and a second consenting face. Record actual results and failures, not just expected events. Repeat phone/gaze scenarios at least three times when time allows and report the actual denominator.
2. In Electron, separately test End and physical Ctrl+Shift+Q, including during startup and immediately before restart. With the optional Windows guard enabled, test Alt+Tab, Win, PrtScn and Ctrl+C/V, then verify normal key behavior returns. Record every failure and physical release time.
3. Try an unavailable camera index and, if an external camera is available, disconnect it. Verify visible error, camera closure, guard release, restart and an inactive exported report. Never report fake-camera tests as this result.
4. Open the exported JSON and match its session ID, ended time, source labels, observed events and guided trial notes. Check the old session report remains intact after restart.
5. Rehearse the whole three-minute pitch offline after setup, open the PDF/PPTX on the presentation laptop, and add the actual registered team identity if required. Until human detection succeeds, demonstrate simulation with its label visible.

Operational deployment remains blocked by missing human evidence, incomplete managed Windows policies, no LMS integration, and no institutional report access controls or signed evidence. This is a hackathon prototype. The documents do not authorize submitting it or contacting KRU.
