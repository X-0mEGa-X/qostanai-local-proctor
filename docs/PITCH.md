# Six-slide pitch and three-minute script

The captain narrates; Member 2 operates the demonstration. Codex prepared the deck, script, pilot proposal and jury answers. The latest roster is The Mentalist: captain Artur Bulatov, Aibek Zainiddin and Adilet Derdybekov, Astana IT University, Astana. Slide 1 now includes these user-supplied details.

Deliverables: [presentation PDF](../submission/presentation.pdf), [editable PPTX with notes](../submission/presentation.pptx), [jury answers](JURY_QA.md), [pilot proposal](PILOT_PLAN.md), and [claim audit](RELEASE_REVIEW.md). The deck has exactly six slides. The timing below allocates 180 seconds including a 65-second demonstration; a human timed rehearsal remains necessary.

## 1. Team and problem: 0:00–0:20

Slide: **Qostanai Local Proctor. Local exam signals for human review.** Captain owns engineering and pitch; Member 2 owns QA/demo. Reviewers need context for phones, absence and sustained off-screen attention.

Say: “We are The Mentalist from Astana IT University: Artur Bulatov, captain, with Aibek Zainiddin and Adilet Derdybekov. We chose Case 3 from KRU and Qostanai Hub. Our prototype combines local webcam signals and exam-window events into one timeline for human review.”

## 2. Case requirements and coverage: 0:20–0:45

Slide: phone visibility/raised phone with YOLO and a position rule; face presence and attention with MediaPipe and calibration; Electron controls with an optional Windows key hook; local JSON reports. Photography proof and outside-app lockdown remain incomplete.

Say: “YOLO detects phones. MediaPipe supplies face counts and head and iris features. Signals must persist before entering the timeline. Electron restricts navigation and clipboard use, with an optional Windows keyboard hook. Phone photography and control of all outside applications remain partial requirements.”

## 3. Local architecture: 0:45–1:10

Slide: memory-only camera frames, Python models, temporal rules and local JSON review. Electron connects through `127.0.0.1`. End session and Ctrl+Shift+Q provide release paths.

Say: “Python processes camera frames on the laptop. Pretrained YOLO and MediaPipe feed sustained-signal rules. Electron displays the exam and review timeline through a local API. Frames stay in memory. JSON stores event metadata and guided-test observations. Our contribution is this integration, calibration and recoverable workflow.”

## 4. Actual prototype and evidence: 1:10–2:15

Slide: actual Electron screenshot captured in **SIMULATION on 8 October 2026**. **26 Python tests and 2 Node policy tests passed. API and Electron checks passed. Zero human webcam trials are documented.** No accuracy or live-latency measurement is claimed.

Use the verified simulation path for the current pitch. Start simulation before this slide, with Windows hook unchecked. Keep its label visible. No footage or participant camera is needed.

| Within the 65 seconds | Action |
| --- | --- |
| 0–10 s | Identify SIMULATION, camera off and scripted phone-visible/raised events |
| 10–25 s | Show the timeline, timestamps and event sources |
| 25–40 s | End/release protection and export the report |
| 40–50 s | Show the ended JSON session ID, ended time and event sources |
| 50–65 s | State checks and the absence of human detection measurements |

Say: “This is the actual prototype in simulation. Its vision signals are scripted, and the camera is off. Each event has a time and source. We release the session and export its report. Twenty-six Python tests, two desktop policy tests, API integration and Electron recovery/export checks pass. Camera fault checks use fake hardware. We have zero recorded human webcam trials, so accuracy and live latency remain unmeasured.”

If the actual run fails, state the failure and show the dated screenshot or an existing exported simulation report. A screenshot alone does not establish working live detection. Switch to a live demo only after a consented human rehearsal and a revised evidence record. Do not record or upload the camera without explicit instruction.

## 5. Proposed pilot: 2:15–2:40

Slide: proposed 5 volunteers, 2 university Windows laptops and 20-minute practice sessions, supervised by a teacher. Measure misses, false alerts, timing, release and reviewer effort. Consent, accommodations and an agreed retention policy are conditions.

Say: “We propose five volunteers on two university Windows laptops, with a teacher supervising twenty-minute practice sessions. We would measure scenario misses, false alerts, latency and successful release, then compare reviewer effort. Reduced footage transfer and faster triage are hypotheses. This pilot needs university agreement, accommodations and a retention policy.”

## 6. Limits and next steps: 2:40–3:00

Slide: coarse gaze, raised-phone heuristic, unfinished OS lockdown and pending human tests. Disclose YOLOv8n/COCO, MediaPipe, OpenCV/PyTorch, FastAPI, Electron and Codex/ChatGPT assistance. Next: human validation, supervised pilot and managed exam policies.

Say: “Gaze remains approximate, and a raised phone cannot establish photography. Complete OS lockdown is unfinished. We disclose pretrained YOLO, MediaPipe, the software libraries and Codex/ChatGPT assistance. Our next step is human validation, followed by a supervised pilot and managed exam policies.”

## Judging map

| Criterion | Points | Coverage |
| --- | ---: | --- |
| Case fit | 15 | Slides 1–2 map each group and expose partial coverage |
| Technical implementation | 20 | Slides 3–4 show modules, local flow and actual software checks |
| Deployment potential and effect | 20 | Slide 5 proposes a supervised pilot and measurable hypotheses |
| Innovation | 15 | Slides 2–3 explain integrated calibration, temporal rules and recoverable local review; slide 6 credits existing models |
| Working prototype and demo | 15 | Slide 4 shows actual application behavior and export; simulation is explicit |
| Pitch and answers | 15 | Six slides, 180-second allocation, captain narration, Member 2 operation, `JURY_QA.md` |

These are coverage targets, not awarded points. Requirements/weights come from the supplied case/rules, summarized in `CASE_AND_RULES.md`. Evidence comes from code and `RELEASE_REVIEW.md`. No accuracy, savings, completed pilot or institutional endorsement is claimed.

## Rehearsal cuts

Open the report destination and presentation before speaking. Explain component names once. If behind time, shorten the timeline explanation on slide 4 by ten seconds; keep the mode label, release/export, unmeasured accuracy and final limitations. Do not rush or skip emergency recovery. Verify registered team identity and presentation playback before submission.
