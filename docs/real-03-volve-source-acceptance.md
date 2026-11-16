# REAL-03 historical-source acceptance case: Volve (candidate, not accepted)

Date: 2026-11-16. Branch: feature/real-03-04-workstation-review.
Status: **SOURCE IDENTITY HOLD — do not report a completed matched replay**.

## Source identity discrepancy requiring resolution

Open Well Data lists a telemetry extract named `F-1_C__NO_15_9-F-1_C__3-1-22-1.parquet` with a three-hour example beginning **2013-08-25 07:08**. Its description identifies raw channels `BITDEP` (bit depth, m), `HKLD_AVG` (hookload, tonne), `WOB_AVG` (WOB, tonne), `SURF_RPM` (rpm), and `PUMP` (SPP, bar). These are *source descriptions*; the source bytes and underlying row values have not yet been independently downloaded or inspected in this workstream.

The Norwegian Offshore Directorate's Volve wellbore record lists **15/9-F-1 C as entered 2014-02-21**, conflicting with an interpretation that the above 2013 telemetry is necessarily from that wellbore's operation. The source label and reported rig time may refer to a dataset namespace, earlier phase, or another mapping; **none of these explanations has been verified**. Do not join the 2013 trace with a 2014 job event log by name alone.

Sources (public):
- https://openwelldata.org/datasets/volve/
- https://factpages.sodir.no/en/field/pageview/all/3420717
- https://www.equinor.com/energy/data-sharing
- https://openwelldata.org/source/volve/ (Databricks Marketplace access and licence conditions)

## Candidate source inventory and gates

| ID | Required original | Status and action |
| --- | --- | --- |
| V-RAW | Original WITSML telemetry, export path and SHA-256 | **Missing local verified bytes**; retrieve through Equinor's authorized Databricks route; preserve original alongside any CSV derivative |
| V-META | WITSML well UID, wellbore UID, log UID, start/end UTC and channel mnemonic/unit metadata | **Not inspected**; verify against official well identity before replay |
| V-EVENT | Daily drilling report/time-based operations matching the **same UID and interval** | **Not matched**; compare event-time zone/clock source, do not infer from report date |
| V-TALLY | As-run assembly/BHA lengths, sequence, datum, and anchor | **Not verified**; schematic may be symbolic only |
| V-DEPTH | Running-string depth (not merely bit depth), units, datum, timestamp matching anchor | **Not verified**; prohibit reconstructed liner/hanger position without it |
| V-CLOCK | Independently checked timestamp basis and offset/drift evidence | **Not verified** |
| V-RIGHTS | Equinor licence/access review | **Pending original-source acquisition** |

## Strict replay acceptance sequence

1. Acquire original WITSML and associated DDR files through authorized source. Record immutable SHA-256, complete source pathname, licensing conditions, and the raw well/wellbore/log UIDs.
2. Check source UID and chronology **against official well record**. If the 2013/2014 discrepancy remains unresolved, reject this candidate or use it solely as an explicitly unpaired telemetry visualization.
3. Map each native sensor mnemonic, *as-recorded* unit, time zone/offset, null markers, sampled intervals, and device meaning (e.g., `PUMP` is a source mnemonic; confirm it actually represents standpipe pressure). Do not convert by inference.
4. Import the resulting CSV into the **existing browser app** without replacing that application. Confirm chart cursor and recorded elapsed-time playback against sampled source rows, including gaps.
5. Only connect the existing `scripts/bha_tally.py` engine to case assembly data after **as-run** components, unit, depth datum, reliable anchor and relevant running-string depth are verified. If absent, keep symbolic not-to-scale view; no physical liner-hanger position claim.
6. Reconcile DDR times with telemetry only when investigator records the source, time basis, signed correction and reviewer declaration. Retain both original and aligned times.
7. Produce and reload annotated case, alternative hypotheses, contradictory evidence and reviewer disposition; inspect every cited row/time/source in generated report.
8. Execute browser regression on Python 3.11/3.12 and a Windows interactive review. Record the exact revision/CI run and failures; keep REAL-03/04/05 open until actual source-matched acceptance.

## Baker Hughes case separation

KHRM-299510 remains the *liner-hanger-specific* candidate, not the Volve validation case. Its original SOP, well sketches, schematic and equipment drawings were previously identified, but the repository's `docs/lh017-real-case-engineering-evidence-gate.md` does **not** establish matching historical rig telemetry, as-run tally, or clock basis. Do not upload proprietary OEM documents to a public repo or substitute training limits for case-specific procedures.

## Acceptance decision (current)

- Raw public telemetry bytes verified: **NO**
- Wellbore identity/time discrepancy resolved: **NO**
- Historical source-matched depth-and-tally replay completed: **NO**
- End-to-end liner-hanger investigation reviewed: **NO**
- Gate: **OPEN / BLOCKED BY SOURCE-MATCH VERIFICATION**
