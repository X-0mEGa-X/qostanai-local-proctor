# Member 2 product testing and demo prompts

You own QA and demonstration evidence. Use a Plus chat/Codex session and short requests. First accept the GitHub invite, clone, read the README and create `member2/qa-demo`. Your writable scope is `docs/QA_CHECKLIST.md`, `docs/VALIDATION.md`, `docs/DEMO_RUNBOOK.md` and anonymized test summaries. Send core-code defects to the captain with reproduction steps.

If your chat cannot read the repository, attach the case/rules and paste the relevant README, architecture and checklist text. A private GitHub URL by itself may not give ChatGPT access. Ask for file contents or a patch, save them locally and make a PR. Save chat outputs between steps to reduce repeated context.

## Step 1 make an executable test plan

```text
I am Member 2 of a three-person hackathon team using ChatGPT Plus. We chose Case 3, local proctoring for KRU/Qostanai Hub. The captain/Codex owns the Python vision and Electron/security code. I own QA and demo. Read the attached case/rules, README, architecture and QA checklist. Turn the checklist into a 90-minute prioritized manual test plan with exact steps, expected signals and an empty actual-result column. Cover neutral baseline, phone, raised phone, down/side gaze, absence, second face, camera failure, copy/paste, Windows keys, recovery and report export. Distinguish simulation from live evidence. Do not invent results or change backend/desktop code. Return only the plan and a compact CSV header.
```

## Step 2 analyze observations

Run the tests yourself with consent. Copy the resulting observations into this prompt.

```text
Here are my actual Case 3 observations: [PASTE LOG WITH DEVICE, MODE, LIGHTING, SCENARIO, DURATION, EXPECTED, OBSERVED, LATENCY, MISSES AND FALSE FLAGS]. Convert these into docs/VALIDATION.md. Separate automated software checks, scripted simulation, model execution checks and real webcam validation. Compute only metrics justified by the trial data and show denominators. Rank defects by whether they block submission; give concise reproduction steps for the captain. Treat gaze as a coarse calibrated proxy and phone raised as a heuristic. Do not claim production accuracy or successful OS lockdown from an untested feature.
```

## Step 3 record the demo

```text
Based on the attached actual QA outcomes, create docs/DEMO_RUNBOOK.md for a 60-90 second recorded live demonstration and a 65-second stage demo inside a three-minute pitch. Include camera framing, consent, calibration before filming, phone visible/raised, sustained down gaze, second face if reliable, one tested protection action, emergency release, report export and a fallback if the camera fails. Label recorded live footage and any scripted simulation clearly. Use no fabricated results. Give a second-by-second shot list and a rehearsal checklist. Keep participant faces/recordings private unless they consent to the intended sharing.
```

## Step 4 hand off evidence

```text
Prepare my QA/demo handoff to the captain from these files and observations: [PASTE SUMMARY]. List completed tests, unresolved release blockers, actual device/latency/trial results, the demonstration video location/access, and exactly what remains unverified. Review only my owned docs for contradictions with the implementation. Suggest a concise commit message and PR description. Do not edit application code or call simulation a live detector demo.
```

## Git handoff

```powershell
git switch -c member2/qa-demo
# Save only your owned documents, then inspect the diff.
git add docs/QA_CHECKLIST.md docs/VALIDATION.md docs/DEMO_RUNBOOK.md
git diff --cached
git commit -m "Document real QA findings and demo runbook"
git push -u origin member2/qa-demo
```

Open a pull request on GitHub into `main`. Do not add private reports, raw faces or videos to Git by default. If installation is blocked, use the captain's laptop for live trials and continue your planning/analysis in Plus.
