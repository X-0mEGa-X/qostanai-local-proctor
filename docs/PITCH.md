# Three minute pitch and PDF outline

The captain and Codex own the final six-slide PDF, script, pilot proposal and jury answers. The captain presents the spoken sections and Member 2 runs the demonstration. Member 3 can join rehearsal without owning a required deliverable. Replace team identity and add actual test findings before submission. Keep unsupported numbers out. Present live behavior and limits accurately.

## Six slides

1. **Qostanai Local Proctor**: team name/members; local proctoring for KRU and Qostanai Hub, Case 3.
2. **Exam supervision problem**: phones and off-screen materials are difficult to review remotely; case asks for local vision and environment controls. Cite the supplied case, not invented market statistics.
3. **Local architecture**: webcam -> YOLO phone detector / MediaPipe face mesh -> sustained signal rules -> exam dashboard and local review report. AI helps build the app; it does not judge the student through cloud calls.
4. **Live demonstration**: show actual measured phone, face and gaze events, plus blocked shortcut and successful recovery. Label any simulation screenshot/recording explicitly. Insert observed device/latency/trial count only after QA.
5. **Pilot at KRU**: proposal for a small consented supervised lab pilot. Measure false flags, scenario misses, inference latency, review time and recovery success. Benefits such as less footage transfer and easier triage are hypotheses to test. Staff review all flags.
6. **Limits and next steps**: phone position is not proof of photography; gaze varies with people/lighting; full lockdown needs managed OS policies; disclose pretrained models, libraries and Codex/ChatGPT. Request a mentor-supported validation pilot.

## Timed script

**0:00-0:20, captain:** “We chose Case 3: a local proctoring system for KRU and Qostanai Hub. The task combines phone detection, face and gaze monitoring, and control of the exam environment.”

**0:20-0:45, captain:** “Our prototype keeps camera processing on the laptop. YOLOv8n finds phones; MediaPipe provides face meshes and calibrated head and iris features. A short glance is not automatically a violation. Sustained signals create entries for a human reviewer.”

**0:45-1:50, Member 2:** Run the prepared live sequence: start/consent and calibration; phone for 3 s; down look for 5 s; a second consenting person enters; attempt clipboard or Alt+Tab with the tested guard; end session and export a report. Use a pre-calibrated consented live session if initial startup exceeds the slot. If switching to the fallback video, identify it as recorded live. Any scripted fallback is explicitly simulation.

**1:50-2:20, captain:** “Each event records its type, time and mode. Camera frames are not saved by default. The exam window restricts navigation and clipboard actions. The optional Windows hook intercepts selected shortcuts, with an emergency release. We do not claim complete OS lockdown or verified photo-taking.”

**2:20-3:00, captain:** “Our next step is a supervised pilot to measure false flags, missed scenarios and reviewer workload on ordinary laptops. Before deployment, the institution must establish its exam policies, accessibility accommodations and managed-device controls. We used pretrained public components and Codex/ChatGPT during development; the team can explain the resulting code.”

## Jury answers

- **Is looking away cheating?** No. These are review signals with duration thresholds; context, accommodations and human judgment are required.
- **Can you prove a photo was taken?** No. We detect phones and raised position. Camera orientation/shutter action is an unresolved case requirement.
- **Does YOLO detect faces?** Our COCO YOLO detects phones. MediaPipe supplies face count/mesh; no pretrained COCO face class is claimed.
- **Can Alt+Tab or screenshots bypass it?** The tested native hook intercepts selected keys. Elevated apps, other capture methods and OS recovery paths remain; complete lockdown needs managed OS policies.
- **What accuracy do you have?** Give the actual labeled scenario count and outcomes. If unmeasured, say validation is pending; do not substitute a model's public COCO score for this webcam use case.
- **Why local?** Local inference avoids uploading video and permits operation after setup without internet; hardware performance and installation remain conditions.
- **What is new?** The team's contribution is a local integration of calibrated dwell rules, transparent review events and reversible exam-window protection. YOLO/MediaPipe themselves are existing components.
- **Can this be deployed tomorrow?** Only as a supervised prototype trial. Production needs validation, managed devices, institutional policy, licensing review and trustworthy report handling.
