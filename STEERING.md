# STEERING — Liner Hanger Investigation MVP

**Decision:** 2026-11-15 — User-approved scope reduction to finish a usable **entire application MVP**, not all nine research/calculation stages.  
**Primary goal:** Deliver and test a locally runnable retrospective liner-hanger investigation application as soon as feasible, with **today as the target**. Do not claim it is finished until a working end-to-end demonstration passes.  
**Repository:** `smbabalola/liner-hanger-project`; existing Windows checkout `C:\dev\liner-hanger-project`.  
**Task authority:** This file and [TODO.md](TODO.md) supersede the old nine-stage calculation-first execution order. Retain prior work and engineering evidence in Git history and existing skill references.

## Single MVP outcome

A user loads **one historical or explicitly synthetic liner-hanger job** and can, in the same local application:

1. **Create/open a case** with its well/job identity, available assembly outline, procedure steps, job log, and recorded surface data.
2. **Import and map CSV surface telemetry** — timestamp, depth, standpipe pressure, hookload, torque, RPM, flow/pump rate, pumped volume and returns when present — with units, clock/source information and missing-channel warnings. Do not require all channels or wireline/formation logs.
3. **Replay the operation** with synchronized time-series charts, a basic **moving drillstring/running-tool/liner schematic** (where depth/assembly data permit) and chronological reported job events. A basic outline is acceptable when exact BHA is unknown. A visual must not imply verified downhole tool actuation.
4. **Check the approved/entered procedure** against reported steps and observable rig signals; produce a chronological list of supported deviations and *evidence gaps*. Never infer OEM limits or internal failures from a surface signal alone.
5. **Add, edit and save timestamp/range annotations** via a modal, with relevant observations revealed on inspection and preserved in the case.
6. **Review alternative explanations**, clearly distinguishing observations, reported events, calculations, hypotheses, and unverified root causes.
7. **Export a readable investigation report** with case details, timeline, deviations, evidence links, notes, missing inputs and review status.

**Release audience:** local engineering demonstration/review only, not rig control, live advisory, OEM certification or a field-approved diagnostic product.

## MVP release conditions — all required

- **One runnable local app** with real UI navigation through Import → Replay → Deviations/Notes → Report. This is **app delivery**, not merely a collection of Python scripts, UI mockups or documentation.
- **End-to-end synthetic normal case** and **end-to-end synthetic anomalous case** each work through that UI, with reliable loading, aligned replay, expected differences, saved annotations and exported reports. Normal cases must not manufacture faults.
- Invalid/missing channels, inconsistent timestamps, incomplete assemblies, unsupported configurations and missing OEM instructions produce clear **unavailable/needs review** states, not invented parameters or arbitrary alarms.
- **Automated tests and a fresh local/CI run pass** for the shipped MVP; confirm basic functionality and report generation. Record actual commands, results, commit SHA and any known limitations in TODO.
- Basic launch instructions plus a short first-use guide are included. No private BH manuals, customer packages or original rig logs are committed to the public repository.
- Output explicitly states **investigation draft — not independently engineering approved**. No field-restricted physics model or OEM limit may be portrayed as operationally validated.

If any item fails, mark the MVP **NOT COMPLETE**, fix it or report the exact blocker. Do not mark it 100% on the strength of individual solver test counts.

## Build order — shortest path to a usable app

**MVP-01 Inventory/choose:** Inspect the **existing** UI prototypes, telemetry replay, moving assembly, annotation, evidence and reporting components. Reuse working code; do not rewrite validated parts or start another disconnected prototype. Identify the smallest local runtime and single case format.

**MVP-02 Wire the app:** Link existing parsers/skill functions to the chosen application shell and provide a single open-case/import workflow.

**MVP-03 Replay + procedure review:** Synchronize telemetry, assembly view and job logs; show deviation candidates with a concrete source/time/step and explicit uncertainty.

**MVP-04 Notes + report:** Modal/range annotations, persistence and evidence-linked report export.

**MVP-05 End-to-end acceptance:** Exercise both normal/anomalous fixtures through the app, repair any release-blocking defects, verify clean launch and document limitations. Only then call **MVP complete**.

Work sequentially and in meaningful batches; use the first failing MVP gate. Keep `STEERING.md` short and `TODO.md` as a concise live checklist. Update both when scope or release status changes.

## Explicitly deferred — NOT MVP blockers

- Further LH-CALC-02 full-field 3D torque/drag qualification; LH-CALC-03 generalized Bingham/Herschel–Bulkley turbulent or transitional hydraulics, full SPP rig-equipment model and independent field approval; LH-CALC-04/05 advanced surge/swab and quantitative OEM actuation modelling; LH-CALC-06/07/08 nine-stage certification gates **beyond what the MVP actually invokes**.
- Automated root-cause certainty, new OEM support, cloud hosting, multi-tenant authentication, WITSML, live rig advisory, mobile builds, voice automation and elaborate simulations.
- Source-incomplete quantitative comparisons and private operator/OEM case validation.

**Keep existing calculators available behind clearly labelled research/unsupported interfaces, or leave them disconnected if unnecessary. Do not delete their code or tests.** The deferred `LH-CALC` stage checkboxes stay historically unaccepted; MVP success is tracked **separately** and does not confer engineering approval.

## Engineering honesty and confidentiality

Use the Baker Hughes first-release procedural focus and existing investigation skill. The initial release may inspect **ball drop/seating, hanger setting, running-tool release, cementing and liner-top packer** stages as the supplied procedure/data allow; no universal model-specific limits. Evidence is surface telemetry + chronological job logs + user-authorized programme and drilling-fluid records — **not wireline/formation-evaluation logs**. Ranges and signal types must be source-mapped; distinguish rig SPP from cement-unit/setting differential. No silent default OEM dimensions, ratings, measured pressures or failed-job diagnoses.

Preserve historical implementation and review records via Git history and skill reference files. Do not commit restricted Baker Hughes training guides, job packs, customer records, secrets or any local untracked archive. Human review is required before engineering/field use, **but a labelled demo MVP does not need imaginary operator/OEM sign-off**.

## Status and autonomy

**MVP STATUS: NOT YET VERIFIED COMPLETE.** The existing skill and partial prototypes provide reusable building blocks. No end-to-end local application acceptance is asserted by this steering change. Today's target is ambitious and depends on what already works; report blockers rather than claiming completion or continuing endless physics research.

Do not assume continuous work occurs between chat messages. If a scheduled automation operates on the repository, it must follow this **MVP-first** steering order and must not resume deferred LH-CALC research until explicitly reprioritized by the user.
