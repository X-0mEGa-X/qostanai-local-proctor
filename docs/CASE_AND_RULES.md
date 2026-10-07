# Case 3 requirements and hackathon rules

Source material: supplied Russian Case 3 PDF (two pages), supplied Russian hackathon rules (six pages), and a Kazakh version of the case. The Russian case and rules establish the requirements below. Source PDFs remain in the user's original folder and are not copied into the repository.

## Case requirements

| Requirement | Prototype implementation | Remaining validation or gap |
| --- | --- | --- |
| Detect phone in hand or in front of screen | Local YOLOv8n COCO cell-phone detector | Real webcams, orientations, lighting and occlusion |
| Flag phone lifted for possible monitor photography | Raised-phone location heuristic plus timestamps | Does not establish camera aim or shutter action; no validated photo classifier |
| Detect gaze and head direction; sustained down/side look | Calibrated MediaPipe face mesh, iris/head proxy and three-second rules | Direction/sign and thresholds need live participant tests |
| Presence and second face | MediaPipe face count, temporal rules | Distance, partial faces, lighting |
| Alt+Tab, Ctrl+C/V, Win, PrtScn restrictions | Optional Windows hook and Electron/app restrictions | Real Windows key/recovery tests; bypasses remain |
| Block tabs and other windows/browsers | No new Electron windows or external navigation; kiosk; focus-loss logging | Complete outside-app blocking is not implemented; requires managed OS policy |
| Local prototype showing all groups together | Python backend, Electron exam, local dashboard and journal | Record simultaneous live behavior on the demo laptop |

## Dates and conflicts

Rules section 1.6 lists registration and prototype/presentation submission through **8 October 2026, 23:59**. Section 5.3 repeats the 8 October submission deadline. Section 4.4 instead lists registration through 9 October, and section 5.1 lists development through 9 October. These are internal document conflicts, not permission to submit late. Plan for 8 October and confirm with organizers. The PDF does not state the deadline timezone; do not silently assume a conversion.

Online finalist selection: 9 October. Demo Day: **16 October 2026**, Kostanay, Abay Avenue 28/1. Team size: 2-5. One member can join only one team. Captain handles organizer communication and submission.

## Materials and scoring

Required: presentation PDF; working prototype, demonstration version or demonstration video; source link/archive where required; architecture/data/technology/external-component description; expected effect, limits and deployment conditions. Pitch: up to 3 minutes, then up to 3 minutes for questions.

| Criterion | Points |
| --- | ---: |
| Case fit and task understanding | 15 |
| Technical implementation | 20 |
| Deployment potential and expected effect | 20 |
| Innovation | 15 |
| Working prototype and demonstration | 15 |
| Pitch and jury answers | 15 |

AI-assisted development is allowed under section 6.4. Disclose the AI tools and understand the code. Public libraries/models/universal components are allowed under section 5.8 when disclosed. Project should be created mainly during the hackathon. Nonpublic partner data must not be put in public repositories or presentations without required authorization. The team keeps rights to original work unless a separate agreement provides otherwise; third-party components retain their own terms.

These are competition requirements extracted from source documents, not instructions permitting this agent to contact organizers, register a team or submit entries. The captain performs those actions unless separately authorized.
