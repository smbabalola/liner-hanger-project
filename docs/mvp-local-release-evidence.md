# Liner Hanger RCA — local MVP evidence and release boundary

**Date:** 2026-11-15  
**Delivery classification:** **Browser-verified local engineering demonstration MVP.** Not a field-approved tool, a Baker Hughes-certified calculation, or a deployed commercial application.  
**Code source:** `skills/liner-hanger-rca/app/index.html` and `app.js`; launch instructions `skills/liner-hanger-rca/app/README.md`.  
**Source code checkpoint:** `519de543dd3ae6ee2d0232875ea31516e7a172e5` (last implementation/test commit before the verified build).

## Actual acceptance evidence

Hosted GitHub Actions regression: [run 43764373475](https://github.com/smbabalola/liner-hanger-project/actions/runs/43764373475), at commit `519de543`, verified from both independent job logs:

- **Python 3.11: 939 passed in 19.07 seconds**, no failures or skips.
- **Python 3.12: 939 passed in 33.62 seconds**, no failures or skips.

The full regression includes `tests/test_mvp_offline_app.py`, which actually launches the app through Playwright Chromium using local `file://` URLs and tests:

1. Normal synthetic case opens; 61 samples, charts, depth-driven *schematic* movement and synchronized replay; no manufactured deviation; draft report includes unapproved/undetermined conclusion.
2. Anomalous synthetic case produces an apparent procedure-pressure deviation window; clicking it jumps to the correct sample; modal annotation is stored, restored after page reload, present in report and Markdown download completes.
3. Imported CSV charts work with missing channels; missing running-string depth keeps the assembly stationary; absent rulebook yields **not verifiable**.
4. Duplicate CSV timestamps and unsupported case file schema are rejected.
5. Dragging horizontally across a trend creates a selected index/time interval and opens the annotation modal.
6. Optional required-event sequence flags a source-declared **out-of-order reported step** as a review question, while a missing step becomes an **evidence gap**, not proof of omission.
7. **Standalone portability:** copy only the `app` folder to a new directory, open its HTML directly, export a complete case JSON and re-import it; expected anomaly remains visible and no browser runtime errors occur.

These are real automated UI-browser checks, not merely Python algorithm tests. An independent hands-on run in the user's Windows/Edge installation has **not** been observed in this conversation; a first-use smoke check there is recommended, and any platform-specific defect should be corrected before wider rollout.

## Intentional MVP architecture decision

Previous Utah FORGE replay was an event-specific HTML generator with hard-coded case details, and v1.5 chart annotation assets depended on a fixed `caseData` layout. Those existing versions were inspected, preserved, and used as design/behaviour references. For the fastest usable local deliverable, the MVP uses a small **new, self-contained offline browser shell** with matching engineering conventions and transferable case JSON. The browser's procedure comparator implements a restricted subset of the existing `check_procedure.py` contract. **This is not a live invocation of the Python skill APIs, a migration of the entire existing v1.5 annotation code, or a claim of full backend-feature parity.** Such integration is post-MVP work if needed.

## Capabilities and known limitations

**Delivered:** import telemetry CSV and optional job-event/procedure JSON; replay synchronized surface signals; a schematic with separate drillstring/running tool/liner and depth-based motion only when sourced running depth exists; observed signal deviations and event-order questions; annotations on selected replay ranges with browser persistence and JSON export; draft Markdown investigation report.

**Not delivered/not claimed:** measured BHA tool actuation, validated Baker Hughes setting pressures/force limits, dynamically complete hydraulics, automated mechanical root cause, certified engineering review, real KHRM job-data integration, rig-versus-cement pump normalization for every case, field deployment, authenticated operator data, cloud/mobile, or 1:1 integration with all Python RCA skill outputs.

All sample dates, numeric limits, tool depictions and procedure approvals are **synthetic**, and deliberately not manufacturer operating guidance. Source document permissions and user-specific rig data must be reviewed before importing confidential materials into any shared system. No proprietary documents were committed as a result of this MVP work.

## Decision

**Local browser MVP development and automated UI acceptance: COMPLETE at its expressly reduced scope.**  
**Windows user smoke/acceptance: NOT YET OBSERVED.**  
**Engineering/OEM/field approval: NOT PROVIDED.**  
**Broader nine-stage LH-CALC research: DEFERRED, not accepted.**

For any broader engineering release, reopen the appropriate engineering and independent-validation gates rather than reclassifying the browser demonstration as physically validated.
