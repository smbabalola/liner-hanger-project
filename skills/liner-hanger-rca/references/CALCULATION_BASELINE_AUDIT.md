# LH-CALC-00 — Calculation baseline, gap ledger and validation intake

**Audit date:** 2026-11-14  
**Status:** IN PROGRESS — source code inspected through repository GitHub API; Windows checkout and HEAD/test rerun remain unverified in this session.  
**Current steering:** repo-root `STEERING.md`. This reference stays **inside the transferable skill** to provide UI/application developers and future Codex sessions a durable engineering capability map.

## Observed implementation — inspectable repository source

| Existing skill asset | Confirmed capability | Still missing for engineering sign-off |
| --- | --- | --- |
| `scripts/bha_tally.py` | Explicit planned/as-run tally, top-to-bottom component ordering, source-identified length and MD anchor, nominal position calculations, manual and Excel import, missing length returns unavailable | Verified KHRM configuration/dimensions, directional survey/TVD and physical string forces |
| `scripts/equipment_specs.py` | Exact component identity fields, engineer-entered sourced specification values, non-mutating edits, reviewed internal-reference offsets and nominal MD mapping | Authenticated model/size/revision applicability, independently verified source-specific ratings and engineering review |
| `scripts/engineering_baseline.py` | Quantity comparison gated by stage, case, component, sensor domain/location, MD, unit family, pressure basis, document provenance and model version | **No physical equations implemented**; current numeric differences do not verify model correctness or approve limits |
| `scripts/operating_limit_screen.py` | Reviewed source and matching manufacturer/tool/revision/domain checks for candidate surface-data limit comparisons | Actual authorized limit records, independent authentic approval process and real telemetry evidence |
| `scripts/evidence_timeline.py` | Existing time-series/evidence chronology infrastructure | Actual verified as-run rig CSV clocks, true string depth mapping, numerical model link and independent RCA review |
| `tests/test_engineering_baseline.py` | Synthetic source/MD/pressure-basis compatibility and negative tests | Not a torque/drag, fluids or hydraulics numerical benchmark |

**Test baseline:** User independently ran `py -m pytest -rs -q tests` inside `skills/liner-hanger-rca` after pulling commit `43fe431` and reported **219 passed in 11.73 s**, no failures, on **2026-11-12**. This is a **previously observed** software regression, not a new run in this audit. The current Windows `C:\dev\liner-hanger-project` working tree, HEAD and new test run are **not accessible through the GitHub API**. GitHub source review does not substitute for local tests.

## Planned KHRM-299510 design package — not engineering evidence yet

User previously named a well sketch, 7-inch ZXPN/2RH work breakdown, 7-inch schematic workbook, tieback SOPs, signed ticket and drawings. Project-file search on 2026-11-14 found the generic `Liner Hanger Systems.pdf` and `Liner Hanger Hydraulics.pdf` training guides, **not readable copies of the named KHRM plan files**. Neither an original KHRM engineering result nor a measured well survey was extracted here. Do not infer a case-specific torque/drag, ECD, setting force or pressure from filenames. No failure has been reported for KHRM; this is a *planned job* benchmark candidate.

### Minimum engineering input and benchmark ledger

