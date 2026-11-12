# Evidence-linked retrospective timeline v0.1

**Date:** 2026-11-12  
**Task:** LH-007 (partial implementation; local regression and engineering review pending)  
**Source files:** `skills/liner-hanger-rca/scripts/evidence_timeline.py`, `skills/liner-hanger-rca/tests/test_evidence_timeline.py`.

## Scope

The original `scripts/build_timeline.py` remains untouched: it normalizes offset-aware CSV timestamps and joins **exact timestamp** events. This new module accepts source-linked `EvidenceEvent` records and **actual outputs** of the existing `operating_limit_screen.screen()` function. It does not modify original telemetry, infer missing event times or create a GUI.

For every screening record, `events_from_screen(case_id, limit, observation, result)` recomputes the supplied result and rejects inconsistent/tampered status. It records source document ID, telemetry source/channel, tool-rule identifier, engineer-review state and reasons. Categories:
- `outside_screening_bounds` → `screening_candidate` (review required, **not** confirmed deviation/failure).
- `within_screening_bounds` → `screening_context` (not proof of successful setting or release).
- `unverifiable` → `evidence_gap` (not a deviation).

`build_timeline()` orders **only** offset-aware events with verified time basis, keeps approximate/unknown event times in `unplaced_events`, refuses duplicates and cross-case mixing, and exposes `earliest_screening_candidate_id` only for the supplied timestamp-verified comparison candidates. **It does not assert the earliest operational deviation**, because unreported/uncaptured events may precede it.

## Important evidence boundaries

- A review flag and time-alignment boolean in the incoming source are caller-entered declarations; the module cannot independently confirm rig clock calibration, official source approval, source authenticity or cross-document time matching.
- Events merely reported in a day-level drilling report are not given fabricated timestamps. Uncertain events cannot determine precedence over a sensor event.
- Raw rig CSV samples, aggregations and sensor histories remain separate from derived screening and investigation data.
- Rig Pump 2 is never equated to the cement-unit pump. Standpipe pressure is not converted into tool-internal setting pressure.
- No actual Baker Hughes technical limits, model-specific setting values or tool conditions are included. Tests use fictional values and IDs only.
- A screening candidate is not automatically an engineer-authored annotation; review/acceptance/audit workflows are later work. No causal or procedural claim is generated.

## Run the local test suite

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

Prior user-verified baseline: **63 passed**. The new timeline test module has additional positive/negative test cases; **actual pytest output remains the acceptance evidence**, not an assumed pass.

## Next steps

Implement formal event source provenance/uncertainty, engineer annotation links, planned-vs-observed chronology, first *supported* deviation criteria and alternative hypotheses only after approved job-specific sequence evidence is available. Maintain the existing no-automatic-root-cause policy.
