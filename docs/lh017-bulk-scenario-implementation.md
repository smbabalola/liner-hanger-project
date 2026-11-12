# LH-017 — Five-family bulk scenario implementation

**Date:** 2026-11-12  
**Implementation status:** committed; **full Windows regression not yet run**.  
**Evidence level:** synthetic software/investigation workflow only, **not physical Baker Hughes diagnostic validation**.

## Added files

- `skills/liner-hanger-rca/tests/fixtures/lh017_bulk_synthetic_cases.json`: 15 independently identified fictional cases (five families × normal/anomalous/ambiguous).
- `skills/liner-hanger-rca/scripts/lh017_bulk_scenarios.py`: single fixture loader/validator, source-gated runner, shared timeline/hypothesis/report integration, and 15-pair exporter.
- `skills/liner-hanger-rca/tests/test_lh017_bulk_scenarios.py`: parametrised integration checks across every case and negative controls, manifest checks and family-specific assertions.
- Root `.gitignore`: excludes local `skills/liner-hanger-rca/reports/` to prevent accidentally committing generated real-well artifacts.

## Case matrix

| Family | Normal | Anomalous | Ambiguous |
|---|---|---|---|
| Ball drop / seating / water hammer | LH017-01-NORMAL-SYNTH | LH017-01-ANOMALOUS-SYNTH | LH017-01-AMBIGUOUS-SYNTH |
| Hanger setting | LH017-02-NORMAL-SYNTH | LH017-02-ANOMALOUS-SYNTH | LH017-02-AMBIGUOUS-SYNTH |
| Running-tool release | LH017-03-NORMAL-SYNTH | LH017-03-ANOMALOUS-SYNTH | LH017-03-AMBIGUOUS-SYNTH |
| Cementing | LH017-04-NORMAL-SYNTH | LH017-04-ANOMALOUS-SYNTH | LH017-04-AMBIGUOUS-SYNTH |
| Liner-top packer setting | LH017-05-NORMAL-SYNTH | LH017-05-ANOMALOUS-SYNTH | LH017-05-AMBIGUOUS-SYNTH |

**Normal:** A fictional, dated surface observation plus an imprecisely dated job note. No induced failure hypothesis and no assertion of successful operation.

**Anomalous:** A fictional, timestamped surface observation, a same-time but unverified assessor interpretation and an approximate job note. Two explicit mechanism questions with competing interpretation links and historical discriminating checks; no verified cause or tool-state verdict.

**Ambiguous:** A surface source whose channel/clock identity is not adequately established. The evidence remains unplaced and unresolved; two hypotheses remain questions, not ranked mechanisms.

The generated reports deliberately have **no approved numeric OEM screening rules**, no derived downhole forces/pressures, no true job trajectory, and no verified ball/hanger/running-tool/packer state. These cases test cross-family *evidence handling* only. They do **not** claim to verify model-specific mechanical signatures; that still needs approved OEM documents and independently checked references. All source names are synthetic.

## Shared gate and export

The runner rejects missing case-matrix coverage, duplicate IDs, non-BH manufacturer, false documentation status, invented reviewed exact models, and unrecognised synthetic source identity. It uses the existing `evidence_timeline.py`, `hypothesis_review.py` and `investigation_report.py` without duplicating their logic. Every report remains `draft_unapproved`, cause `undetermined`, reviewer/signoff `not_completed`.

Generate the complete offline package from the skill root:

```powershell
py scripts/lh017_bulk_scenarios.py --output-dir reports/lh017-bulk
```

Expected: 15 Markdown files, 15 JSON files and `validation-manifest.json` (31 total). No input-source files are copied to the output folder by the runner. The manifest is a **synthetic workflow summary**, not an engineering certificate.

## Validation required

Last verified regression before this implementation: **152 passed in 7.21 seconds** on Windows. New module adds **26 parametrised/test-function cases**; anticipated 178 total, **unverified** until Windows run.

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
py scripts/lh017_bulk_scenarios.py --output-dir reports/lh017-bulk
```

After the full regression: inspect one normal, anomalous and ambiguous report **for each family**, including source timing, data gaps and competing explanations. If any fail, log the failure and correct the entire suite before closing the software phase.

## Blockers before engineering acceptance

- The underlying five BH physical workflows still lack validated model/size/revision-specific SU/TU and correct as-run tool assemblies.
- Source-page/CSV-row traceability is simulated; no historical customer data approved for distribution or independent engineer approval.
- Missing high-resolution real-world pressure, pump-rate/volume, torque/RPM, hookload and returns sequences prevent verified expected-versus-observed physical reconstruction.
- Normal fictional stage response does not confirm successful equipment function.
- Independent technical falsification of the five competing mechanism pairs is not yet complete.

**LH-017 stays open.** This is a coordinated synthetic scenario integration milestone, not a v1 release gate approval.
