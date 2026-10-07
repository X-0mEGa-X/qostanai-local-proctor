# Prototype validation status

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
| Dependency consistency | `pip check` passed; npm audit reported 0 vulnerabilities in 14 packages | Installed Python dependencies satisfy declared constraints; npm audit applies to that dependency graph only |

The project uses a Cyrillic Windows folder. MediaPipe's native model-path loader failed on that path; loading the model bytes into `BaseOptions` resolved the model execution check.

## Human checks pending

Real phone/face/gaze detection, direction signs, glasses/lighting robustness, real keyboard interception, camera removal/recovery, actual offline trial, fresh setup on a second laptop, measured inference latency and a consented real demo recording are pending. No accuracy, reviewer-time savings or production-lockdown claim is supported by this starting validation.

Member 2 should extend this record with actual device details, sample counts and outcomes using `docs/QA_CHECKLIST.md`. Keep simulation events separate from observed webcam results. Private test reports and diagnostic screenshots remain outside version control.
