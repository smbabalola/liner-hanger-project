# Liner Hanger Investigation Workbench — Local MVP

> **REAL PRODUCT MVP UPDATE — 2026-11-16:** This application is the established browser shell for the real investigation product; it is **not yet the accepted real-case MVP**. [STEERING.md](../../../STEERING.md) and [TODO.md](../../../TODO.md) require independent job-source intake, a richer central replay workstation, complete procedures/annotations and one authorized real case acceptance. The 939×2 synthetic-browser tests are historical baseline, not final product approval. The new Source Register can add separate procedure, daily report, equipment/BHA, fluids and telemetry document **references**, with original filename/size and optional SHA-256; **no PDF content extraction or source binary preservation is claimed**. Source files remain outside downloaded case JSON and must be retained separately. Job events can also be entered manually with their source and timestamp status; actual procedure sources are not automatically approved. Not all existing Python skill engines are connected to this browser shell yet.

**Status:** Local/offline engineering demonstration. **Not** field-certified or manufacturer-approved. Never use outputs to direct live rig activities.

## Launch

In the existing project checkout `C:\dev\liner-hanger-project`, open:

`skills\liner-hanger-rca\app\index.html`

in Chrome or Edge. No installation, cloud account, API key, network service or build tooling is needed. Optionally serve the app from the skill directory:

```powershell
cd C:\dev\liner-hanger-project\skills\liner-hanger-rca\app
py -m http.server 8765
```

Then open `http://localhost:8765`. All processing happens inside your browser and nothing is uploaded to a server.

## Five-minute walkthrough

1. Under **Import case**, choose **Load synthetic normal example**. Switch to **Replay**; move the time cursor and inspect the shared trend and assembly schematic. Then open **Deviations**. The fictional normal case has zero apparent pressure deviations.
2. Return to **Import case**, choose **Load synthetic anomalous example**. In **Deviations**, review the seven fictional pressure readings above the **fictional 180 psi rule**. Clicking the window jumps the replay cursor to the start.
3. Drag horizontally over a chart to open a **time-range annotation modal**. Add the observation, alternatives and a source reference, then save. Click **Notes** to edit or navigate saved annotations. Notes are stored in browser local storage; **Export case JSON** for a durable transferable backup.
4. Under **Report**, export a Markdown investigation draft that retains case information, source assertions, chronology, procedure flags, annotations and review limitations.
5. To investigate your own *authorized* case, supply a CSV with `timestamp` plus whichever numeric channels exist; optionally import `events.json` and `rules.json` as described below.

Both built-in cases are **purely synthetic**. Their purported approvals and rule thresholds are **fictional test declarations**, not authentic Baker Hughes equipment values or operating limits.

## Import a nonstandard rig telemetry CSV

The importer keeps a **raw column-to-channel mapping** for the current case. It first suggests known aliases (`timestamp`, `spp`, `hookload`, `torque`, `rpm`, `flow`, `returns`, `running_depth`) but **does not assume unknown header names**. If it cannot identify a meaningful time-and-signal mapping, it opens **Review rig-export column mapping**. For a recognized CSV, use **Review source columns and units** to confirm/override the automatic selections.

1. Choose your CSV file, select the recorded timestamp column, and map each measured channel using its exact raw header. Unused columns can stay unassigned; a source column must not represent two signals.
2. Select the actual source unit shown in the export, e.g. `psi` or `bar`, `m MD` or `ft MD`. **No conversion is performed.** A selected unit is a user-declared value pending engineering review.
3. Timestamps must be ISO 8601 with `Z` or explicit `±HH:MM` offset. If a vendor export lacks offsets, normalize the timestamps using the documented rig clock source **before** importing; the app refuses an ambiguous clock.
4. Click **Apply mapping and import telemetry**. The canonical data retains the original CSV row number and the mapping (header, raw column index and declared unit). The original CSV bytes are not embedded in case JSON, so preserve the file independently.
5. The saved case and Markdown report include the mapping record. Quantitative procedure thresholds remain unverifiable when the relevant source unit is unknown or conflicts with the rulebook. Real-case assembly motion requires an actual running-depth series **and its confirmed source unit**; hole/bit depth alone is not sufficient.

For source PDFs, drawings, daily reports, fluid documents and tally spreadsheets, the **Job evidence register** stores only filename, size, evidence category, source reference and optional SHA-256, **not the document contents or automatic interpretations**. Enter reported job events with their source/time through the form. This is only the first part of REAL-02; full document interpretation and complete case workflow remain in progress.

## Input files

- Telemetry CSV must contain `timestamp`, `t` or `time` (strictly increasing, unique, valid timestamps). For unambiguous clock handling use ISO 8601 with an explicit UTC `Z` or offset. Optional columns: `depth`, `running_depth`, `spp`, `hookload`, `torque`, `rpm`, `flow`, `volume`, `returns`. Synonyms appear in the UI. Units are **not converted or inferred**: validate the source before comparing a value to a rule.
- Job chronology is a JSON array, e.g. `[{"time":"2026-11-10T09:20:00Z","label":"Circulate","source":"daily-report/page-2"}]`. Missing timestamps remain event-source questions; don't assume report time equals rig sensor time.
- Procedure rules are intentionally compatible with the essential `check_procedure.py` schema: `{"procedure":{"approved":true,"revision":"REV-A","approval_reference":"source-ref"},"telemetry_clock_alignment_verified":true,"channel_units":{"spp":"psi"},"rules":[{"id":"rule-1","step":"Circulate","description":"Example check","approved":true,"source_reference":"approved-procedure/page","channel":"spp","operator":"<=","value":180,"unit":"psi","window":{"start":"2026-11-10T09:10:00Z","end":"2026-11-10T09:45:00Z"}}]}`. These are *caller declarations*, not independently authenticated approvals. Missing evidence yields **unverifiable**, not an automatic compliance/failure verdict.
- Saved case format `liner-mvp-case-1` is an offline JSON transfer file. Raw sample records, source row indices and notes are included. No OEM manuals or private job files are embedded in source code.

## Scope and limitations

This MVP provides a **retrospective first-pass investigation workspace**, not a mechanically validated simulator. Charts show the imported numeric values and omit missing values. **Running-string depth** is required to move the schematic: a hole/bit-depth channel alone does not measure liner/hanger position. The schematic is always an unscaled schematic; it does not establish downhole actuation.

Procedure comparisons show **apparent deviations** only when the input rulebook supplies source/clock/unit/approval declarations. Check original sensor calibration, selected time window, stage, approved equipment model/revision, rig-vs-cement sensor source and report uncertainty before relying on these prompts. The MVP report cannot establish a mechanical root cause. Reviewer status always remains **not completed**, even when a user-supplied rulebook says approved.

The standalone Python skill includes much more sophisticated research-only hydraulics, modelling, reports and evidence engines; those are **not automatically applied or field-approved in this MVP**. The JavaScript application reuses their domain conventions and first-release investigation steps but does **not** yet invoke all the Python investigation APIs or support arbitrary tool-specific mechanisms.

## Tests

The GitHub Action `.github/workflows/skill-regression.yml` runs the skill's complete pytest suite on Python 3.11/3.12 and installs Chromium/Playwright. `tests/test_mvp_offline_app.py` opens this actual HTML app and exercises normal/anomalous cases, CSV ingestion, evidence notes, invalid imports and report download. See `TODO.md` for the **observed** accepted test/run/commit rather than inferred totals.

Release status is conditional on that regression passing and the application being verified in a local browser.
