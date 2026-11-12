# LH-001A — Baker Hughes v1 equipment coverage and source gate

**Date:** 2026-11-12  
**Status:** Candidate shortlisting, **not engineering approval**  
**Release scope:** Retrospective fault finding for Baker Hughes liner-hanger jobs; one shared, manufacturer-extensible backend.  
**Evidence basis:** `docs/baker-hughes-document-inventory.md` (page mapping of the two user-provided originals). Reconfirm against the original PDF for each production-grade extracted rule. The copyrighted PDF bytes are deliberately not in Git.

## Support classification

- **Inventory-only:** tool/family named in the guide but no approved model-and-revision-specific operating criteria established.
- **Mechanism-described:** source explains generic function or actuation family, permitting *questions and alternate explanations*, never quantitative acceptance thresholds.
- **Model-specific-reviewed:** exact model, size, part/configuration and revision have authorized engineering documents, reviewed values, and an engineer-approved test record. **No candidate below currently qualifies.**
- **Unavailable:** insufficient source evidence or conflicting identity. Must fail closed; never silently inherit an alternative OEM or tool variant.

Training guide statements are **not** approved operational limits. `H292..` family identifiers and cited SU/TU references are document pointers, not confirmation that those additional units have been obtained.

## Initial candidate set — selected for evidence-led v1 investigation

| Equipment identity / family | Mechanism as indexed in source | Source pages (PDF, 1-indexed) | Additional model-unit reference reported by guide | Current support gate |
|---|---|---|---|---|
| Hyflo III hanger | Mechanical hanger | BH-SYS-2016 pp28–31 (family section) | H29222 / SU 4364 | Mechanism-described; no approved numerical rules |
| CMC hanger | Mechanical hanger | BH-SYS-2016 pp28–31 | H29210 / SU 4268 | Mechanism-described; no approved numerical rules |
| RCM II hanger | Mechanical hanger | BH-SYS-2016 pp28–31 | H29226 / SU 10018 | Mechanism-described; no approved numerical rules |
| FLEX-LOCK mechanical hanger | Mechanical hanger | BH-SYS-2016 pp28–31 | H29413 / TU 4669 | Mechanism-described; variant required |
| Hyflo II hanger | Hydraulic hanger | BH-SYS-2016 pp33–39 | H29233 / TU 4300 | Mechanism-described; no approved numerical rules |
| HMC hanger | Hydraulic hanger | BH-SYS-2016 pp33–39 | H29223 / SU 4269 | Mechanism-described; no approved numerical rules |
| HSR II hanger | Hydraulic hanger | BH-SYS-2016 pp33–39 | H29227 / SU 10008 | Mechanism-described; no approved numerical rules |
| FLEX-LOCK hydraulic hanger | Hydraulic hanger; **distinct from mechanical variant** | BH-SYS-2016 pp33–39 | H29410 / SU 10124 | Mechanism-described; variant required |
| ControlSET FLEX-LOCK hanger | Hydraulic hanger | BH-SYS-2016 pp33–39 | H29416 / SU 100935 | Mechanism-described; no approved numerical rules |
| SDD hanger | **Hydraulic-set** in BH source; prior LinerForge software categorization conflicts | BH-SYS-2016 p38 | H29262 / source text SU 4793 vs URL 4739_TU (unresolved) | Mechanism-described for classification only; exact unit **unavailable until reconciled** |
| ZXP family liner-top packer | Packer variants must not be collapsed | BH-SYS-2016 pp42–47 | See source page/model unit | Mechanism-described; exact ZXP/Ultra/ZXHD/ZXPN/ZXP-D variant required |
| HRD-E running tool | Running / release equipment | BH-SYS-2016 p89 | H26693 | Mechanism-described; configuration and revision required |
| 2RH running tool | Running / release equipment | BH-SYS-2016 p90 | H26523 | Mechanism-described; configuration and revision required |
| C-2 rental tool | Rental / running equipment | BH-SYS-2016 p91 | H26521 | Inventory-only until function/configuration specifically reviewed |
| RS/PBR packoff arrangements, ball seat | Sealing/seat arrangements; single/dual configurations differ | BH-HYD-2020 pp9–19; BH-SYS-2016 pp87–104 | Model/part number not established | Mechanism-described; individual part and position required |
| Landing collar, plugs, darts, floats/shoes | Cementing components, distinct from rig pump instrumentation | BH-SYS-2016 pp63–85 | Individual model/part number not established | Mechanism-described; installed part/configuration required |

**Source fidelity:** Pages above identify family sections, not a claim that each named row is wholly explained on every page of the range. Page-exact extraction remains part of review. Other known family names remain **inventory-only**, not silently supported.

## Five v1 fault-finding tracks — allowed question scope

