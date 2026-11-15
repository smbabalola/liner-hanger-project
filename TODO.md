# TODO — Liner Hanger Investigation MVP (active release checklist)

**Approved 2026-11-15:** Deliver a **complete, locally runnable retrospective RCA application MVP** as soon as feasible; target **today**. [STEERING.md](STEERING.md) is authoritative. The earlier LH-CALC calculation-first programme is **deferred**, not deleted or retroactively accepted. Its extensive earlier progress log remains in Git history and source-specific `skills/liner-hanger-rca/references/` documents.

**MVP release status:** **NOT VERIFIED COMPLETE**. No app-release acceptance is claimed by editing these files. `[x]` below requires actual implemented/observed evidence; existing reusable code is noted separately but is not proof of app integration.

## Execute these five gates in order

- [ ] **MVP-01 — Inventory existing UI + select a single working app shell.** Audit current HTML/JS prototypes and moving assembly, chart/replay, range-annotation modules; locate the Python skill case/parser/timeline/hypothesis/report components. Choose fastest locally runnable architecture. Identify actual file paths, entry command, existing functionality, missing integration and any blockers. **Pass:** selected runnable shell + short reusable-component map; don't build a second demo.
- [ ] **MVP-02 — One app and one open/import case workflow.** From the chosen UI, create/open a case, import CSV rig data and chronological job events, enter optional approved procedure + component outline, map channel names/units/time/source. Preserve raw data and surface missing/invalid channel warnings; wire existing skill APIs without repo-root-only assumptions. **Pass:** UI can load a fictional case, retain original readings and show import diagnostics.
- [ ] **MVP-03 — Synchronized investigation replay and deviation timeline.** Show standpipe pressure, hookload, torque, RPM, pump flow/volume, returns and depth **when present** on selectable time trends; animate a distinguishable drillstring/running-tool/liner outline using sourced depth. Synchronize events, procedures and user playback selection. Produce a list of **source-supported potential procedure deviations** and missing evidence; never infer tool success from surface pressure alone. **Pass:** normal and anomalous fictional runs replay at expected timestamps; gaps/unavailable channels don't create false deviation findings.
- [ ] **MVP-04 — Annotations, hypotheses and report export.** Allow time-point/range selection → modal entry/edit → saved notes/reload/hover display. Connect alternative explanations with supporting/contradicting observations; export readable Markdown or PDF (one reliable format is enough for MVP), including procedure deviations, source IDs, uncertainties, and engineer-approval status. **Pass:** saved annotation survives reopening and appears at the right interval in the exported investigation draft.
- [ ] **MVP-05 — End-to-end release test and actual local run.** Launch from documented commands; verify synthetic **normal** and **anomalous** cases through UI Import → Replay → Deviations → Notes → Report. Run relevant automated tests and a clean installation/smoke test. Fix all blocking defects; check no private BH/customer data or API keys appear in commits. **Pass:** record paths, test commands, observed pass/fail totals, UI run evidence, final commit, remaining non-blocking issues. Mark release **MVP COMPLETE (LOCAL ENGINEERING DEMO ONLY)** only if every gate passes.

## What already exists — reuse, don't rediscover or recertify

- Evidence-led case tools, Baker Hughes first-release operating-stage framework, basic BHA geometry, chronological events, alternative-hypothesis review and report-generating scripts already exist in `skills/liner-hanger-rca/`. Previous development produced **15 synthetic report scenarios**, with report reviews and software regression; **this does not prove a connected user-facing app**.
- Some telemetry replay/assembly motion and range-annotation UI prototypes were previously developed. **Inspect actual checkout and retest**; current version, import/runtime path, and end-to-end behaviour are not yet re-verified for this MVP.
- Restricted calculation modules (Newtonian, power-law, Bingham/Herschel–Bulkley laminar annulus, nozzle, static hydrostatics and research pressure accounting) and earlier CI tests exist. Use calculations only when applicable and explicitly **source-labelled/research-only**. They are **not a prerequisite** for the application MVP.
- Prior GitHub Actions fully tested up to at least **923 Python cases per interpreter** after the Newtonian turbulent pipe work; additional pressure-accounting work was under way. **The current repository HEAD/full-suite result must be checked before any fresh release claim.** Never confuse backend physics pass counts with app UI acceptance.

## Today's critical path / implementation discipline

1. **Stop all new LH-CALC research and benchmark hunting.** Do not work on transitional/turbulent non-Newtonian models or real-rig SPP.
2. **Start at MVP-01:** inspect existing application assets and identify the shortest working integration path.
3. **Prefer an offline/local prototype**, no cloud/deployment/authentication work, preserving user's existing UI requests (moving assembly, hover/range notes, modal editor).
4. **Ship the minimum coherent workflow**, test end-to-end, record current status. Incomplete or missing real Baker Hughes/rig data must be labelled **unavailable**; synthetic examples are acceptable for demonstrating functionality, not real incident conclusions.
5. **If time runs out**, commit the actual working state, list exact failing release gate(s) and resume from there; do **not** call the MVP done.

## MVP excludes (deferred and non-blocking)

- **LH-CALC-02–08 formal model/field approval**, advanced torque/drag, Bingham/HB transient and turbulent flow, full SPP, surge/swab, verified OEM setting forces and all nine-stage engineering signoff programme.
- Other manufacturers, cloud, WITSML/live monitoring, mobile app, voice, multi-tenant administration, AI auto-verdicts, complex fluid dynamics simulation.
- Live rig recommendations or claims of Baker Hughes qualification; final operational use remains subject to competent human review and source-governed OEM requirements.

**Deferred LH-CALC accepted status:** `LH-CALC-00` and restricted `LH-CALC-01` were earlier counted **2/9 accepted development stages**; `LH-CALC-02` parked 6/7 and `LH-CALC-03` historically open. That count is **not the MVP percentage** and does not gate the local investigation demo.

## Release record — fill only after tests

| Evidence | Result |
| --- | --- |
| MVP release status | NOT VERIFIED COMPLETE |
| Selected app entrypoint / launch command | Pending MVP-01 |
| Synthetic normal case complete through UI | Not verified |
| Synthetic anomalous case complete through UI | Not verified |
| Charts/assembly/procedure sync | Not verified |
| Modal annotation persistence/export | Not verified |
| Report export + reviewer/unavailable labels | Not verified |
| Full automated tests and fresh-install smoke | Pending |
| Last code commit and test logs | To be recorded after implementation |
| Known missing non-blocking enhancements | Advanced engineering work deferred |

**Final acceptance decision:** Only check all five boxes, declare a **local demonstration MVP**, and update this record after directly observed passing end-to-end evidence. Do not invent tests, browser runs, root causes, source values, OEM limits, reviewer sign-offs or release tags.
