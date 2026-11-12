# LH-001 — Existing Skill and LinerForge Asset Audit

**Audit date:** 2026-11-12  
**Scope:** Baker Hughes retrospective fault-finding skill v1; read-only review of pre-existing assets  
**Status:** **Initial archive/code audit completed; LH-001 stays open** pending local prototype verification and source-dependency review  
**Do not imply engineering/operational validation from automated software tests.**

## 1. Evidence examined, and reproducibility

### Existing personal-Library ZIP archives

| Source | SHA-256 prefix | Members | What was examined |
|---|---|---:|---|
| `liner-hanger-investigation-skill-v1.5.zip` | `9b6e2f04f3f2100124` | **46** | Full ZIP member manifest; extracted scripts, references, README, tests; automated regression test run |
| `liner-hanger-investigation-skill-v1.4.zip` | `359c39915e433b8854` | **45** | ZIP content manifest, direct member hash comparison against v1.5 |
| `liner-hanger-rca-skill-knowledge-v1.2.zip` | `4112df8761543ea2fc` | **14** | ZIP member inventory; earlier investigation knowledge and template package |

These are **available personal-Library attachments**, not files currently committed to this GitHub repository. All three original ZIPs were copied to a private ephemeral audit workspace for inspection; **no proprietary OEM manuals were added**.

The actual v1.5 package root is `liner-hanger-rca-skill/`. It contains `SKILL.md`, `README.md`, **5 Python scripts**, **3 automated test files**, **11 references**, **4 schema examples**, `assets/annotation_workspace.{js,css}` and offline historical/synthetic examples. The examples include large telemetry CSVs, browser HTML replays and a preview image; these should not all be included in the shipping core by default.

Comparison against v1.4: **37 members unchanged**, **8 existing members changed**, **1 new test** (`tests/test_chart_modal_v15.py`), and **no members removed**. The newer update focuses on annotations/editor behaviour, not a rewritten procedure engine.

### Automated software verification

On **2026-11-12**, the extracted **v1.5** package was tested with:

```powershell
cd liner-hanger-rca-skill
python -m pytest -q tests/
```

