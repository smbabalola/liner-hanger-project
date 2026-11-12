# First Release Scope — Baker Hughes Retrospective Fault Finding

**Decision date:** 2026-11-12
**Decision:** Approved by user
**Release:** Baker Hughes fault-finding skill v1 (skill-first; no UI)

## Goal

Build a reusable, auditable engineering **investigation skill** for **past** Baker Hughes liner-hanger operations. An engineer supplies tool configuration, approved job steps, rig surface measurements, chronology and available reports. The skill reconstructs the operation, identifies the first supported discrepancy, compares hypotheses with evidence, and drafts a reviewable investigation report. It **does not** automatically prove the internal mechanical root cause or issue live rig instructions.

### Five initial investigation families

These follow the source's five troubleshooting lessons, rather than invented broad categories:

| Family | What v1 investigates | Source basis |
|---|---|---|
| 1. Drop ball / water hammer | Recorded ball-drop sequence, pressure signature, possible premature seat shear; distinguish symptoms and alternatives | BH-HYD-2020, PDF p82 (course lesson p77) |
| 2. Set hanger | Reported set attempts, transferred load, hookload/drag, tag/support ambiguity, hydraulic setting sequence where applicable | BH-HYD-2020, PDF pp83–85 (lesson pp78–80) |
| 3. Release running tool | Recorded release chronology, pressure/flow/hookload/torque response as applicable, alternative explanations | BH-HYD-2020, PDF pp86–90 (lesson pp81–85) |
| 4. Cement liner | Stage chronology, source-correct pump/pressure interpretation, returns/losses, plugs/packoff observations | BH-HYD-2020, PDF pp91–94 (lesson pp86–89) |
| 5. Set liner-top packer | Transferred load, liner-top packer evidence and packoff position/unstabbing ambiguity | BH-HYD-2020, PDF pp95–96 (lesson pp90–91) |

These pages are *training context and investigation prompts*, **not** authorization to apply universal actuation pressures or remedial steps.

## Document references

- **BH-SYS-2016:** Baker Hughes *Introduction to Wellbore Construction – Liner Hanger Systems*, 132-page self-study guide. Equipment-family descriptions and assembly drawings. Refer to [Baker Hughes source inventory](baker-hughes-document-inventory.md).
- **BH-HYD-2020:** Baker Hughes *Liner Hanger Calculations and Hydraulics – Theory*, 99-page self-study guide. Hydraulics, packoffs, calculation examples and troubleshooting.
- The third supplied PDF is an **identical duplicate** of BH-HYD-2020. Its duplication is not independent corroboration.
- LinerForge's 38 templates are **inventory/assembly reference only**. Some contain guessed dimensions, pressure thresholds, and ratings; these are forbidden as verified diagnostic rules.

The BH self-study guides are copyrighted. Do not commit originals to GitHub, redistribute them, or treat them as approved field procedures. The later Service Units / Technical Units referenced within BH-SYS-2016 have not yet been independently verified for exact model/size/revision applicability.

## What is in v1

- Baker Hughes manufacturer identity with tool family, model, size/revision and running-tool, packoff, ball-seat, float and liner-top-packer configuration when available.
- Protected document/source register and a **per-tool coverage matrix**.
- Surface rig CSV input with units, timestamps, source integrity, and missing/misaligned channel checks; operating logs and job programme review.
- Shared chronological timeline and plan-versus-observed evidence.
- Clear distinction of measured/reported/calculated/inferred/unknown.
- Five investigation family workflows with alternatives, contradictions, uncertainty and missing evidence.
- Only essential deterministic calculations needed to evaluate a specific hypothesis, and only after test validation.
- One structured retrospective fault-finding report, with evidence IDs, citations, limitations, and human review.
- Successful/normal controls and anomalies for repeatable tests; no forced failure classification.
- A manufacturer-extensible **backend data contract** even though only BH source packs may be activated.

## Not in v1

- General well/job planning application, full torque-and-drag simulation, general cementing design/TOC prediction, broad hydraulics simulator, operational dashboard and replay UI, formal service ticket generation, Halliburton or other manufacturer packs, real-time diagnostic commands, live WITSML, simulated driller, OEM certification, definitive automated root-cause attribution.

Prior prototype work is preserved as a reference; none of these deferrals means the feature is permanently cancelled.

## Coverage gates

Each individual tool/assembly is rated independently:
- **Inventory only:** name or family known, not enough to apply equipment-specific logic.
- **Mechanism described:** manufacturer source identifies function and configuration but exact limits/revision missing. Safe output is a *cited, qualitative hypothesis with explicit limitations*.
- **Model-specific reviewed:** model, version/size, source-approved expected sequence and quantitative limits confirmed, with validation review; only at this level may numeric tool rules be considered.
- **Unavailable:** no legitimate source or conflicting/insufficient data; do not infer from another tool or manufacturer.

Tools not passing model-specific review are **not** silently enabled; the skill can still analyse generic surface evidence and flag what is missing.

## Definition of done for v1

1. The recovered prior investigation skill is inventoried and reused, not unnecessarily rebuilt.
2. The five workflows have source mapping and explicit evidence/uncertainty contracts.
3. A source/knowledge pack registry can reject unsupported BH tool variants and non-BH manufacturer choices.
4. At least **one normal and one anomalous** synthetic or authorized case can be processed end-to-end, with known-answer expectations and no invented facts.
5. Automated regression tests pass; unit and timestamp transformations are checked; no guessed operating limits are used.
6. The report clearly discloses unverified equipment assumptions and remains subject to competent engineer review.
7. `TODO.md` records objective acceptance evidence and the skill receives a tagged release only after the release gates are satisfied.

## Implementation discipline

Follow `START_HERE.md`, then `TODO.md`, then `AGENTS.md`. One task at a time. Do not start application UI before acceptance and explicit user approval.
