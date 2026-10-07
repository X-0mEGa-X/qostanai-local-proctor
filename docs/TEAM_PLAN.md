# Three person hackathon plan

Build and submit a working local proctoring prototype for Case 3. The captain's Pro account handles sustained engineering and integration with Codex; the two Plus accounts handle shorter, well-defined tasks with saved outputs. Everyone must understand and explain their part.

## Ownership

| Person | Owns | Deliverable | Do not edit without captain coordination |
| --- | --- | --- | --- |
| You, captain, Pro | Core app, vision, security, integration, GitHub, submission | Running live prototype, tested release, architecture and disclosures | Captain is final integration owner |
| Member 2, Plus, supplied handle Bulataovv8 | Product QA and demo operation | Completed test matrix, defects, short demo video and fallback recording | `backend/`, `desktop/`, dependency files |
| Member 3, Plus, supplied handle Nevel12 | Pitch and pilot case | Six-slide PDF, three-minute script, jury Q&A, source-backed adoption proposal | App code and dependency files |

The supplied handles were not found by GitHub on 7 October. Invitations require corrected profile URLs. Roles can be swapped if skills fit better; no role depends on having Pro. [Official OpenAI plan documentation](https://learn.chatgpt.com/docs/pricing) includes Codex in both Plus and Pro; exact allowances and model access vary. Use the strongest reasoning option actually available for difficult engineering, and an ordinary/default model for bounded drafting. Avoid assuming either subscription is unlimited. This app does not use paid cloud inference.

## First 30 minutes

1. Captain confirms team registration and checks the organizer's submission instructions. Use **8 October 2026, 23:59** as the conservative submission deadline; the rules contain conflicting dates. Confirm the deadline's timezone with the organizer. Internal team scheduling uses Asia/Bishkek.
2. Teammates accept invitations, clone the repo, and read `README.md`, `docs/CASE_AND_RULES.md`, `docs/ARCHITECTURE.md` and their prompt guides.
3. All three run simulation. Only the captain needs to install/run the full live stack immediately if teammates have installation trouble.
4. Create branches `member2/qa-demo` and `member3/pitch`. Work on owned files only; use pull requests into `main`.
5. Agree a team name and a presenter. The captain records actual available hardware and remaining hours. The schedule below assumes about 24 hours, not a confirmed event duration.

## A 24 hour work schedule

| Time from kickoff | Captain and Codex | Member 2 | Member 3 | Integration gate |
| --- | --- | --- | --- | --- |
| 0-2 h | Setup, model loading, camera pipeline | Run baseline checks; prepare scenario matrix | Extract judging criteria; six-slide outline | Everyone can launch or access the demo |
| 2-6 h | Live phone/face/gaze checks, threshold tuning | Record real test observations across lighting and glasses | Pilot workflow, sources, benefits and limits | Core live scenario completes without crash |
| 6-10 h | Validate guard and recovery; repair defects | Repeat priority tests on another laptop | Draft PDF pitch and Q&A | No unresolved release-blocking failures |
| 10-14 h | Integrate reports, pin working dependencies | Record 60-90 second live demo | Add only measured metrics/screenshots | Live evidence exists; simulation labeled |
| 14-18 h | Fresh-clone setup check, review PRs | Rehearse demo and recovery | Rehearse timed pitch with all members | Whole presentation fits 3 minutes |
| 18-22 h | Freeze features; release candidate | Run final checklist and fallback video | Finish PDF and submission description | Submission materials complete |
| 22-24 h | Upload and verify receipt | Verify artifact links/playback | Cross-check claims and organizer checklist | Submit before conservative deadline |

If fewer than 12 hours remain, freeze optional features immediately. Prioritize live phone/face signals, gaze calibration, recovery, report export and the required PDF. Do not spend the final hours training a model, adding a cloud platform, building login/accounts or adding untested features. Do not present a simulation as a completed live prototype.

## Handoffs and account usage

Every 2 hours, each member shares: finished files/PR, one piece of evidence, current blocker, next action. Keep outputs in the repo so a new AI chat can resume from facts. Plus members should use the four focused prompts in their guides, paste only relevant excerpts and error logs, and keep source gathering/drafting bounded. Move complex code defects to the captain's queue with reproduction steps. Never share account logins.

Codex has built the starting code and documents. Human work still includes consented live trials, verifying claims, choosing the team identity, learning the code, recording a real demonstration and submitting through the organizer's form.
