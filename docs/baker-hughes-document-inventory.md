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

## 2026-11-12 addendum — original documents recovered in historical conversation record

A separate search of prior ChatGPT discussion found that **on 19 March 2026**, during **LinerForge** tool-template work, the user and assistant worked with uploaded Baker Hughes PDFs reportedly titled:
- `Liner Hanger Systems.pdf`
- `Liner Hanger Hydraulics.pdf` (also referred to as `Liner Hanger Calculations and Hydraulics`).

The historical analysis identified equipment names and families including **Hyflo III, Hyflo II, CMC, RCM II, FLEX-LOCK, HMC, HSR II, ControlSET FLEX-LOCK, SDD, ZXP / ZXP Ultra / ZXHD / ZXPN, HRD-E, 2RH**, and components such as **RS/PBR, landing collars, plugs, darts, balls, floats and shoes**. Additional names in that discussion: **ZXP-D, INLine, Z-Flex, UniFlex, C2, COMPdril / COMPdril Solo, SureFlow, Bullet seal, JMZX and SISOSR**. These are **historically discussed names, not presently verified tool-by-tool manual coverage**.

**Critical provenance distinction:** The original PDF bytes, page ranges and revisions were **not retrieved** in the present Library/Project search. This addendum corrects the earlier implication that no original manuals had ever been uploaded: the March conversation indicates that they **were** uploaded and used there. However, their technical coverage, operating limits and suitability for troubleshooting **cannot be independently certified** until the PDFs are re-accessed. The earlier discussion described their content as adequate for **family-level structure, component functions, hydraulic/packoff concepts, sequence modeling and planning-grade rule-based simulation**, not full certified diagnostic rules/curves for every tool.

**Follow-up:** Locate the March 19, 2026 LinerForge chat attachment copies or reattach PDFs in this Project; inventory their pages/model references and only then re-rate specific tools. The prior chat title and folder name are not yet known.

---

## 2026-11-12 follow-up — read-only LinerForge catalog inspection

Read-only examined existing private repo `smbabalola/LinerForge`, source:
- `src/features/liner-hanger-simulation/services/bakerToolCatalog.ts`
- `src/features/liner-hanger-simulation/services/platformToolPackLibrary.ts`

**Confirmed source-code inventory:** `bakerToolCatalog.ts` defines **38 named catalog templates** (some are tools, some are subassemblies/accessories), grouped here by the code's categories:

| Category | Catalog entries |
|---|---|
| Hangers | Hyflo III; CMC; RCM II; FLEX-LOCK Mechanical; Hyflo II; HMC; HSR II; FLEX-LOCK Hydraulic; ControlSET FLEX-LOCK; SDD |
| Packers / combinations | Hyflo III Packer; ZXP; ZXP Ultra; ZXHD; ZXPN; INLine; Z-Flex; ZXP with Integral FLEX-LOCK; UniFlex |
| Running / setting tools | HRD-E; 2RH; Hydraulic Pusher Tool; Setting Sleeve; Setting Dog Sub |
| Packoff | RS Packoff; PBR Packoff; Swab Cup Assembly; Drillable Packoff Bushing |
| Ball-seat equipment | ST Landing Sub; DOBS |
| Cementing accessories | Type I Landing Collar; Type II Landing Collar; LFC Landing Collar; COMPdril Landing Collar; COMPdril Solo / LF Plug System; Float Collar; Float Shoe; Pump-Down Plugs / Balls / Darts |

**CRITICAL ENGINEERING FINDING:** The code's `operatingEnvelope: {}` is empty on **all 38 catalog records**. Many records list `requiresEngineeringInput` for pressure/load/temperature ratings. The same source contains generic `deriveRatingsForRole()` values for tensile, yield, burst and collapse, plus `inferredLength()` and `deriveInAirWeightForRole()`. These are **software heuristics / default estimates, NOT confirmed Baker Hughes product ratings or dimensions**. `deriveBakerToolProfileOverrides()` contains hardcoded simulated seat pressure gains and set-confirmation thresholds; none were backed by source/part/revision citations in the examined code. These numbers **must not be imported into the engineering skill as OEM specification or fault-finding thresholds**.

`platformToolPackLibrary.ts` labels seed pack calibration `maturity: "planning_grade"` and `engineeringBasis: "Seeded from Baker Hughes system and hydraulics references."` It also marks certain seeded packs as application-`approved`; that is a **software workflow status**, not verified manufacturer technical approval.

**Result:** We have a substantially richer **catalog/assembly taxonomy and simulation scaffold** than the skill ZIP alone showed. No source-verifiable exact model/size/revision specs or manufacturer-validated diagnostic thresholds were recovered from these files. Read-only LinerForge inspection only; no edits made there.

**Original files:** prior conversation references `C:/Users/smbab/OneDrive/Documents/Projects/LinerForge` but this path is on the user's PC and not directly accessible from this cloud environment. Original PDFs still need to be reattached or located by the user.

---

## Primary finding

**The investigation framework exists; a manufacturer/model/revision-specific Baker Hughes troubleshooting knowledge base has NOT been verified.** No original Baker Hughes training PDF, full running/setting manual, engineering drawing, pressure/force specification sheet, troubleshooting matrix or revision-controlled operating procedure was found in the **inspected skill archives or current accessible Library filename search**. Historical March 2026 conversation evidence, now documented above, **does identify two previously uploaded original PDFs**; their actual file contents are not currently accessible for verification.

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
