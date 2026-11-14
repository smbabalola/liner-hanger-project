# AGENTS.md — Working Rules for All Coding Assistants

## CURRENT STEERING OVERRIDE — approved 2026-11-14

**Read [STEERING.md](STEERING.md) first.** It is now the canonical current engineering objective for Codex. The user explicitly approved an integrated **planned engineering calculation → verification → optional historical fault investigation** workstream, staged as `LH-CALC` tasks in `TODO.md`. Earlier statements in this file saying **all broad calculations must be deferred**, or demanding **fault-investigation-only release before any calculation code**, are **superseded for this approved workstream only**. Do not discard retrospective safety/evidence rules or the existing tested RCA skill. UI construction and additional OEMs remain deferred.

**Authoritative read sequence now:** `STEERING.md` → `START_HERE.md` → `TODO.md` → `AGENTS.md` → `skills/liner-hanger-rca/SKILL.md` → source/tests. Start with `LH-CALC-00` in the active staging plan, not the older general v1 list. Codex may repeat the bounded build/test/commit cycle **only during its running session**; no claims of autonomous after-session execution or engineering certification. Every executable module and its interfaces must be embedded in `skills/liner-hanger-rca/`, with portable skill-only delivery.


Applies to the entire `liner-hanger-project` repository. This is an **engineering skill-first** project.

## Read-first sequence (mandatory at session start)
1. `START_HERE.md` — objectives, scope and current reality.
2. `TODO.md` — the authoritative ordered task register.
3. This file — operating rules.
4. Only then inspect current source, tests, changes and task-specific references.

Start by stating the chosen task ID, the verified existing implementation, the minimal proposed change and the tests needed. **Do not generate a fresh project plan every session.** If the task is blocked, document the blocker in TODO rather than taking unrelated work.

## One repository, one checkout

- Work only in **`smbabalola/liner-hanger-project`** and the existing **`C:\dev\liner-hanger-project`** checkout.
- Do not create another GitHub repository, clone, Git worktree or development folder to 'start fresh'.
- Use normal Git branches inside the existing checkout for feature work when appropriate; never overwrite uncommitted changes.
- Never alter `ObserveIQ`, `WellOptix`, `LinerForge`, or `linercalc-pro` as a side effect. Read-only consultation of WellOptix concepts is allowed.
- Never force-push, rewrite history, delete branches, or replace the known v1.5 annotated reference.
- Keep potentially large test datasets and proprietary documents outside Git until provenance, permissions and size are checked.

## Manufacturer-selection architecture (confirmed)

- Follow [docs/multi-manufacturer-architecture.md](docs/multi-manufacturer-architecture.md).
- **One shared engineering backend**, with source-controlled manufacturer → tool family → exact model/size → revision/configuration selection. Baker Hughes is the initial inventory target; Halliburton and others are future provider packs, not current verified support.
- Keep generic data processing independent of manufacturer. Vendor-specific rules are isolated, gated by provenance/engineering review and must never leak across manufacturers.
- Never silently fall back from an unsupported Halliburton/other tool to Baker Hughes parameters.
- **First-release functional scope is confirmed:** Baker Hughes-only **retrospective fault-finding skill**. Broad engineering simulations and other OEM packs are deferred. Read [docs/first-release-scope.md](docs/first-release-scope.md).

## Core product boundary

**Complete and validate the Baker Hughes Retrospective Fault-Finding Skill v1 first.**
During this phase, deliver:
- A portable skill package with clear instructions, references, provenance and scenario checks.
- Testable deterministic Python engineering functions, not hidden calculations inside an LLM prompt.
- Historical surface rig-data ingestion and chronological evidence-based investigation of Baker Hughes operations.
- Clear, reviewable retrospective troubleshooting reports; full field-service reports are deferred.

**Do not implement or redesign the application UI** until the BH-only fault-finding v1 gate is accepted and the user explicitly starts that workstream. Do not implement broad well planning, hydraulics, cement placement simulation or other manufacturers during v1. Existing HTML prototypes are reference artifacts, not current development targets.

## Strict task loop

1. **SELECT** — choose the first eligible pending task in `TODO.md`, obey dependencies.
2. **AUDIT** — inspect pre-existing files and behavior; distinguish implemented skill vs prototype vs unverified.
3. **PLAN SMALL** — write a short expected-output and test plan for *one task*.
4. **IMPLEMENT** — smallest change necessary; preserve previously verified capabilities.
5. **TEST** — run automated and scenario tests; examine source data, time bases, units and engineering semantics.
6. **REVIEW** — compare actual evidence to each stated acceptance criterion; run regression tests.
7. **RECORD** — document failures/blockers and test evidence; update `TODO.md` and validation register.
8. **COMMIT** — narrow commit, state task ID and outcome; then select the next task.

