# LH-017 — Bulk engineering validation plan (five retrospective investigation tracks)

**Plan date:** 2026-11-12  
**Scope:** One coordinated bulk implementation, integration regression and evidence-review batch for Baker Hughes-only retrospective fault finding.  
**Approval status:** Proposed plan, not evidence of engineering acceptance. Existing independent baseline: **152 tests passed in 7.21 s** on Windows.  
**Release boundaries:** No job-package generator, operational directions, app/UI, numerical OEM actuation thresholds or automatically certified root cause.

## Why bulk

All five workstreams use one source-gated equipment/evidence contract, one chronological reconstruction engine, one hypothesis register and one report generator. Implement the five families **in a single feature batch**, with common fixtures, validations and one regression cycle. Keep independent acceptance criteria per family because a passing cementing scenario does not validate hanger-release physics.

## Batch matrix — 15 independent synthetic case packets

| Family | Normal / adequately observed control | Anomalous but not proven | Ambiguous / missing source |
|---|---|---|---|
| Ball drop / seating / water hammer | Recorded drop and surface response in chronological context without certifying ball state | Unexpected pressure response; consider transient, seating and line effects | Unaligned pump pressure or undocumented ball/seat model; result unresolved |
| Hanger setting | Reviewed rig SPP and hookload/change sequence; no automatic state verdict | Pressure or hookload behaviour inconsistent with the documented expectation; competing mechanical and friction explanations | Unknown hanger variant, unsupported source setting criterion or missing movement measurement |
| Running-tool release | Logged release attempt with sourced response but no automatic confirmation | Unexpected surface load/pressure response; hydraulic/mechanical alternatives remain separate | Missing running-tool type/revision and inability to discriminate release vs string movement |
| Cementing | Time-linked source-specific pump rate, volumes and returns where provided | Unexpected surface pump/return pattern; do not infer cement placement | Rig SPP or rig Pump 2 presented as cement-unit telemetry; unverified flow path/rate/volume |
| Liner-top packer setting | Reported set-down and surface response; no downhole-set proof | Suspected incomplete setting with drag/packoff alternatives | Missing element/packer revision, depth reference or meaningful load-transfer evidence |

**Important:** The “normal” label means an intentionally uneventful fixture, **not confirmed tool operation**; “anomalous” means a review trigger, **not a proven mechanism**. These fixtures use fictional values and synthetic review flags, never universal Baker Hughes ratings.

## Shared synthetic evidence contract (one schema for all 15)

- Case: `case_id`, `family`, `scenario_class`, `manufacturer_id`, `tool_family/model/size/revision/configuration`, `supported_coverage` and source provenance.
- Equipment and geometry: planned-versus-as-run BHA and anchor/datum/length unknowns. Unknown means unavailable; never substitute nominal depth.
- Original inputs: separate labelled sensor sources for rig standpipe, cement-unit pressure, hookload, torque/RPM, pump rate, volumes, returns, timestamps/time zones and chronological job events. Include only sources relevant to the fixture; never invent missing channels.
- Observation status: measured/reported/calculated/interpreted/unknown, clock alignment, unit and mapping quality, original source IDs and precise row/page locators where fictional fixtures supply them.
- Mechanism questions: **at least two** explicit alternatives for each anomalous investigation, assessor-authored supporting/contradicting evidence, discrimination questions and missing evidence.
- Report: always `draft_unapproved`; `undetermined` cause and tool state, unless a separate future controlled human approval mechanism is built and independently verified.

## One implementation batch, one test suite

1. Design the shared fixture schema and define `LH017-*` case IDs for all 15. No duplicate report engine or per-family business logic.
2. Add synthetic fixture JSON records and a runner that invokes the **existing** operating-limit, timeline, hypotheses and investigation-report scripts.
3. Add the **whole 5×3 parametrised matrix** in one regression module: 15 end-to-end case tests plus cross-case/source negative controls. Verify normal cases do not assert success, anomalous cases retain two alternatives, ambiguous cases remain explicitly unresolved.
4. Export 15 Markdown/JSON reports into an excluded local output directory and produce a machine-readable validation manifest with case ID, input provenance, test result and known gaps.
5. Inspect representative reports from each of the five families **as one review package**; correct common contract defects once, rerun the entire suite. Keep acceptance and blockers per family.
6. Record actual full Windows test count and exact run result in `TODO.md`; require independent engineer review and source evidence before signing off LH-017.

## Engineering acceptance gates

**Gate A: software and provenance (can run with synthetic fixtures).** All 15 scenarios, source/time/unit/cross-OEM negative controls and deterministic report assertions pass. Source labels and unknowns are preserved; no diagnosis is certified.

**Gate B: documentary applicability (requires authorized references).** Each scenario explicitly points to correct Baker Hughes family mechanism and page-specific source, with exact tool model/size/revision and approved SU/TU/job-specific documents where quantitative claims would be made. If unavailable, mark `mechanism_described_only` or `insufficient_documentation`, and never load a numeric rule as validated.

**Gate C: engineering validation (requires competent independent review).** Review expected versus observed chronology, physically credible competing explanations, correlation/confounders, sensor provenance and falsification checks across five families; qualify accepted subset and document unsupported models.

**Gate D: release readiness.** Clean checkout, reproducible regression, report artifacts and source/rights check. Do not approve or release for operational use before gates B/C and the wider task register are accepted.

## Risks and limits

The scope is a **bulk plan** for offline investigation scenarios, not a bulk certification of five actual Baker Hughes tools or fault models. The prior course guides support generic mechanism questions only; approved model/revision ratings and authentic as-run records remain outstanding. Tool-specific programming must not be reverse-engineered from synthetic pressure readings or published without rights review.

## Verification on Windows after the future batch implementation

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

The existing verified regression is **152 passed in 7.21 seconds**. A new test count will be reported **only after** actual collection; do not guess from the scenario count.
