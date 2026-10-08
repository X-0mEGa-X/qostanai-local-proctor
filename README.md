# Qostanai Local Proctor

Case 3 prototype for KRU and Qostanai Hub, Qostanai Industry Hackathon 2026. Local webcam inference, a protected desktop exam window, and a timeline of signals for human review.

**Latest release review:** [verified checks and remaining human tests](docs/RELEASE_REVIEW.md). [Presentation PDF](submission/presentation.pdf) and [editable PPTX](submission/presentation.pptx).

**Start with [the current team plan](docs/TEAM_PLAN.md).** Copy the prompts from your own guide:

| Member | Responsibility | Prompt guide |
| --- | --- | --- |
| Captain + Codex / Pro account | Engineering, integration, presentation and submission packaging | [Development](docs/prompts/MEMBER_1_PRO.md) |
| Member 2 / Plus | Product testing, live test matrix, demo recording | [Member 2](docs/prompts/MEMBER_2_PLUS.md) |
| Captain + Codex (former Member 3 duties) | Six-slide PDF/PPTX, pitch, pilot and jury answers | [Presentation guide](docs/prompts/CAPTAIN_PITCH.md) and [timed script](docs/PITCH.md) |

## Run on Windows

Install **Python 3.12**, Node.js LTS and Git. Accept the repository invitation before cloning this private repository. The included Windows dependency lock was checked with Python 3.12.

```powershell
git clone https://github.com/X-0mEGa-X/qostanai-local-proctor.git
cd qostanai-local-proctor
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
npm start
```

On the captain's current laptop, dependencies are already installed. Launch with `powershell -ExecutionPolicy Bypass -File scripts/start.ps1`; this also works when Node is available through Codex but npm is not on PATH.

The setup command downloads CPU PyTorch, Python dependencies, Electron and two pretrained models. It needs internet once and may take several minutes. Webcam inference and event reporting then run locally without any OpenAI API key. In Electron, choose **Live**, consent, start, and face the screen for 20 valid frames. The optional Windows guard blocks selected keys while the session is active. **End session** or **Ctrl+Shift+Q** releases protection. The UI heartbeat watchdog also ends a session when the UI stops responding. Ctrl+Alt+Delete remains an OS recovery route.

For browser preview or backend development:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`. Browser preview provides only limited protection. Do not run this backend command concurrently with `npm start`, which launches its own backend.

**Simulation** produces scripted face, gaze and phone signals without opening a webcam. It is a rehearsal and software test, not evidence of detector accuracy.

## What is implemented

- YOLOv8n COCO class 67 phone bounding boxes and confidence.
- MediaPipe Face Landmarker face mesh: face count, calibrated iris/head proxy, sustained downward/side signals.
- Debounced events: phone visible, phone raised, no face, multiple faces, down/side gaze and environment events.
- Electron navigation/window restrictions, kiosk exam mode and clipboard restrictions.
- Optional reversible Windows low-level keyboard hook: Alt+Tab, Windows keys, PrtScn, Ctrl+C/V, Alt+Esc and Ctrl+Esc.
- Session metadata JSON export; no video or snapshots are saved. Reports are kept under ignored `data/` until manually deleted.

## Limits that matter for judging

Phone detection cannot prove that a shutter fired or that a camera points at the monitor. The raised-phone rule is a bounding-box position heuristic. Gaze is a calibrated estimate that needs validation across people, glasses and lighting. MediaPipe counts faces; standard COCO YOLO has a person class but no face class. This prototype does not train a separate face model.

Electron and key hooks do not establish complete OS lockdown: other displays, elevated applications, remote access, Ctrl+Alt+Delete and other screen capture methods can bypass them. We do not terminate outside programs. Managed Windows exam accounts and institutional OS policies are required for a deployment that blocks all outside windows and browsers. Flags are for human review, not automatic cheating verdicts.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
npm test
.\.venv\Scripts\python.exe scripts/check_vision.py
```

`check_vision.py` uses a generated blank frame to check that both models load and execute. It does not validate real-world accuracy. [Manual tests](docs/QA_CHECKLIST.md) must be completed on a real webcam before calling the live demo validated.

See the [8 October release review](docs/RELEASE_REVIEW.md) for fixed defects, presentation claims and five human checks. The latest [validation record](docs/VALIDATION.md) documents 26 passing Python tests, 2 passing Node checks, API integration, actual desktop report download, session isolation and renderer-crash recovery. Human webcam and physical Windows shortcut results remain pending.

For measured human trials, use the [guided live validation procedure](docs/LIVE_VALIDATION.md) and open `http://127.0.0.1:8765/?validate=1` after starting the local backend. It adds timed cues and metadata-only trial results. The [proposed KRU pilot](docs/PILOT_PLAN.md) describes supervision, accessibility, managed Windows controls and evaluation measures.

## Project map

`backend/`: vision, temporal rules, local API, Windows hook. `desktop/`: Electron isolation and window protection. `frontend/`: dashboard and sample exam. `docs/`: requirements, architecture, team plan, prompts, pitch and submission checklist. `scripts/`: setup, downloads and diagnostic checks.

See [architecture and disclosures](docs/ARCHITECTURE.md) and [case/rules summary](docs/CASE_AND_RULES.md). External software has its own licensing, including Ultralytics AGPL-3.0 and pretrained model terms. No blanket license is assigned to the whole project; the team retains its original work, subject to dependency obligations.
