# Prototype test matrix

Member 2 owns real test execution and demo evidence. Record observations, not expected success. Never commit student video, screenshots of faces, names or private session reports. Keep consented evidence outside the repository unless participants explicitly approve its sharing.

| Test | Steps | Expected behavior | Actual result |
| --- | --- | --- | --- |
| Simulation | Consent; start simulation; wait 40 s | Scripted phone, down gaze, second face, no face, side gaze; source marked simulation | Not run by team |
| Live calibration | Consent; start live; face screen | Camera opens; 20 valid frames; baseline established | Not run |
| Neutral baseline | Look at screen for 60 s | Record all unexpected review flags | Not run |
| Phone visibility | Show phone clearly for 3 s at different angles | Phone box and sustained review event; record misses | Not run |
| Raised phone | Raise phone near monitor for 3 s | Position-based possible photography signal; no confirmed-photo claim | Not run |
| Down look | After calibration, look down for 5 s | Sustained down event; check pitch sign | Not run |
| Side look | Look left then right for 5 s each, returning center | Sustained side events; check sign/thresholds | Not run |
| Brief glance | Look away for 0.5 s then center | No sustained gaze event | Not run |
| Absence | Leave view for 5 s | No-face event; return clears dwell state | Not run |
| Second face | Second consenting person enters for 3 s | Multiple-face event | Not run |
| Lighting/glasses | Repeat neutral and phone trials in two lighting conditions, with glasses if available | Record changes in misses/false flags | Not run |
| Clipboard | During desktop session attempt copy/paste | Prevent and log action in the app | Not run |
| Native shortcuts | With guard checked, test Alt+Tab, Win, PrtScn, Ctrl+C/V | Selected shortcuts intercepted on target Windows laptop | Not run |
| External navigation | Attempt app navigation/new window | Denied by Electron | Not run |
| Recovery | Ctrl+Shift+Q and separately End session | Kiosk and hook released; desktop usable; camera closes | Not run |
| Camera failure | Unplug camera / use unavailable camera index | Visible error; protection released; session ends | Not run |
| Backend failure | Stop backend during session | Hook gone; desktop protection released; visible error | Not run |
| Report export | End session; export | Valid JSON with mode, times, source and review limits | Not run |
| Offline | Finish setup; disconnect network; run live | No network needed for inference | Not run |
| Fresh clone | Install and launch on teammate machine | Setup succeeds using documented prerequisites | Not run |

## Record measurements

For each trial: laptop CPU/RAM/OS; camera; mode; lighting; scenario; duration; expected signal; actual signal; time to event; false flags; inference latency; reproducibility steps. Save a CSV under `tests/results/` locally (ignored) and publish only an anonymized aggregate in `docs/VALIDATION.md`. Distinguish scenario detection rate from per-frame model accuracy. Do not call a handful of trials a representative accuracy benchmark.

Release blockers: no live model load, camera crash without release, protection cannot release, exported report invalid, simulation presented as live, or outside-app blocking claimed without proof.