| Track | Documentary context | May reason about | Must not assert without additional evidence |
|---|---|---|---|
| Ball drop / seating | BH-HYD-2020 p82 | Chronology, pressure response, ball/seat alternatives, water-hammer possibilities | Actual ball seated, seat sheared, or universal pressure threshold |
| Hanger setting | BH-HYD-2020 pp83–85 | Hookload and pressure evidence, string support/drag alternatives | Hanger set/unset from a single surface trace or unsourced setpoint |
| Running tool release | BH-HYD-2020 pp86–90 | Observed release sequence and hydraulic/mechanical alternatives | Internal tool release from pressure alone |
| Cementing | BH-HYD-2020 pp91–94 | Rig-vs-cementer channel provenance, stage logs, returns/volumes and gaps | Cement unit pressure inferred from rig Pump 2 or rig SPP |
| Liner-top packer | BH-HYD-2020 pp95–96 | Reported set-down load, packoff and unstabbed alternatives | Confirmed packer setting from hookload alone |

## Source-gating requirements before applying equipment-specific rules

Each future BH knowledge entry must include:

1. `manufacturer_id = baker_hughes`, unique tool **family and actuation variant**, model, nominal size and revision (unknown values remain null).
2. Physical `component_id` linked to the *as-run* BHA tally and a separate planned configuration.
3. Source ID, document title/revision and **page-exact** reference for *each individual engineering claim*; accessible original held in authorized storage.
4. Explicit engineering review status, supported operation phase, units and any required additional assumptions.
5. Calculated depth references derived only from *actual component lengths and a documented MD anchor*; missing lengths or datum means **position unavailable**. MD and TVD must never be conflated.
6. No default actuation/load/pressure ratings. Family-only references may guide evidence questions but **must not** issue an approved operating verdict.
7. Other manufacturer IDs must not fall back to Baker Hughes knowledge.

## BHA builder boundary for the later implementation

The v1 BHA needs a deterministic ordered as-run component list with independently entered lengths, orientation, joints, anchors, datum and measurement provenance. A useful initial calculation is `component_reference_MD = known_anchor_MD ± sum(actual_lengths_between_anchor_and_reference)`, **but** only after choosing top-to-bottom orientation and whether the anchor is on the string or well. Tool stretch, space-out, joints, packer/set-down movement and survey effects are unknown until supplied and verified. The same model must support full or partial unknown tally without inventing missing values.

**Do not port** the `inferredLength()`, `deriveRatingsForRole()`, `deriveBakerToolProfileOverrides()` or software-`approved` seed pack values from LinerForge as manufacturer-approved values.

## Acceptance and outstanding evidence

- **Completed here:** explicit first candidate shortlist; source-family matrix; qualitative investigation boundaries; per-entry source gate; SDD and SU/TU inconsistencies flagged.
- **Not completed:** page-exact model/revision review of each candidate, approved Technical/Service Units, verified source licensing for broader distribution, reviewed numerical criteria, engineering sign-off and validation of geometry.
- **LH-001A stays unchecked.** The next useful source request is **one known, actually run Baker Hughes configuration** (hanger + running tool + packoff/seat + packer + cementing components) with model/size/revision, as-run tally and permitted source documents. It is better to validate one full assembly than assume all catalog families are supported.


## 2026-11-12 user decision — dual BHA tally intake

**Approved:** support both **manual component-by-component entry** and **existing Excel tally import** from the outset of the BHA geometry work. This is an engineering data-intake requirement, not permission to start the deferred application UI.

Both routes must produce one common validated BHA/tally data contract and identical deterministic calculations. Preserve separate **planned** and **as-run** assemblies. An import must not silently replace an existing manually entered or previously accepted tally; review differences and explicitly accept an import before it becomes the active as-run basis.

**Manual input:** ordered components, unique component identifiers, equipment identity and actual measured length with units, attachment/reference points, source and revision metadata, known depth anchor/datum and orientation. Allow unknown/missing values without default lengths.

**Excel intake:** accept .xlsx (and optionally .xls after an explicit safe conversion decision), inspect sheets/headers, permit user mapping for component description/ID, sequence, measured length, units, measured-depth anchor and relevant references; retain original row/sheet provenance. Reject ambiguous units, missing critical data and contradictory component order until reviewed. Never treat an arbitrary Excel column as manufacturer approval.

**Validation before positions:** check duplicate sequence/identifiers, positive component lengths, segment order, unit consistency, datum, anchor direction and whether anchor is referenced to the assembly or well. Maintain clear differences between nominal tally MD, measured MD, TVD and any estimated effects of stretch or movement. No inferred manufacturer lengths or unsupported operating limits.

**Acceptance tests to implement:** equivalent manual-and-Excel fixture yields identical computed reference depths; wrong units/missing lengths/unknown anchor return explicit unavailable or review-required; planned-vs-as-run stay separate; import differences cannot silently overwrite accepted components; duplicate/invalid rows produce source-linked errors. This item belongs to future BHA data contract implementation; **not yet implemented or tested**.
