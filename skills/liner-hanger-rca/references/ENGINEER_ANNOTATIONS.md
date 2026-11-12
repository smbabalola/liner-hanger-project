# V1.5 — Engineer-controlled telemetry annotations and documentation

## Purpose
The annotation workspace extends the existing retrospective investigation skill. It is **not** another application. Engineers can highlight a measured signal interval, zoom into it, capture observations and competing explanations, link supporting records, and export an evidence notebook for technical review.

## How engineers use the 16B example
1. Open `examples/utah_forge_16B_78_32/replay.html` in a local browser. The original playback, moving casing schematic, telemetry trends and event checkpoints remain intact.
2. On the existing rig charts choose the **±30 min** view for close inspection. Click **Select chart range** and drag left-to-right (or right-to-left) across any channel. Alternatively use **Mark point at cursor** or **Mark ±5 min**. A contextual editor opens at the selection.
3. The selected time window is highlighted across all eight charts. In the chart-side editor, inspect the selected channel's 1-minute median measurements and drag across its enlarged chart to zoom further. **Annotate zoomed range** uses that more precise interval.
4. Document the observation separately from an interpretation; include alternatives and what would falsify them. Record the engineer's identity, status, job/procedure reference and any missing evidence. Attach supporting PDF/image/text/docs *locally*.
5. Saved marks persist across all charts. Hover a marked interval to preview it when paused; click it to reopen. Open **Annotations** to show the collapsible evidence register with **Inspect on chart**, **Edit**, **View attachments** or **Delete**. Export a portable JSON case file with embedded attachment contents or produce a standalone printable HTML investigation report (browser Print → Save as PDF).
6. To restore another session or share within an approved private workflow, import the evidence JSON. JSON imports are rejected when the case ID does not match the current well.

## Provenance and evidence controls
- The selected interval includes Pason clock timestamps, signal name and engineering unit, underlying row indices, source-window depth proxy, source description, author, status, creation/update times and references. The JSON export also captures the selected signal's min/max and sample coverage.
- The 16B chart is **1-minute median data** derived from the public 10-second Pason archive. It can miss peaks or transients. The original 10-second source remains in the package for verification; the notebook does not claim that the 1-minute display proves a short-duration event.
- The 16B Pason Bit Depth channel drives the casing schematic only **as a shoe-position proxy**. The exact tool/sensor mapping is not verified.
- The Pason clock offset relative to UTC and daily reports is **not verified**; this limitation travels with every exported record.
- Source material may be missing or misleading. Never infer approval, correct procedure, confirmed root cause, safe-to-operate status or a specific tool mechanism from a screenshot/annotation.
- Engineer-authored `procedure_question` is a request to investigate—not an approved rule violation. A confirmed deviation can be entered only using the separate approved-procedure checking workflow and verified chronology.

## Automatic suggestions
The optional **Find review candidates** action scans only the plotted 1-minute summaries. It surfaces the three largest temporally separated single-minute changes in **hook load and rig standpipe pressure**, plus near-zero RPM channel characteristics if found. These are unsupervised prompts, **not failures, abnormality thresholds, compliance verdicts or root causes**. Every suggested finding remains a draft until an engineer explicitly saves it. Do not treat the absence of suggestions as proof of no problem.

## Attachments and privacy
Attachments up to 6 MB each and 18 MB per annotation are read locally and included as data URIs in exported JSON. Supporting file bytes are **not** retained in browser local storage and are **not** included in the printable HTML report; that report lists their names. Engineers must export the JSON before closing if attachments matter and keep it in their approved evidence repository. Browser local storage is best-effort for note metadata and may be unavailable depending on browser/file origin. The offline HTML does not transmit files to any service. This is a prototype, not a hardened multi-user records database. Use only authorized, appropriately protected case material.

## Reuse for other jobs
The v1.5 module is reusable and supplied as `assets/annotation_workspace.js`, `assets/annotation_workspace.css` and `scripts/add_annotation_workspace.py`. The injector currently supports the **16B-style self-contained `caseData` + `charts` HTML structure**, and has been tested on this example. It is idempotent; the existing records and display are preserved. Adapters for other schemas (such as the earlier 16A replay) should be added and separately tested rather than silently assuming signal alignment.

From the root of the skill:

```bash
python scripts/add_annotation_workspace.py --html examples/utah_forge_16B_78_32/replay.html
python -m pytest -q tests/
```

Always preserve the unmodified original rig records; annotated JSON is derivative evidence and engineering interpretation, not raw rig data.


## New chart-first interaction (v1.5)
- **Create:** Select **Select chart range** and drag, or use **Mark point at cursor** / **Mark ±5 min**. An in-place contextual form opens beside the selection automatically, including the zoomable detail chart and full evidence fields. Selecting a zero-width interval is valid for a point annotation.
- **Inspect:** Saved time windows remain highlighted across all channels; while paused, hovering reveals a title, status and short note. Click any saved highlighted band to open that exact note for editing. Overlaps prioritize the shortest interval; the side register lists all annotations.
- **During playback:** A saved annotation crossing the playhead creates an optional small, nonblocking notification, never an automatic modal or pause. Select **Pause & inspect** to stop playback and inspect it. Disable **Show annotations during playback** to suppress notifications.
- **Find notes:** The **Annotations** button opens a collapsible right-side register, with type filtering, editing, attached-file recovery after JSON import, and exports. The interface does not require scrolling to the bottom of the charts.
- **Evidence:** All saved notes are engineer observations or review prompts. A highlighted interval is **not** proof of a failure, causal mechanism or procedure noncompliance. Keep UTC/Pason clock uncertainty and 1-minute aggregation in the evidence record.
- **Storage:** The standalone offline HTML uses best-effort browser localStorage for note metadata. Attachments are not backed up until exported JSON. The notebook provides no authenticated multi-user access control or tamper-proof audit trail; such capabilities are out of scope for this version.
