# Six-slide outline for a three-minute presentation

Presenter and pitch owner: Member 3, with Codex supporting the draft. Member 2 operates the demonstration; the captain supports technical questions. This is an outline, not the final presentation PDF. Use the actual team name and three members' names on slide 1.

Evidence: the implementation and checks recorded on 8 October 2026 in [VALIDATION.md](VALIDATION.md). Participant webcam trials remain pending. Requirements and judging weights come from the supplied Case 3 brief and hackathon rules, summarized in [CASE_AND_RULES.md](CASE_AND_RULES.md).

## 1. Team and problem — 0:00–0:20

**Title:** Qostanai Local Proctor

**On the slide:** Team name; three names and roles; Case 3, KRU and Qostanai Hub. Reviewers need evidence of phones, absence and sustained off-screen attention during a computer exam.

**Say:** “We are [team name], a team of three. We chose Case 3 from KRU and Qostanai Hub. Our prototype brings local webcam signals and exam-window events into one review timeline. A person reviews the evidence and decides what it means.”

## 2. Case requirements and our approach — 0:20–0:45

**Title:** Case requirements and coverage

| Case need | Current approach |
| --- | --- |
| Phone in view or raised near the screen | YOLOv8n phone detection and a position heuristic |
| Presence, second face and sustained down/side gaze | MediaPipe face count and calibrated head/iris features with dwell thresholds |
| Exam protection | Electron navigation/clipboard controls and an optional Windows keyboard hook |
| All functions together locally | Desktop dashboard and timestamped JSON review report |

**Say:** “YOLO detects phones. MediaPipe provides face counts and head and iris features. Signals must persist before entering the review timeline. The desktop restricts navigation and clipboard use, with optional Windows key interception. Phone photography and complete control of outside applications remain partial requirements.”

Evidence: case mapping, `backend/vision.py`, `backend/rules.py`, `desktop/policy.cjs`, `backend/windows_guard.py`.

## 3. Local system architecture — 0:45–1:10

**Title:** Processing on the exam laptop

**On the slide:** One flow connecting webcam frames in memory, Python/OpenCV, YOLO and MediaPipe, temporal rules, the Electron dashboard and a local JSON report. Show the separate exam-control path and emergency release. The local API binds to `127.0.0.1`.

**Say:** “The Python service processes camera frames on the laptop. YOLO and MediaPipe feed sustained-signal rules. Electron displays the exam and review timeline. Reports contain event metadata, while camera frames stay in memory. Our contribution is the integration of calibrated signals, transparent reports and reversible protection. We use existing pretrained models.”

Evidence: [ARCHITECTURE.md](ARCHITECTURE.md). No cloud inference or custom model training is implemented. Offline operation after setup still needs the human trial.

## 4. Actual prototype and measured results — 1:10–2:15

**Title:** Prototype demonstration and verified checks

**On the slide:** The real application or a consented recording clearly labeled with its capture date. Evidence strip: **22 Python tests and 2 Node tests passed. API and Electron checks passed. Actual JSON download and renderer-crash release passed. Live accuracy: not measured.** Test counts describe software checks, not detection accuracy.

Before the pitch, Member 2 starts a consented live session and calibrates with the actual demonstrator. Allow first model loading outside the three-minute slot. Use this sequence only after it passes the human rehearsal:

| Time within this slide | Action and visible evidence |
| --- | --- |
| 0–6 s | Show LIVE mode and completed calibration |
| 6–14 s | Hold a phone for at least 3 s; show its timeline entry |
| 14–23 s | Look down for 5 s, then center; show the signal if detected |
| 23–31 s | A second consenting participant enters for 3 s; show the face-count event |
| 31–42 s | Attempt a previously tested clipboard action; show its environment event |
| 42–53 s | Ctrl+Shift+Q; confirm release; export the ended JSON report |
| 53–65 s | State verified checks and their limits |

**Say while operating:** “These are the app's actual outputs. Each event carries its time and source. Our automated checks pass, including report download and recovery after a page crash. Both models also executed on a generated blank frame. We have not established participant detection accuracy.”

