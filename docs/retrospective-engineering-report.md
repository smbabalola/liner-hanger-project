# LH-016 — Retrospective Engineering Report (draft-only v0.1)

**2026-11-12 · Implemented, Windows regression and independent engineering approval pending.**

## Scope

The reporting backend turns already structured, reviewed-as-data investigation outputs into a portable, non-approved engineering **draft**. It does not perform job-package generation, new engineering calculations, a user-interface build, source-to-fact extraction, or automatic equipment/failure diagnosis.

Files:
- `skills/liner-hanger-rca/scripts/investigation_report.py` — `compile_report()` and `render_markdown()`.
- `skills/liner-hanger-rca/tests/test_investigation_report.py` — source-linked normal/anomalous full-pipeline report checks.

## Contents

1. Equipment and BHA scope as **supplied**, preserving unknown fields rather than backfilling values.
2. Evidence register and verified chronological event order; uncertain-time report events remain unplaced.
3. Within/outside/unverifiable screening entries and the **earliest eligible screening candidate**, explicitly not the first proven operational departure.
4. Competing hypotheses with evidence for/against, context, unresolved questions and discriminating historical checks; no probability, forced ranking or inferred root cause.
5. Missing/unverified sources, unknown timestamps, unlinked evidence, limitations and investigation checks.
6. `undetermined` conclusion and `draft_unapproved` review status, with no generated engineering sign-off.

Report source IDs remain attached to individual events. If the optional `source_register` is supplied, missing source IDs trigger an error rather than fabricated citations. Input case IDs, event IDs, evidence links and source IDs are cross-checked before compiling. The Markdown view exposes the provenance and limitations in readable format; JSON remains the portable structured source.

`compile_report` does not permit an incoming confirmed cause. A future, separately authorised workflow would be needed for competent-engineer review, signed findings, and controlled updates. Caller-entered reviewer fields and sourced values are NOT independently authenticated here.

## Regression and acceptance boundaries

Tests reuse both `LH003-NORMAL-SYNTH` and `LH003-ANOMALOUS-SYNTH` through the existing BHA tally, internal reference, limit screen, timeline and competing-hypothesis modules. They verify no invented normal-case success; two alternatives and contradictions in the anomaly; unknown BHA depth; rig vs cement unit provenance mismatch; time uncertainty; evidence references; rejection of unmatched sources, unsupported case associations and false sign-off claims.

Previous Windows baseline (before this addition): **112 passed** on 2026-11-12. The **new reporting tests have not yet been executed on the user's Windows checkout**; do not assume their pass.

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

## Limitations before engineering release

- No verification that a real Baker Hughes job package's OEM parameters or exact model/size/revision were authorised or correctly extracted.
- No actual raw rig CSV ingest or source-clock calibration is performed by the report generator; it consumes earlier outputs and their source declarations.
- Report does not infer actual success/failure, physical failure modes, causal chains, cement placement, downhole pressure or safety.
- Independent document rights, source traceability, service-unit reference reconciliation, model-specific technical review and controlled engineer approval remain outstanding.
- PDF export, printable presentation and graphical interfaces are **not** this task. Keep job-package generation deferred.
