# LH-016 report traceability fixes — second inspection pass

**2026-11-12 · Implementation committed; local Windows full regression and new exports pending.**

## Changes addressing uploaded-report issues

1. **Event identity and time uncertainty:** Screening event IDs now use an opaque truncated SHA-256 digest of the source identity, no longer an embedded timestamp. The input observation's raw `source_sample_time` is retained separately from its verified, chronological `timestamp`. For an unverifiable cement/rig pressure comparison, verified event time remains `null`, even if a raw CSV sample time exists. A hash ID is an identifier, not evidence validation.
2. **Numeric screens:** The timeline event includes the original observed value/unit/domain/pressure basis and configured rule bound/unit/domain/pressure basis. The report prints these as **as-reported** values and explicitly states when comparison is not authorised. It does not infer that the rule is an OEM-certified limit. In the fictional anomaly, 215 psi is screened against a fictional 200 psi upper bound; a separate rig SPP reading of 220 psi is explicitly **not comparable** with a cement discharge rule.
3. **Hypothesis interpretation:** The report now preserves the authored rationale, assessor, draft review status and source IDs for every supports/contradicts/context/unresolved link, without upgrading evidence into causal proof.
4. **Source provenance:** Screen reports retain source rule location and revision plus observed channel name. Missing observation row/location and revision are declared `not supplied`. No page, CSV row, drawing detail or authenticated review is fabricated.
5. **Chronology ties:** Same-clock events may appear in deterministic listing order, but the Markdown explicitly warns that this is not proven temporal/causal order.

## Validation

Added 4 tests in `tests/test_report_traceability_fixes.py` that regenerate both synthetic reports in a temporary directory and verify the above. Previous independently verified baseline: **133 passed in 8.92 s**. New expected count **137**, not yet independently run.

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
py scripts/export_synthetic_reports.py --output-dir reports/synthetic
```

## Engineering limitations / acceptance

- The fictional source register does not contain actual BH document page/paragraph, trusted engineering approvals or full CSV sample locators. The software records **not supplied** rather than claiming to have validated them.
- Hookload observation remains qualitative; numerical hookload change not supplied in fixture.
- Planned-vs-actual engineering reconstruction and validated BH operating procedures remain outside this report-only task.
- The model cannot independently verify author/reviewer identity, rule authenticity or real tool state.
- The two regenerated Markdown exports must be examined by the user/competent engineer before LH-016 acceptance; do not mark accepted because tests passed.
