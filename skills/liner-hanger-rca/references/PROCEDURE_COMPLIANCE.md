# Procedure compliance workflow — Version 1.3

## Purpose and strict distinction

The skill checks **what an approved tool/job procedure required** against **what a rig record can prove**. Reported equipment failure, anomalous telemetry and confirmed procedural noncompliance are three separate categories. A failed hanger setting is NOT itself evidence that a procedure was breached.

## Procedure intake

1. Preserve the original file, author, identifier, revision, date, approval status and manufacturer/tool configuration. Avoid publishing restricted manuals.
2. Read the job-specific procedure, approved equipment specifications, job checklist, tool/BHA tally and relevant operating windows. Training or background PDFs are **not** automatically applicable job procedures.
3. Optionally run `scripts/extract_procedure_candidates.py <pdf> --output candidates.json`; its page-referenced lines are **unapproved review candidates**, not executable rules. Inspect images/tables in the PDF manually.
4. Map each check to a measurable surface channel, the approved unit/limit, scope (stage, date/time), tolerance, hold duration and required confirmation signal. Record whether it is observable from telemetry, narrated only in daily reports, or not observable without manual evidence.
5. An engineer validates each checklist item and confirms that the procedure version was actually in force for the job. Keep original source/page references.
6. Treat inferred operation labels and missing sensor readings as unknown, never PASS.

## Rulebook contract

Use `schemas/procedure_rulebook_template.json`. To enable numeric checks, include:

- `procedure.approved: true`, non-empty `revision`, `approval_reference` (must refer to genuine authorization; test-only values allowed **only** in explicitly labelled synthetic tests)
- `telemetry_clock_alignment_verified: true` only after time base and offset are independently checked against event logs
- `channel_units`: verified native source units for each checked channel. Torque in the Utah FORGE CSV is `ft-lbs`, and top-drive rotational speed is `rpm`. Pressure/hookload/flow/pump-stroke units are not established by the source header.
- Each rule: `{id, step, description, source_reference, approved, channel, operator, value, unit, window: {start,end}, min_duration_minutes, min_coverage}`. Operators: `<`, `<=`, `>`, `>=`, `between` (the latter also requires `upper`). Times use `YYYY-MM-DDTHH:MM:SS` **in the explicitly verified source time base**, with end exclusive.
- `channel` one of `rpm`, `torque`, `hookload`, `pressure`, `flow`, `spm`, `block`, `slips`, `pressure_peak`, `torque_peak`, `rpm_peak`. Do not compare unlike measures; medians and peaks have different evidentiary meaning.

If ANY approval, source reference, time alignment, unit consistency, valid event interval or coverage check is absent, the result is **UNVERIFIABLE** and there can be no confirmed procedural violation.

## Comparator and evidence quality

Run `python scripts/check_procedure.py --rules approved_rules.json --telemetry examples/utah_forge_16A_78_32/rig_5min.csv --output investigation_results.json`.

- `met`: the sampled values tested within a verified window did not violate the defined rule. This does **not** establish that an unmeasured manual action took place.
- `deviation`: one or more contiguous windows failed the approved numerical check. These are **apparent, machine-screened deviations**, not an autonomous compliance verdict. Inspect the raw 10-second samples, sensor health, time mapping, relevance of procedure revision and operational circumstances before expert signoff.
- `unverifiable`: insufficient/unauthorised procedure or evidence. Does not imply compliant or noncompliant.

The display's UTC-free local time strings are NOT evidence of a shared time zone. Hole depth is NOT liner shoe depth; block position is NOT running-string depth unless translated with a verified pipe-tally connection/event model. No action, pressure limit, or causal finding may be invented.

## Rule and incident learning

Store: rule source, approval, verification findings, anomalies, raw-data pointers, interpreted operation state, reviewed hypotheses, confirmed outcome and evidence gaps as separate fields. Do not let AI silently update manufacturer criteria from historical cases.

## Utah FORGE case status

**Well 16A(78)-32, 31 Dec 2020–2 Jan 2021:** real rig telemetry and a day-level reports-based assembly visualization are available. Daily reports describe an unsuccessful liner-hanger setting attempt and subsequent inspection. Exact job/OEM procedure, instrumentation units for most fields, verified time alignment to individual operational steps and running-string depth are NOT present. **Therefore the delivered case has zero provable procedural breaches; this is a limitation of evidence, not a finding of compliance.**
