# Prototype validation status

## Guided live validation preparation on 8 October 2026

The guided recorder passes 22 Python tests, including six new checks for confirmation, metadata-only storage, missed/unexpected events, direction mismatches, incomplete/early trials and second-person consent. The 2 Node policy tests, API integration and Electron smoke checks also pass after this addition. The Electron check ran on a separate local port in simulation, including actual JSON download and recovery after a failed page stop request or renderer crash.

The new live page at `/?validate=1` provides a five-second cue countdown, 60 seconds of normal screen use and eight-second scenario trials. Per-frame processing median/p95 and cue-to-event delay are distinct measurements. The latter includes participant reaction and dwell time. Left/right ground truth refers to the participant. No detector sign or threshold was changed without live evidence.

**Human results are pending.** No participant trial was completed during preparation. The idle local service is ready; the camera opens only when the user consents and starts Live. No camera footage was saved or uploaded. Future confirmed results belong in a separate dated entry, keeping any private metadata reports outside Git.

See [the guided procedure](LIVE_VALIDATION.md) and [proposed KRU pilot](PILOT_PLAN.md).

## Audit on 8 October 2026

The working tree was clean before this audit. Existing teammates' changes were not overwritten. The following checks ran locally after the fixes; participant webcam accuracy and physical keyboard interception remain unmeasured.

| Check | Result | Scope |
| --- | --- | --- |
| Python suite | 16 passed | Temporal rules, clean model inputs, calibration reset and synthetic iris directions, fake camera failure/cancellation, storage failure, watchdog and fake Windows hook cancellation |
| Node policy suite | 2 passed | Selected shortcut policy, emergency exemption and navigation boundary |
| API integration | Passed | Auth/origin/consent checks, invalid/duplicate start rejection, simulated phone events, environment source labels, ended local JSON and export, inactive calibration rejection |
| Electron integration | Passed | UI start, emergency cancel/restart, actual Export-button JSON download, failed page Stop-request recovery, renderer crash with main-process session release |
| Actual models on a generated 640×480 blank frame | Passed; 0 faces and 0 phones | Both downloaded models execute on this Windows laptop; this is not a participant accuracy trial |
| Dependency consistency | `pip check` passed | Installed Python dependencies satisfy their requirements |
| Visual inspection | Top and bottom screenshots inspected | Controls, timeline, source labels and report button render without observed overlap |

Before fixes, the new failure-path tests produced four failures and two errors. Confirmed defects included phone overlays entering face inference, stale calibration progress after face loss, camera opening after a canceled model load, cleanup exceptions leaving sessions active, and unhandled report write failures. The fixed suite passes. Additional recovery checks cover a canceled hook installation and a crashed renderer. The renderer crash test deliberately triggers a Chromium crash diagnostic; its final recovery assertions passed.

Reproduce with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test tests/desktop.test.cjs
.\.venv\Scripts\python.exe scripts/check_api.py
.\.venv\Scripts\python.exe scripts/check_vision.py
node node_modules/electron/cli.js . --smoke-test
.\.venv\Scripts\python.exe -m pip check
```

API and desktop checks use simulation and leave private test reports under ignored `data/` and `output/qa/`. Unit tests substitute fake camera/model/hook outputs. The vision execution check loads real models but never opens a webcam. No human scenario counts, real-world accuracy, measured webcam FPS, cost savings or completed university pilot are supported by this audit.

The dashboard's live processing value covers a frame iteration, including capture, model processing and JPEG encoding; it is not an FPS benchmark. Simulation now displays “Scripted · no inference” rather than an inference-time claim. Security events use source `environment`; scripted vision uses `simulation`; webcam vision uses `live`.

Current demo blockers and the short human test list are in [DEMO_AUDIT.md](DEMO_AUDIT.md). The six-slide presentation outline is in [PITCH.md](PITCH.md).

## Earlier checks on 7 October 2026

Checks executed on the captain's Windows laptop on 7 October 2026. These results establish software behavior and model execution. Real participant webcam accuracy has not been validated.

| Check | Observed result | What it establishes |
| --- | --- | --- |
| Python temporal-rule tests | 4 passed | Dwell thresholds, reset/re-arm, frame-gap reset, phone/multiple-face signals |
| Node desktop policy tests | 2 passed | Selected shortcut decisions, emergency exemption, exact navigation boundary |
| API integration | Passed | Cookie/origin/consent validation, invalid/duplicate start rejection, simulation phone events, local report persistence and export |
| Electron UI integration | Passed | Actual UI start, desktop bridge, model readiness, scripted phone events, Ctrl+Shift+Q UI release, ended report and disabled stop control |
| Visual UI inspection | Top and bottom screenshots inspected | Dashboard, controls and review timeline render without observed overlap |
| Vision execution on a blank generated frame | Both models loaded and executed; 0 faces / 0 phones | YOLO and MediaPipe are executable on this machine; not sensitivity/accuracy |
| Windows hook lifecycle | Registered successfully; stopped; thread exited | Hook can install and release; no physical shortcut interception claim |
| Independent heartbeat watchdog | Expired session ended and protection released; stopped timer stayed stable | Recovery works independently of the vision worker; no participant camera needed |
| Dependency consistency | `pip check` passed; npm audit reported 0 vulnerabilities in 14 packages | Installed Python dependencies satisfy declared constraints; npm audit applies to that dependency graph only |

The project uses a Cyrillic Windows folder. MediaPipe's native model-path loader failed on that path; loading the model bytes into `BaseOptions` resolved the model execution check.

## Human checks pending

Real phone/face/gaze detection, direction signs, glasses/lighting robustness, real keyboard interception, camera removal/recovery, actual offline trial, fresh setup on a second laptop, measured inference latency and a consented real demo recording are pending. No accuracy, reviewer-time savings or production-lockdown claim is supported by this starting validation.

Member 2 should extend this record with actual device details, sample counts and outcomes using `docs/QA_CHECKLIST.md`. Keep simulation events separate from observed webcam results. Private test reports and diagnostic screenshots remain outside version control.
