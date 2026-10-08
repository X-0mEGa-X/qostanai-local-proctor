# Proposal for a supervised KRU pilot

We propose a practice pilot of Qostanai Local Proctor with five consenting volunteers, two university Windows laptops and a teacher present. Each volunteer completes a 20-minute session. This is a proposed feasibility study, with no exam penalties or claim of university approval. No completed pilot, detection accuracy or workload saving is established.

## Student and teacher workflow

The teacher checks camera access, model readiness, report storage and emergency release, then explains the review signals and agrees any accommodations. Students consent, calibrate while facing the screen and complete practice tasks. The current app contains a sample question; integration with a real university exam platform remains future work.

A supervisor gives timed cues for phone visibility, raised phone, gaze, absence and a second consenting face, recording whether each action actually occurred. The student ends the session and verifies release. The teacher reviews the exported event report against the supervisor's notes, labels each alert as supported, false, accommodation-related or uncertain, and records review time. Alerts never automatically determine misconduct.

## Hardware and setup

Use powered Windows 11 laptops with working webcams and consistent lighting. The development laptop has an i5-1135G7 and approximately 8 GB RAM; this is a reference configuration, not a validated minimum. The prototype runs its detectors on CPU.

IT installs Git, Python 3.12, Node.js, locked dependencies and the two model assets while connected to the internet. Test launch, writable storage and recovery on both laptops before volunteers attend, then conduct a disconnected-network trial. Institutional protection requires a compatible managed Windows edition and policies; the development laptop currently runs Home.

## Data and review

Camera processing runs locally. The app holds preview frames in memory and stores event metadata in local `data/` JSON files. Guided trials additionally store categorical observations, pose/iris deltas and processing times. No camera footage is saved or uploaded by this workflow. Reports are excluded from Git but are ordinary local files, without institutional access control or signed evidence protection.

Use random session identifiers. Keep any participant mapping separately under teacher control. Agree access, retention and deletion before consent; a suggested pilot policy is deletion of individual records seven days after review and retention only of an anonymized aggregate. Without footage, uncertain events may remain unresolved and should not become adverse findings.

## Accessibility and false alerts

Offer an alternative supervised activity when gaze or head movement is unsuitable for assessment. Agree accommodations for assistive technology, involuntary movement, vision differences, glasses and required breaks. Include comfortable screen positions and varied lighting in testing. Record calibration failures and participant discomfort. Manual review must distinguish permitted behavior from detector error; per-student automated policy exemptions are not yet implemented.

## Managed Windows controls still required

IT should provide a standard exam account, protect the application installation from student changes, allow only approved applications and required runtimes, and define policies for browsers, remote access, capture tools, removable media and network access. Keep an administrator recovery route and test failure recovery before enforcing restrictions.

Assigned Access offers a restricted experience with an allowed application list; its supported editions include Pro, Enterprise and Education. Home is not listed. [Microsoft Assigned Access](https://learn.microsoft.com/en-us/windows/configuration/assigned-access/)

For a desktop app, Shell Launcher can replace the shell on supported Enterprise/Education editions, but it does not itself block other applications. Application-control policies require separate design and testing. These options are not configured in our prototype. [Microsoft Shell Launcher](https://learn.microsoft.com/en-us/windows/configuration/shell-launcher/), [Microsoft App Control and AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/appcontrol-and-applocker-overview)

## Measures and decision

| Measure | Pilot method |
| --- | --- |
| Detection failures | Confirmed scenario trials with missing required events divided by assessable trials, separately for each scenario; report counts and invalid trials |
| False alerts | Adjudicated unsupported alerts per participant-hour of ordinary activity, plus alert type and conditions |
| Gaze direction | Compare participant-left/right/down instructions with label distributions; report unavailable samples and reversed directions separately |
| Latency | Per-frame processing median/p95; cue-to-alert delay separately, including reaction and dwell time. Observer-marked physical onset is needed for action-to-alert latency |
| Reviewer workload | Time and decision agreement for matched written case packets with and without the event timeline; counterbalance order. Measure live supervision time separately; no footage is needed |
| Recovery | Successful releases / attempts, release time, camera closure and valid ended reports |

Reduced footage transfer and faster reviewer triage are hypotheses. The pilot should establish whether they occur. Pause for any failed release, unintended recording or invalid report. Set acceptable miss/false-alert thresholds with KRU before testing; a small convenience sample cannot establish general accuracy or justify a consequential rollout.