**Measured results available now:** 22/22 Python and 2/2 Node checks passed. The generated 640×480 blank-frame model check returned zero faces and zero phones. The desktop test downloaded a valid ended-session report and confirmed release after a forced renderer crash. These tests did not use a participant webcam or physically press guarded keys. No measured webcam FPS, accuracy or savings are available.

**Fallback:** Show a consented recording of a real run if one exists. Otherwise label the app SIMULATION and state that vision signals are scripted. Do not present test fixtures, scripted confidence values or simulation processing time as live measurements. Never claim a missed event was detected.

## 5. Proposed university pilot and expected benefits — 2:15–2:40

**Title:** Proposed supervised university pilot

**On the slide:** A proposal: 5 consenting volunteers, 2 university Windows laptops, 20-minute practice sessions. Compare timestamped scenario notes with reports. Measure scenario misses, false flags, processing time and successful recovery. Compare reviewer time against the same scripted sessions reviewed manually.

**Say:** “We propose a supervised practice pilot with five volunteers on two university laptops. We would measure scenario misses, false flags, processing time and recovery, then compare reviewer effort. Local processing may reduce the need to transfer footage, and timestamps may help reviewers find relevant moments. These benefits still need measurement.”

Pilot conditions: university permission, consent, an agreed retention policy and accommodations, a supervisor present, no automatic penalties. Recovery and report checks must pass before operational assessment. Size and duration are proposed parameters, not completed work or an agreement.

## 6. Limitations, external components and next steps — 2:40–3:00

**Title:** Limits and next steps

**On the slide:** Gaze/head proxy needs validation. Raised phone cannot establish photography. OS lockdown and signed evidence logs are unfinished. Credit YOLOv8n/COCO, MediaPipe, OpenCV/PyTorch, FastAPI and Electron. Disclose Codex/ChatGPT assistance. Next: live validation, supervised pilot and managed exam policies.

**Say:** “Gaze remains approximate, and a raised phone does not prove photography. Complete OS lockdown is unfinished. We disclose pretrained YOLO, MediaPipe and our software libraries, plus Codex and ChatGPT assistance. Our next step is live validation, followed by a supervised university pilot and deployment review.”

Evidence: architecture, dependency manifests and validation record. Dependency/model licensing must be reviewed before institutional distribution. No original detector training, certification or university adoption is claimed.

## Judging coverage

| Criterion | Points | Evidence |
| --- | ---: | --- |
| Case fit | 15 | Slides 1–2 map the requirements and disclose partial coverage |
| Technical implementation | 20 | Slide 3 shows actual modules and local data flow; slide 4 shows verified behavior |
| Deployment potential and effect | 20 | Slide 5 proposes a pilot, measurements and deployment conditions |
| Innovation | 15 | Slides 2–3 describe the team's integration and calibrated review workflow; slide 6 credits existing models |
| Working prototype and demo | 15 | Slide 4 shows the app, report and recovery, with truthful fallback labels |
| Pitch and answers | 15 | Six slides total 180 seconds; Member 3 narrates, Member 2 operates, captain supports technical questions |

## Short jury answers

- **What accuracy do you have?** Software checks and model execution pass. Participant detection accuracy is unmeasured. The pilot will report conditions, trial counts, misses and false flags separately.
- **Does looking away mean cheating?** No. It creates a review signal after the duration threshold. Human judgment and accommodations remain necessary.
- **Can you prove a photo was taken?** No. Box position and area indicate a raised phone. Camera aim and shutter action are unresolved.
- **Can protection be bypassed?** Yes. Other capture methods, elevated applications and OS recovery paths remain. Full control requires managed devices and institutional policies.
- **Why local?** Frames and event metadata stay on the laptop without cloud inference. Installation and performance on target laptops still need verification.
- **What did your team create?** Integration, calibrated temporal rules, the dashboard, local reports, protection and recovery. We disclose pretrained models, libraries and AI assistance.
- **Has a university adopted it?** No completed pilot or adoption is established. Slide 5 is a proposal.
- **What happens on failure?** Main-process emergency stop, a backend watchdog and cleanup/storage failure handling are implemented. Automated failure tests pass. Physical camera and keyboard tests remain pending.

The supplied documents provide competition requirements. They do not authorize contacting the university, submitting materials or claiming endorsement.
