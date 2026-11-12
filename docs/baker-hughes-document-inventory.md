# Baker Hughes Liner-Hanger Documentation Inventory — Preliminary

**Date:** 2026-11-12  
**Task:** LH-001 (focused Baker Hughes source inventory; overall asset audit remains open)  
**Decision status:** User confirmed **Baker Hughes retrospective fault finding** as release v1 on 2026-11-12. This file contains the evolving technical coverage audit, not approval of individual model rules.

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

## 2026-11-12 verified update — original Baker Hughes PDFs supplied and inspected

**This section supersedes the earlier 'not found' statements above.** Original file contents have now been provided directly in this conversation and inspected. Do **not** commit the copyrighted PDFs to the repository.

### Source identities and duplicate check

| ID | Actual PDF | Pages | SHA-256 | Source status |
|---|---|---:|---|---|
| BH-SYS-2016 | `Liner Hanger Systems.pdf` — *Introduction to Wellbore Construction - Liner Hanger Systems* | 132 | `6ecb23760a3036207eed11e71b784adca1d5a03268bae104eaf9a5e699c47c8c` | Original user-supplied Baker Hughes 2016 self-study guide |
| BH-HYD-2020 | `Liner Hanger Hydraulics.pdf` — *Liner Hanger Calculations and Hydraulics - Theory* | 99 | `ad123443c94d987d48d604f5f5ff46307e40a7b17ffd0ca27af34f14188d5df9` | Original user-supplied Baker Hughes 2020 self-study guide |
| Duplicate | `Liner Hanger Calculations and Hydraulics-Theory - Copy.pdf` | 99 | Same SHA-256 as BH-HYD-2020 | **Exact duplicate**, not independent evidence |

### BH-SYS-2016 equipment coverage and source pages (PDF 1-indexed)

| Category | Equipment | PDF page(s) | Source-reported product family / referenced further unit |
|---|---|---:|---|
| Mechanical hangers | Hyflo III; CMC; RCM II; FLEX-LOCK | 28–31 | H29222 / SU 4364; H29210 / SU 4268; H29226 / SU 10018; H29413 / TU 4669 |
| Hydraulic hangers | Hyflo II; HMC; HSR II; FLEX-LOCK; ControlSET FLEX-LOCK; SDD | 33–39 | H29233 / TU 4300; H29223 / SU 4269; H29227 / SU 10008; H29410 / SU 10124; H29416 / SU 100935; H29262 / text SU 4793 vs URL 4739_TU discrepancy |
| Liner-top packers | Hyflo III, ZXP, ZXP Ultra, ZXHD, ZXPN, ZXP-D | 42–47 | Multiple model/variant identifiers; see original pages |
| Integrated combos | INLine, Z-Flex, ZXP with integral FLEX-LOCK, UniFlex, SLZXP, SLP-R, 3D | 53–59 | Family-level explanation and several identifiers |
| Cementing hardware | Landing collars, floats, cementing heads, plugs and darts | 63–85 | Family overviews and variants |
| Rental tools | HRD-E, 2RH, C-2; packoffs and ball seats | 87–104 | HRD-E H26693 (p89), 2RH H26523 (p90), C-2 H26521 (p91) |
| TORXS | Completion/tool system | 107–110 | Introductory coverage |

**Important correction to prior code audit:** LinerForge classified SDD as mechanical, but **BH-SYS-2016 explicitly calls SDD a hydraulic-set liner hanger** on PDF p38. The original manufacturer document takes priority; flag catalog value for later correction, **do not modify LinerForge automatically**.

### BH-HYD-2020 engineering and investigative coverage

- PDF pp9–19: RS, PBR, swab-cup sealing and ball-seat arrangements, including single and dual packoff configuration.
- PDF pp26–80: capacity, buoyancy, string weight, stretch, tensile and overpull, torque/turns, hydrostatic/differential pressure, piston force, pipe strength, circulation and liner-top testing, reversing cement. **Exercises and assumed values are not universal product ratings.**
- PDF pp82–96: dedicated troubleshooting module:
  - p82: ball drop / water hammer and premature seat shear.
  - pp83–85: setting hanger forces, light liner, drag/tagging, load indications.
  - pp86–90: hydraulic sequence, running-tool release and differing internal/external fluid columns.
  - pp91–94: cement displacement, loss/plug/packoff problems and circulating-pressure interpretation.
  - pp95–96: liner-top packer load and packoff unstabbed conditions.

These guides support **structured, equipment-aware retrospective troubleshooting and source-backed hypotheses**, **not** verified exact model/size/revision actuation pressures or definitive physical failure conclusions. Source BH-SYS-2016 repeatedly refers engineers to its Service Units / Technical Units for additional tool detail. The training examples and LinerForge generated ratings must never be loaded as universal field limits.

**Source risk:** Each PDF contains Baker Hughes copyright; keep source bytes private and do not publish or commit them. Derived metadata, short source abstracts and original citations may be tracked; check use permissions before distribution.

### Updated inventory deliverable

The companion workbook `Liner_Hanger_Multi_OEM_Inventory_Source_Verified.xlsx` extends the prior multi-OEM workbook and adds:
- `Original PDF Register` — source names, hashes, rights considerations.
- `BH Source-Cited Coverage` — 36 directly mapped tool/group entries with PDF page references, product IDs, further OEM unit requests and status **Partial - guide only**.
- `Troubleshooting Evidence` — nine source-cited concern areas, not live operational instructions.

The workbook was generated as a conversation artifact; **not** yet committed to GitHub. The manufacturer-extensible backend decision is unchanged; only BH has reviewed sources to date. Halliburton remains future/unverified.

**LH-001A status:** **In progress, substantial document recovery completed**. Still requires tool-by-tool review of exact technical-unit content and an engineering sign-off criteria decision. Do not mark full OEM troubleshooting coverage complete.

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

## Scope decision confirmed

The user confirmed **Baker Hughes-only retrospective fault finding as first skill release** on 2026-11-12. This does not certify full tool/revision coverage. Broad engineering functions and additional manufacturers remain deferred. See [first-release-scope.md](first-release-scope.md).

## Next step

**LH-001 remains unchecked.** To complete the tool-specific part of the inventory, find/access the original training documents, review the per-tool technical coverage and obtain user confirmation of intended release scope. Do not report the task as complete on the basis of the public source register alone.