| Data family | Required fields | Current verified status | Gate when absent |
| --- | --- | --- | --- |
| Well survey | MD, inclination, azimuth, reference datum, TVD convention, survey method | **Missing / not source-reviewed** | No depth-dependent torque/drag or TVD integration |
| Wellbore sections | Hole/casing IDs, top/bottom depths, clearance/restrictions | **Missing / not source-reviewed** | No validated annular flow path or surge/swab |
| Running string and liner | Component order, lengths, OD/ID, linear weight, material/connection, fluid exposure | Software tally contract available; **actual KHRM values missing** | No real string loads or hydraulic volumes |
| Fluid | Density by stage/depth, rheology/model, circulation temperature if applicable | **Missing / not source-reviewed** | No buoyancy, hydrostatics or fluid losses for KHRM |
| Planned operation | Stages, trip speeds, pump rates, circulation path, ball/drop sequence, source revisions | **Missing / not source-reviewed** | No meaningful stage-specific predictions |
| BH equipment | Exact model, size, revision, setting areas, seat/shear/set/release criteria, authorized technical/setting instructions | Source-gated fields exist; **no approved KHRM criteria verified** | No authorized force/setting or OEM limit verdict |
| Original calculation outputs | Original engineer's pickup/slack-off/torque/pressures/volumes and exact calculation basis | **Missing / not source-reviewed** | No numerical agreement claim |
| Authentic executed data | Verified as-run configuration, rig CSV and clock/sensor mappings | **Not provided for KHRM** | No retrospective failure analysis of KHRM |

## Independent validation plan — do not substitute tests for engineering

**Geometry and statics (LH-CALC-01):** Define dimensional and sign conventions and a physical reference for cylindrical capacity `V = π(D²-d²)L/4`, hydrostatic differential `Δp = ∫ρg dz`, component weight/force balance and displacement volumes. Build independent hand-computed worked cases in SI and oilfield units; exercise vertical/zero-flow, nonphysical diameters, missing source density, missing survey and depth-basis errors. These are **target equations, not already implemented or validated models**.

**Torque and drag (LH-CALC-02):** Choose a documented friction/contact model and published or hand-checkable vertical/horizontal/constant-inclination reference cases with known normal forces. State treatment of buoyancy, wall contact, rotation, stiffness, doglegs and buckling. Require independent reviewer verification of sign directions and realistic sensitivity ranges. **No fixed 'approved' friction coefficient.**

**Circulating hydraulics (LH-CALC-03):** Validate limiting cases (zero flow → zero frictional loss, matched Reynolds number in independent smooth-pipe Newtonian reference, section-loss additivity and dimensional units), then progressively expand to non-Newtonian rheology and annuli. Ensure standpipe vs ball-seat and cement-unit pressure basis remains isolated. Do not claim full field prediction before geometry/rheology and flow path validation.

**Surge/swab (LH-CALC-04):** Benchmark clearly stated moving-pipe/annulus model against published/reference analytical limits; test movement direction, rate sensitivity and clearance; display pressure estimate and limitations, not a safe tripping rate.

**Tool hydraulics (LH-CALC-05):** Benchmark `F = Δp A_eff` using independently computed areas and explicitly named differential pressure locations. No tool-specific setting/shear/release recommendation without exact approved source.

**Release acceptance:** Each stage must record reference bibliographic/source ID or approved calculation, model version, exact assumptions, hand/reference expected values, numerical tolerances, test command/output, reviewer, acceptance scope and exclusions. Unavailable evidence yields `unavailable` or `unvalidated`, **not** synthetic approval.

## LH-CALC-00 remaining actions to close this gate

- [x] Read canonical steering/TODO and verify the latest GitHub skill source contents by API.
- [x] Audit reused BHA tally, equipment specs, baseline comparisons, limit screen and evidence timeline.
- [x] Record missing case-specific source inputs and a bounded benchmark/validation plan in the skill package.
- [ ] Confirm local Windows HEAD and clean/dirty state **without discarding user changes**.
- [ ] Rerun complete local `py -m pytest -rs -q tests` and record its actual result after pulling the audit commit.
- [ ] Extract exact KHRM source pages/cells *if authorized readable attachments become accessible*; otherwise formally label the case-specific benchmark BLOCKED and proceed only with independent public/synthetic model fixtures.
- [ ] Accept the gate after local regression and documented source-availability decision; until then it stays open.

**Progress bookkeeping:** LH-CALC-00 checkable audit actions **3/7 completed (~43%)**; full engineering programme **0 of 9 stage acceptance gates completed (0%)**. The percentages use explicit item/gate counting, not subjective confidence or a claim about how much actual physics has been completed.
