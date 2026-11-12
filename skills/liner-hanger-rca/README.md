# Liner Hanger Investigation Skill v1.5 — Retrospective Investigations

One portable skill with public technical background and a controlled path for incorporating authorized training PDFs and reviewed job outcomes. The original investigation workflow is retained. The package includes self-contained example replay HTML inside `examples/` but does not create a separate application or repository. It does not claim to have ingested training materials that have not been supplied.

## Contents
- `SKILL.md`: primary skill instructions and guardrails
- `references/KNOWLEDGE_BASE.md`: equipment, operations, telemetry reasoning, failure-signature prompts
- `references/SOURCE_REGISTER.md`: manufacturer/source URLs with provenance and limitations
- `references/INGESTION_AND_RULES.md`: PDF, procedure and historical-case learning protocol
- `references/INVESTIGATION_METHOD.md`, `DATA_INTAKE.md`, `HYPOTHESIS_LIBRARY.md`, `REPORT_TEMPLATE.md`: working references for investigation
- `schemas/*.json`: templates for tool/job data and confirmed incident learning
- `examples/synthetic_preset_review.md`: illustrative first-deviation review

## Security
Public pages are cited, not wholesale copied. Protected material requires permission and should be isolated per customer and tool/revision. No uncontrolled automation, live rig control or machine-generated operating setpoints. Engineering results require competent review.

## Version 1.3 — replay + procedure investigation

### Open the offline investigation dashboard

`examples/utah_forge_16A_78_32/replay.html` is a **self-contained HTML file**. Open it in Chrome or Edge. It contains seven measured rig trends (from the supplied 10-second CSV, aggregated to 5-minute medians) and a **single playback cursor that moves the entire assembly** through the run from surface. The tool geometry/depth are illustrative milestones from daily reports, **not measured running-string positions**. It also has an investigation event list, an approved JSON rulebook importer and an investigation report export.

### Procedure checking

There is no approved running/setting procedure in the Utah FORGE test pack. Therefore no breach can be confirmed from this case alone. The rules pipeline is complete but produces `unverifiable` until an engineer supplies a procedure, units, and validated time alignment.

1. If given a PDF, extract candidate page-referenced lines (not approved rules): `python scripts/extract_procedure_candidates.py job_procedure.pdf --output candidates.json`.
2. After engineering validation, fill in `schemas/procedure_rulebook_template.json` with approved source/revision, verified windows, signal units and individual rules.
3. Run: `python scripts/check_procedure.py --rules approved_job_rules.json --telemetry examples/utah_forge_16A_78_32/rig_5min.csv --output investigation_results.json`.
4. Or import that rulebook JSON into the replay to view and click the **apparent** deviation instances in the charts. Review the original higher-resolution data before declaring a breach.

### Rebuild the HTML from the same skill folder

`python scripts/build_investigative_replay.py --data examples/utah_forge_16A_78_32/rig_5min.csv --events examples/utah_forge_16A_78_32/report_milestones.json --output examples/utah_forge_16A_78_32/replay.html`

`python -m pytest -q tests/` (6 automated comparator tests). Tool outputs and example case are isolated under the same root `liner-hanger-rca-skill` folder. No additional application repository or development folder is required.

### Demonstration of how the deviation list works (synthetic, not Utah FORGE)

`python scripts/check_procedure.py --rules examples/synthetic_procedure_demo_rules.json --telemetry examples/synthetic_procedure_demo_5min.csv`

This completely **fictional** test has one continuous 10-minute out-of-limit episode (two 5-minute rows) that is correctly listed as one *apparent deviation*. Its approval and limits are test fixtures **not** field criteria or genuine authorisations. Real jobs need genuine approved procedures and verified source signals.

## V1.3.1 — Second retrospective example: Utah FORGE 16B(78)-32

See `examples/utah_forge_16B_78_32/README.md` and open its offline `replay.html`. This example adds real Pason 10-second rig measurements, 198 classified slip-to-slip connections and a measurement-driven 7-inch **production casing** schematic (not a liner-hanger setting operation). The casing-shoe animation is based on the `Bit Depth` sensor proxy, whose exact string mapping needs independent confirmation. No approved job procedure supplied; do not mark process violations.