If tests fail or evidence is insufficient, do not tick the task. Fix, narrow the claim or mark **BLOCKED**. Do not bypass tests to meet a deadline. Do not opportunistically work on backlog features.

## Definition of a completed task

A checkbox can be set to `[x]` only if:
- All acceptance criteria are met with reproducible evidence.
- Tests and commands are recorded (and failures honestly reported).
- Inputs, units and scientific assumptions are documented.
- Prior verified behavior remains intact.
- Any engineering model result is benchmarked against a separately checked reference, where the task requires one.
- Changed files and commit SHA are recorded.

'Code compiles', 'the chart renders' and 'LLM says it looks right' are **not** sufficient engineering validation.

## Data contracts and analysis safeguards

- Treat data from surface rig sensors as *surface measurements*. Inferring downhole mechanism/state requires an explicitly labeled interpretation and supporting documentation.
- Do not request wireline or formation-evaluation logs as default/core inputs; this work chiefly uses rig surface time series and chronological job reports.
- Preserve originals, high-rate samples and source metadata; explicitly track chart aggregation.
- Account for the difference between bit-depth proxies, true liner/setting-tool position, MD/TVD, reported steps and confirmed events.
- Track time zone and alignment uncertainty; do not assign exact timestamps to loosely reported job events.
- Distinguish measured / reported / calculated / inferred / unknown and planned / actual.
- Rig pumps may have multiple channels or only aggregate flow. No fabricated per-pump traces.
- Never conflate rig `Pump 2` strokes with the cementing-unit pump without verified provenance.
- Do not equate rig SPP with cement-unit pressure if the pressure circuits are separate.
- Do not assert cement placement from pumping time alone: require flow path, capacities and appropriately sourced volumes; mark losses and gaps.
- Use source-defined OEM tool/model/revision constraints; no generic setting/release thresholds presented as approved.
- A successful operation needs a coherent positive review, not a forced anomaly or RCA report.
- Diagnosis is optional and hypothesis-led; always include alternatives, contradictory evidence and what would resolve uncertainty.

## Scope and source fidelity

- Baker Hughes 2016 *Liner Hanger Systems* and 2020 *Liner Hanger Calculations and Hydraulics - Theory* have been provided and reviewed. Their copyrights remain Baker Hughes'. **Do not commit raw PDF bytes to GitHub.**
- Cite page-level evidence in the source register. Training examples are not general approved setpoints; exact tool variant/size/revision must be verified before numerical diagnostic rules are enabled.
- Do not transfer placeholder dimensions/ratings or synthetic thresholds from the read-only LinerForge catalog into the verified BH rules.
- The user agreed to narrow **release v1**, not to abandon earlier UI and broader engineering work. Keep it archived as reference and deferred backlog.

## Confidentiality, external references, and AI

- Never commit confidential rig/operator records or non-authorised Baker Hughes/proprietary manuals; sanitized examples or approved references only.
- LLMs may organise evidence and draft clearly labelled interpretation; numeric calculations and gating rules belong in deterministic, tested functions.
- Do not provide live operational commands, pressure setpoints, barrier-verification claims or instructions to manipulate real equipment. This project is for retrospective and offline engineering decision support.
- Record source citations and version/revision for equipment-specific rules; mark unknown where unsupported.

## File ownership and change control

- `START_HERE.md`: durable mission/scope and resumption protocol; edit only for an agreed major direction change.
- `TODO.md`: task status, acceptance and blockers; updated with every accepted task.
- `AGENTS.md`: development governance; change deliberately, not casually.
- `skills/liner-hanger-engineering/`: portable skill source; no embedded UI code.
- `src/liner_hanger/`: shared, testable engineering implementation.
- `tests/`: reproducible fixtures and validations.
- `docs/asset-audit.md`: recover/import findings and source locations.
- `docs/validation-register.md`: reference problems, calculation validation and limitations.

**Next eligible work:** `LH-001` — actual asset audit. No premature claims that v1.5 UI constitutes a v1.5 engineering skill release.

## Session closing report

Every coding session should end with:
- Task ID and status (accepted, still in progress or blocked).
- Exact files changed and commit SHA.
- Tests run, pass/fail details and engineering limitations.
- Next task according to `TODO.md`.

Never claim a task is complete or that a model is validated without its recorded evidence.
