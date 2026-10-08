# Demonstration readiness audit — 8 October 2026

## What works in the verified scope

- Real YOLOv8n and MediaPipe models load and execute on a generated blank frame on this laptop.
- Temporal rules produce phone, raised-phone, absence, second-face and sustained gaze events with synthetic inputs. Calibration, reset and relative iris-direction logic pass deterministic tests.
- The local API enforces its cookie/origin/consent boundary and exports ended reports. Simulation vision and actual environment events carry separate source labels.
- Electron starts the app, restricts its navigation and selected shortcuts, supports cancel/restart, downloads JSON through the actual Export button and releases a session after a forced renderer crash.
- Failure tests confirm release during fake camera cleanup failure, canceled model loading, report storage failure and a canceled Windows hook installation. The watchdog runs separately from vision.

## Defects fixed

| Defect | Fix |
| --- | --- |
| Phone overlays contaminated the face model's input | Both detectors receive clean pixels; drawing uses a separate output frame |
| Face loss displayed stale calibration sample counts | Reset reported progress with the stored samples |
| Canceling during model load still opened the camera | Check cancellation before opening the camera; discard late results after stop |
| Camera cleanup errors could skip session/protection release | Release first, attempt each cleanup independently and retain errors in the report |
| Report write errors could strand an active session or prevent export | Check storage before protection starts; expose later failures and retain an in-memory export |
| Delayed native hook installation could enable after stop | Latch cancellation, create the message queue early and unhook a canceled installation |
| Emergency recovery depended on the renderer | Main process authenticates directly to the local stop API; if it cannot stop its backend, it terminates that owned child process |
| UI requests could hang, retain old camera pixels or reuse an old session's timeline | Bound request time, clear unavailable/stopped frames and key events by session |
| Simulation latency and environment source labels could mislead a presenter | Label scripted mode without inference time and separate environment events |

The dependency workflow now installs lightweight test dependencies and runs API integration in CI. Full vision models and Windows hardware remain outside that Linux job. See [VALIDATION.md](VALIDATION.md) for observed local results, not a promise that future hardware trials will pass.

## Incomplete work and demonstration risks

1. **Live vision is not validated.** Phone orientation/occlusion, head-pitch sign, glasses, lighting, second-face tracking and actual processing speed may cause misses or false flags. No real accuracy percentage is available.
2. **Physical protection and recovery need target-laptop testing.** Software tests and a fake hook do not prove Alt+Tab/Win/PrtScn interception. Complete blocking of outside applications, alternative capture tools and elevated windows is not implemented.
3. **Photography remains a partial requirement.** The raised-phone box heuristic cannot establish camera aim or shutter action.
4. **Deployment is still a prototype.** Fresh setup, disconnected-network operation and a consented real demo recording are pending. Models and large dependencies must be installed before the event. There is a sample exam, no LMS integration, no institutional authentication or signed evidence log, and no completed university pilot.
5. **Failure can limit report recovery.** If report storage fails, export while the process remains alive. Forced process termination may lose in-memory events after the last saved snapshot. A stuck driver may require restarting the app before starting another session.

## Human tests required before a live presentation

| Test | Short procedure | Record / pass condition |
| --- | --- | --- |
| Phone | In LIVE mode, show one phone for 3 s at several angles and heights, removing it between trials | Actual phone/raised events and delays; document misses, not an assumed accuracy |
| Face and gaze | Calibrate, remain neutral for 60 s, look down/left/right for 5 s each, try a brief glance, leave for 5 s, then add a second consenting face for 3 s | Correct baseline/directions and face-count events; count unexpected flags; repeat after recalibration |
| Protection and recovery | With Windows guard enabled, try Alt+Tab, Win, PrtScn and Ctrl+C/V. Test End session and Ctrl+Shift+Q separately, including during startup | Keys/windows behave as intended; desktop and camera recover every time. Ctrl+Alt+Delete remains available |
| Failure and report | Use an unavailable camera index, and disconnect an external camera if available. Then complete a normal live session and export JSON | Error is visible, protection releases, exported session is inactive with ended time, source labels and the observed events |
| Offline rehearsal | After setup, disconnect the network and rehearse the complete 180-second pitch/demo on the presentation laptop | Both models run, controls work, exported file opens, and the pitch fits. Test a fresh clone on a second laptop if it is the backup device |

Record device/camera, conditions, attempts, expected and actual events, latency and recovery outcome in [QA_CHECKLIST.md](QA_CHECKLIST.md). Keep consented face evidence and session reports outside Git. Never label simulation as live detection.
