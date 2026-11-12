# Baker Hughes Liner-Hanger Documentation Inventory — Preliminary

**Date:** 2026-11-12  
**Task:** LH-001 (focused Baker Hughes source inventory; overall asset audit remains open)  
**Decision status:** Assessment only. **No scope change approved or implemented.**

## Evidence examined

Examined **actual ZIP member inventories and reference text** of these existing personal Library archives:
- `liner-hanger-investigation-skill-v1.5.zip`
- `liner-hanger-investigation-skill-v1.4.zip`
- `liner-hanger-rca-skill-knowledge-v1.2.zip`

Also searched accessible current Project and personal Library file names/content for Baker Hughes manuals/specifications, and reviewed project source-register statements. **Search scope is limited to accessible materials.** Documents in other ChatGPT conversations/projects, local Windows folders or external accounts may not be surfaced here. No conclusion that such documents do not exist elsewhere.

## Primary finding

**The investigation framework exists; a manufacturer/model/revision-specific Baker Hughes troubleshooting knowledge base has NOT been verified.** No original Baker Hughes training PDF, full running/setting manual, engineering drawing, pressure/force specification sheet, troubleshooting matrix or revision-controlled operating procedure was found in the inspected skill archives or in the accessible Library filename search.

The v1.5 skill package does contain:
- `SKILL.md`, `references/KNOWLEDGE_BASE.md`, `references/SOURCE_REGISTER.md`, `references/INGESTION_AND_RULES.md`
- Method, intake, hypothesis, procedure-compliance, annotation and reporting references.
- `scripts/check_procedure.py`, `scripts/extract_procedure_candidates.py`, `scripts/build_timeline.py`, replay and annotation utilities.
- Tests for procedure checks and annotations.
- Historical Utah FORGE/Pason rig-data examples and HTML investigative replays.

These are technical **method/tools/fixtures**, not original BH manuals.

## Named Baker Hughes sources found in v1.5 source register

| ID | Identified source | Available coverage | Evidence status | Suitability for tool-specific troubleshooting |
|---|---|---|---|---|
| BH-01 | [Baker Hughes — Liner hanger systems](https://www.bakerhughes.com/integrated-well-services/integrated-well-construction/completions/liner-hanger-systems) | General product-family/activation concepts (mechanical, hydraulic, acoustic) | Public site cited in the skill; current page/revision not independently revalidated during this inventory | **Insufficient** |
| BH-02 | [Baker Hughes — FLEX-LOCK liner hanger system](https://www.bakerhughes.com/completions/liner-hanger-systems/liner-hangers/flexlock-liner-hanger-system) | Public description of anti-preset / locking concepts | Public site cited in the skill; no exact tool revision/spec sheet found in package | **Insufficient** |

`SOURCE_REGISTER.md` also references SLB, Weatherford, Halliburton and Packers Plus public sources. These are comparative industry background, **not** evidence for Baker Hughes tool specifications.

### Coverage assessment

| Required item | Status | Gap |
|---|---|---|
| Generic investigation workflow | Present in skill | Must be regression-tested after import |
| Historical CSV / event timeline | Present in skill examples/scripts | Need validation against cases and source timing |
| General hanger-running, setting, release, cementing concepts | Present as OEM-neutral background | Must not be treated as specific BH tool sequence |
| Baker Hughes tool-family naming | Partial (only portfolio and FLEX-LOCK positively identified) | Need per-tool inventory |
| Exact Baker Hughes model / size / revision / assembly BOM | **Not verified** | Needed before applying tool-specific limits or design logic |
| OEM running, setting and release procedure | **Not found** | Critical |
| Tool setting/release pressure/force/torque criteria | **Not found** | Critical |
| Approved internal flow path, component and mechanism drawings | **Not found** | Important for attributing physical failure |
| OEM fault-tree / troubleshooting tables | **Not found** | Important |
| Verified BH case outcomes, inspection reports | **Not found** | Required for stronger root-cause confirmation |

**Rating key:** `Sufficient` means documented mechanisms, exact model/revision and necessary operating criteria plus engineer review; `Partial` means some source material exists but key rules are missing; `Insufficient` means no validated tool-level procedure/spec basis. These ratings concern **tool-specific troubleshooting**, not generic retrospective anomaly analysis.

## Recommended next evidence request (no broad rebuild)

Ask the user to locate the original Baker Hughes training/engineering PDFs or images they remember using in another ChatGPT folder, and provide them in this Project or identify their original ChatGPT Project/conversation. For each document:
1. Record filename, actual tool name/family, size/model, part number, revision, date, origin and right to use.
2. Confirm whether it covers internal mechanism and flow path, component configuration, setting/release sequence, pressure/force limits, troubleshooting and inspection.
3. Extract a **per-tool coverage matrix**, with source document/page references.
4. Classify each tool as `Sufficient / Partial / Insufficient`; engineer-review any quantitative interpretations.
5. Decide whether a Baker Hughes-only retrospective troubleshooting **first release** is feasible **before** changing START_HERE, TODO or AGENTS.

**Do not upload protected Baker Hughes manuals to a public repository**. Even if the user can lawfully review them here, redistribution in GitHub may require authorization. Prefer a private/local source vault and a sanitized rule index.

## Scope decision pending

Two viable product directions remain under discussion:
- Broad liner-hanger engineering skill, with optional investigation.
- **Baker Hughes-only retrospective fault-finding skill**, leveraging the existing investigation framework.

No engineering direction is committed until the user explicitly decides following the documentary coverage audit.

## Next step

**LH-001 remains unchecked.** To complete the tool-specific part of the inventory, find/access the original training documents, review the per-tool technical coverage and obtain user confirmation of intended release scope. Do not report the task as complete on the basis of the public source register alone.
