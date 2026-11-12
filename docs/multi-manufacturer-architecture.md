# Multi-Manufacturer Engineering Architecture — Decision Record

**Date:** 2026-11-12
**Status:** AGREED — manufacturer-extensible backend architecture.
**Product scope still under discussion:** a dedicated fault-finding first release versus the broader engineering skill. Do not assume this architectural decision resolves that separate scope question.

## User-facing concept

The eventual application offers **Manufacturer → Equipment family → Model/size → Revision/configuration** selection. The user should *not* have to manage separate applications for Baker Hughes, Halliburton, etc. A single shared case and retrospective investigation workflow is used.

### First manufacturer

- **Baker Hughes (BH):** first documentation inventory and candidate rules.
- **Halliburton (HAL):** future integration; no assumption that adequate documentation has been acquired.
- **SLB (SLB), Weatherford (WFRD):** future placeholders only. Their brand selection must not imply diagnostic functionality exists.

## Backend rule

`manufacturer_id + equipment_family_id + model_id + tool_revision + job_procedure_revision` selects the **allowed**, source-traceable equipment knowledge pack. If any needed identity is absent or a tool pack fails its quality gate, the backend restricts analysis to manufacturer-agnostic observations and declares that tool-level conclusions are unavailable.

### Proposed records (design, not implemented code)

- `Manufacturer`: id, display_name, enabled_for_inventory, enabled_for_analysis.
- `ToolModel`: manufacturer_id, family, model, variants, allowed revisions, supported configuration.
- `KnowledgePack`: tool reference, revision, source URLs or protected-document IDs, document pages, review status, effective dates, approval metadata, rights-to-use.
- `OperatingStage`: source-approved planned sequence / expected state / permitted observations.
- `DiagnosticRule`: applicability conditions, predicted observable signatures, alternative mechanisms, exclusions, testing references, provenance and validation status.
- `Case`: equipment identity, job information, rig telemetry, operations log, configuration, fluid and cementing context, evidence and conclusions.

All vendor-specific fields are namespaced by manufacturer and model/revision. The **case structure, evidence/provenance system, timeline engine, reporting pipeline and generic calculation utilities** are shared across OEMs.

## Isolation and selection rules

1. Selecting `BH` must never pull a Halliburton or SLB equipment-specific setting/release limit.
2. Selecting `HAL` before approved Halliburton documentation exists must display **unavailable/unverified**, never fall back to Baker Hughes rules.
3. Changing manufacturer/model/revision invalidates any cached OEM-specific interpretation; preserve original evidence, annotations and logs.
4. Generic surface-sensor analysis may continue when OEM rules are unavailable; show restrictions and unknowns.
5. Source precedence: approved job procedure → exact OEM manual/spec revision → independently reviewed model knowledge → generic public background.
6. No speculative numerical setpoints; no unsourced internal failure attribution.
7. Exact manufacturer/model/revision and evidence-quality state must appear in the final report.
8. Verify each future manufacturer independently with tests, authorized documentation and an explicit enabled feature list.
9. Restrict copyrighted/confidential OEM manuals to authorized storage and access; do not automatically commit protected source PDFs to GitHub.

## Compatibility and test gates

- **Cross-OEM isolation:** switching from BH to a future HAL placeholder cannot retain BH rule results.
- **Absent OEM coverage:** generic evidence review works, OEM-specific diagnosis remains disabled.
- **Revision mismatch:** selecting an unsupported revision blocks revision-specific calculations and rules.
- **Source traceability:** every vendor rule resolves to a manufacturer/model/revision document and page/source register.
- **Retrospective only:** the first release gives no live operational setpoints, well-control instructions or equipment-control commands.

## Document inventory

The current working Excel spreadsheet is **`Liner_Hanger_Multi_OEM_Inventory.xlsx`**, created separately as a conversation artifact. It has tabs **READ ME, OEM Registry, Baker Hughes Tools, Source Register, Coverage Criteria, Work Queue**. The working copy must be placed under `docs/inventory/` after confirming confidentiality and permissions. Until then, the existing [Baker Hughes inventory](baker-hughes-document-inventory.md) is the repo-resident audit.

Historical March 2026 LinerForge chat identified `Liner Hanger Systems.pdf` and `Liner Hanger Hydraulics.pdf` / `Liner Hanger Calculations and Hydraulics`, but **actual original PDF bytes and page-level tool coverage have not been retrieved in the current inventory**. Do not mark any exact model/revision 'diagnostically supported' on chat recollection alone.

## Development order

1. Recover, verify and classify BH documents and tool coverage (`LH-001`).
2. Decide the first release scope (BH-only fault-finding or broader skill) explicitly with the user.
3. Add the manufacturer registry and shared case model without UI work.
4. Activate only reviewed BH model/revision packs with test cases.
5. Add Halliburton/other providers via the same audited onboarding method later.
6. Only after skill sign-off, create the app interface and manufacturer selector.