## V1.4 — Earlier notebook workflow (superseded by the V1.5 contextual editor)

Open `examples/utah_forge_16B_78_32/replay.html` in Chrome or Edge. The existing charts and synchronized casing-run playback gained an engineer-controlled investigation notebook; its below-chart editing workflow has been replaced in V1.5:

- **Select range on chart** → drag over a pressure, hookload, torque, RPM, flow or depth trend. The same interval is highlighted on every trend. Click a chart normally to move the shared playback cursor.
- A **zoomable detail chart** provides more precise selection. Click **Annotate zoomed range** to record the narrower interval, or **Mark ±5 minutes at cursor** for an immediate bookmark.
- Add an observation title, engineering interpretation, reviewer name/status, source/procedure references and supporting document(s). Edit, revisit, inspect attachments or delete saved records.
- **Export evidence JSON** for source-linked notes and embedded files; **Import** restores saved evidence for this well; **Generate printable report** creates a standalone HTML report (Print → Save as PDF).
- **Find review candidates** provides unapproved screening suggestions for signal changes; it makes no procedural compliance or root-cause claims.

**Data qualification:** 16B is a full-length casing installation, not a liner hanger, with 1-minute median charts derived from a 10-second Pason record. Its `Bit Depth` channel is a **shoe-position proxy**, and the Pason timestamp zone is **not independently verified**. Approved running criteria were not supplied; compliance is therefore not verifiable.

**Attachment warning:** The local browser draft only retains note metadata; file bytes are preserved in an exported JSON evidence bundle. The offline demonstration is not a multi-user evidence database. Keep sensitive case files in an approved repository.

Reusable source is in `assets/annotation_workspace.js`, `assets/annotation_workspace.css`, `scripts/add_annotation_workspace.py`, with a detailed protocol in `references/ENGINEER_ANNOTATIONS.md` and example record format in `schemas/annotation_record_v1.4.example.json`. This injector supports the 16B-style replay markup; adapters for other layouts will require separate validation.

Run `python -m pytest -q tests/` for existing procedure checker and annotation regression tests.


## V1.5 — In-chart contextual annotation UI

The **same** standalone 16B replay now has point/range annotations directly on measured telemetry. It is an upgrade to the existing skill, not a separate application.

1. Click **Select chart range** and drag on a plot, or click **Mark point at cursor** (or **Mark ±5 min**). A contextual annotation editor opens immediately beside the chart; **no scrolling to the bottom of the page** is required.
2. Add title, notes, category, reviewer and references, and optionally attach supporting files. Save to retain the **marked time window across every channel**. The saved overlay is explicitly a time selection, not automatically a procedural breach.
3. With playback paused, **hover over a saved band** to read its title/summary, then **click the band** to reopen the record for editing. Tiny point annotations remain selectable within a narrow pixel tolerance.
4. Use **Annotations** to open a collapsible **right-side evidence register** with filtering, editing, attachments and evidence/report exports.
5. During playback, **Show annotations during playback** optionally displays small, nonblocking saved-note notifications as the cursor crosses an annotation. **Pause & inspect** opens its editor; switching the checkbox off suppresses notifications. Saved annotations never force playback to stop.
6. **Export evidence JSON** before leaving if attached files matter. Browser local draft storage does not retain file bytes; exported bundles do. Reports remain standalone HTML for printing to PDF.

The `scripts/add_annotation_workspace.py` injector remains idempotent and now supports upgrading an existing v1.4 replay into v1.5 (without stacking duplicate notebooks). Its data adapter still targets **16B-style replay HTML only**. Verified on an actual browser with manual range selection, hover reopening, point bookmarks, sidebar, playback notifications, user opt-out and evidence/report exports. No assertion of casing-tong makeup values or verified procedure compliance has been added.

To test the skill in place: `python -m pytest -q tests/`.
