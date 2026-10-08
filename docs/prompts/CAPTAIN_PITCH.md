# Captain presentation and jury prompts

The captain and Codex own the six-slide PDF, three-minute pitch, pilot proposal and jury answers. Continue in the existing captain chat. Member 2 supplies actual test results and demo evidence. Own `docs/PITCH.md`, `docs/PILOT_PLAN.md`, `docs/JURY_QA.md` and `submission/presentation.pdf`. Member 3 has no laptop-dependent deliverables.

## Step 1 build the judging outline

```text
We are the captain and Codex preparing the presentation for our three-person team. Case 3 is local proctoring for KRU/Qostanai Hub. Read the attached case/rules, architecture and current pitch draft. Create a six-slide outline that fits a three-minute presentation and addresses scoring: case fit 15, implementation 20, deployment/effect 20, innovation 15, demo 15, pitch/Q&A 15. Our app uses pretrained YOLOv8n phones, MediaPipe face meshes and calibrated coarse gaze/head signals, sustained-event rules, Electron restrictions and an optional Windows key hook. Phone raised is not proof of photography; full outside-window blocking is not complete. Disclose Codex/ChatGPT and external components. Do not invent accuracy, savings, clients or pilot results. Give one purpose and at most three short points per slide.
```

## Step 2 propose a grounded pilot

```text
Create docs/PILOT_PLAN.md for a proposed small supervised KRU trial of our local proctoring prototype. Use the supplied case and actual architecture. Define the teacher/student workflow, hardware and offline setup, participant consent, accessibility review, human decision process, event retention/deletion, managed-device requirements, metrics and go/no-go gates. Benefits are hypotheses unless measured. If making external factual claims, search primary sources, link them and separate facts from assumptions. Do not provide unsupported legal compliance claims or invent cost/savings percentages. Keep this to 600 words.
```

## Step 3 make the PDF and timed script

Use the actual validation summary and Member 2's consented screenshots or video. Codex prepares the editable deck and PDF, and the captain checks the team identity, evidence and final claims. Inspect every slide before submission.

```text
Create final slide text and speaker notes for our six-slide Case 3 presentation. Team name/members: [ACTUAL DETAILS]. Actual validation: [PASTE RESULTS]. Demonstration: [PASTE RUNBOOK AND LIVE/RECORDED/SIMULATED LABELS]. Use the approved outline, readable text and actual product screenshots where appropriate. Clearly label unvalidated features and deployment gaps. Put AI/pretrained component disclosure and limitations on the last slide. Write a timed script totaling at most three minutes: captain introduces/technical explanation, Member 2 runs about 65 seconds of demonstration, the captain explains pilot value and limits. Return final slide text and notes; if you can generate a deck, export a presentation PDF to submission/presentation.pdf. Do not invent missing evidence.
```

## Step 4 rehearse and audit claims

```text
Review this final pitch/PDF text against the case, architecture and measured QA: [PASTE TEXT]. Flag unsupported claims, missing scoring points, confusing jargon and any implication that simulation is live evidence. Create docs/JURY_QA.md with 12 likely questions and concise defensible answers covering false positives, photography detection, gaze accuracy, face model, Windows bypasses/recovery, offline performance, privacy, component licensing, AI use, novelty and pilot adoption. Give a rehearsal checklist and cuts if the presentation exceeds three minutes.
```

## Integration

The captain keeps the presentation files with the source repository and checks them against the final tested commit. No handoff from Member 3 is required. Keep missing team details or test evidence explicit until they are supplied.