Result: **14 passed in 3.80s** (execution in cloud workspace with available Python/pytest; the user's Windows machine has NOT yet been tested). The older README's `python -m unittest discover` is not a valid substitute for the pytest suite: it found **0 tests** in this audit.

**Test coverage limitations:** Existing tests cover specific procedure-checker and annotation integration/HTML behaviours. Passing does **not** validate tool-specific mechanical failure diagnoses, every browser function, the rig-data import modes, vendor operating thresholds, exact BHA placement or real-case accuracy. No physical BH historical incident with independently confirmed failure mode was processed during this audit.

## 2. Component-level reuse decision

| Area | Existing component(s) | Reuse classification | What must change for v1 |
|---|---|---|---|
| Investigation method and uncertainty rules | `SKILL.md`, `references/INVESTIGATION_METHOD.md`, `HYPOTHESIS_LIBRARY.md` | **Reuse with BH-specific extension** | Five documentary BH investigative workflows; explicit equipment source gate |
| Evidence intake and risk controls | `references/DATA_INTAKE.md`, `INGESTION_AND_RULES.md`, case and knowledge schemas | **Reuse with extension** | Manufacturer/model/revision, tenant identifier, BHA geometry, tool provenance, no cross-OEM rules |
| Procedure checking | `scripts/check_procedure.py`, `PROCEDURE_COMPLIANCE.md`, rulebook schema, tests | **Reuse with guardrails** | Approved job procedure/revision, tool-specific applicability and sample-quality tests |
| Procedure candidate extraction | `scripts/extract_procedure_candidates.py` | **Reuse as unapproved extraction** | No automatic conversion of extracted training values into approved settings |
| Chronology / timeline | `scripts/build_timeline.py` and report milestone examples | **Reuse, validate against incoming cases** | More robust units/timezone/time source, measured vs reported event status |
| Historical rig-data replay | `scripts/build_investigative_replay.py`, 16A/16B examples | **Reuse as testing/reference asset** | Must not imply 16B full-length casing was a liner-hanger run; do not make HTML the core v1 engine |
| Evidence annotations | `assets/annotation_workspace.{js,css}`, `scripts/add_annotation_workspace.py`, `ENGINEER_ANNOTATIONS.md` | **Reuse, later interface bridge** | Targeted to 16B-style replay HTML; browser local persistence/attachment limitations; CLI/backend evidence records first |
| Reporting | `references/REPORT_TEMPLATE.md`, JSON exports | **Reuse and extend** | Consistent report generator, evidence IDs, BH model and limitations, engineer review status |
| Validated actual BHA geometry and liner-top depth | No demonstrated verified skill module in v1.5 | **Missing; bounded addition** | Tally- and reference-dependent position calculations, planned vs reconstructed; exact component reference points |
| Manufacturer/tenant isolation | No demonstrated approved multi-OEM knowledge-pack backend in v1.5 | **Missing; bounded addition** | BH-only active pack and explicit unsupported manufacturer/model/revision behaviour |
| Five BH-specific failure interpretations | No demonstrated source-gated implementations in v1.5 | **Missing; bounded addition** | BH manual page links, mechanisms, alternative hypotheses and evidential uncertainty |
| Scientific/engineering validation | Limited synthetic procedure fixtures | **Incomplete** | Independent known-answer, normal controls, anomalous scenarios, engineering sign-off |

**Operational data scope:** primary signals are standpipe pressure, hookload, torque, RPM, depth, pump rate/strokes, returns/flow and job/fluid logs. Wireline/formation-evaluation logs were **not** the recorded team's core data and are **not** required.

## 3. LinerForge reference code (read-only)

Examined `smbabalola/LinerForge` at its default branch (do not assume `main`), including:
- `src/features/liner-hanger-simulation/services/bakerToolCatalog.ts` (**84,646 text characters**).
- `src/features/liner-hanger-simulation/services/platformToolPackLibrary.ts` (**29,569 text characters**).

The Baker Hughes catalog has **38 named tool/assembly templates**, spanning hangers, packers, running/setting tools, packoffs, seats and cementing accessories. It is useful for an **equipment taxonomy, assembly component roles, and configuration screens later**.

**Critical unverified/calculated material in the catalog:**
- `inferredLength(role)`, `deriveInAirWeightForRole(...)` assign **illustrative** geometry/weights by role.
- `deriveInternalFeatures(...)` positions internal reference features using **fractions of assumed component length**.
- Catalog `operatingEnvelope: {}` is empty across all 38 templates; model/size/revision ratings are not populated.
- Seed pack `maturity: "planning_grade"`; software `status: "approved"` is a **workflow state**, **not** a BH engineering endorsement.
- Earlier audit also identified generic generated strength ratings and simulated pressure gains. These **MUST NOT** become field criteria.

**BHA placement requirement (user decision):** For v1, the backend should accept actual measured assembly/tally lengths, liner string segments and known depth reference; compute **liner top**, **hanger slip-setting reference**, **packer**, **landing collar**, **float collar**, and **shoe** positions separately, with clear measurement datum, MD units and uncertainty. If the source tally/anchor is absent, return **undetermined**, never silently use guessed role lengths. Capture **planned** and **as-run** values independently. Check overlap against prior casing shoe; quantify string stretch only using verified inputs and a separately tested method. Preserve LinerForge's broader placement optimisation for later.

**Category conflict:** The original BH Systems training guide PDF p38 describes **SDD as hydraulic-set**; prior LinerForge catalog categorised it as mechanical. Manufacturer-authored source takes priority for the inventory, but model/revision questions still require technical-unit review. Do not edit LinerForge silently.

## 4. Baker Hughes source support

The two unique Baker Hughes original sources were inspected in the previous source audit:
- **BH-SYS-2016:** `Introduction to Wellbore Construction – Liner Hanger Systems` (132 PDF pages). Assembly diagrams PDF pp17–19, hanger types and family identifiers, accessory/rental tool examples.
- **BH-HYD-2020:** `Liner Hanger Calculations and Hydraulics – Theory` (99 PDF pages). Packoff/ball-seat arrangements, calculations and five troubleshooting lessons PDF pp82–96.

Follow `docs/baker-hughes-document-inventory.md` for per-family source pages. **These are training guides, not full Service/Technical Units for each exact component/size/revision**. Training worked examples are not universal approved operating limits. Original PDFs are copyrighted; keep them in authorised storage and **out of GitHub**.

## 5. Import / architectural boundaries (no software imported yet)

Recommended package structure after user acceptance of this audit:

```text
skills/liner-hanger-rca/     # imported and regression-tested v1.5 investigation baseline
  SKILL.md
  references/
  schemas/
  scripts/
  tests/
providers/bh/               # BH tool taxonomy + cited qualitative rules, no manuals
core/                       # future shared evidence, BHA geometry, chronology modules
docs/                        # governance and manufacturer-specific audit
```

Names are **proposed**, not implemented. `tenant_id` and `manufacturer_id` belong in future data contracts even though tenant administration and vendor-selection UI are deferred. Proprietary documents stay **outside tracked source control**. Heavy example replay HTML/CSV/image may go to non-release `examples/` only after checking size, rights and provenance.

## 6. Open risks and acceptance gates

1. **Separate newer HTML prototypes: static evidence inspected, behaviour not yet tested.** Both personal-Library assets were retrieved and inspected as source text: `liner_hanger_v1_5_focused_well_setup.html` (477,680 bytes) and `liner_hanger_v1_5_rig_csv_import.html` (467,765 bytes). Both still identify themselves in `<title>` as `16B Casing-Running Investigation — Measured Telemetry`; source text contains BHA, directional, CSV, cementing and tally-related code/labels. These are **larger standalone HTML prototypes**, not proven modules of the v1.5 ZIP skill. No browser/runtime, calculation-accuracy, CSV import/mapping or BHA geometry tests were run on them during this audit. Do not equate keyword presence or UI controls with implemented, validated functionality. Their source rights and relationship to newer bundle ZIPs need confirmation before reuse.
2. **Skill is not yet imported** into `liner-hanger-project`; tests ran against a separately extracted ZIP.
3. **Source data provenance:** 16B is a casing run; string-depth proxy and timestamp zone not independently verified; no approved setting/job-procedure for that test case.
4. **Manufacturer authority:** full BH tool-specific technical units/approved procedures remain to be acquired and reviewed.
5. **Scope creep:** later cementing simulation, real-time rig integration, full application UI and other OEM knowledge packs remain deferred.
6. **Licensing/privacy:** evaluate example case files and per-OEM source permissions before GitHub import, even to private repositories.

## 7. Acceptance summary and next task

- **Validated:** v1.5 archive exists; test suite currently passes (14/14); basic scripts, references, schema and example replay are present; LinerForge contains an extensive but partly inferred BH tool catalogue.
- **Not validated:** tool-specific BH failure diagnostics; guessed geometry, ratings or simulation thresholds; true liner-top position calculations; tenant isolation; a complete end-to-end BH case.
- **Next operational step:** `LH-002` — perform a controlled, minimal-source skill import (preserve current tests), then repeat the 14 tests **on the user's local machine**. But first finalise the outstanding prototype/source-rights screening, and agree what non-proprietary example assets can enter GitHub. No application UI work yet.

**Current LH-001:** initial audit done, full acceptance pending the open gaps above. Avoid checking it complete before local/prototype review.
