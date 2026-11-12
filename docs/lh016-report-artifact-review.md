# LH-016 — Synthetic report artifact inspection checkpoint

**2026-11-12. Status: report-export tool and artifact assertions committed; full Windows pytest run and independent engineering report review pending.**

## Two expected artifacts

Run from `skills/liner-hanger-rca`:

```powershell
py scripts/export_synthetic_reports.py --output-dir reports/synthetic
```

This writes exactly four reproducible **synthetic** files:

- `reports/synthetic/lh003-normal-synth.json`
- `reports/synthetic/lh003-normal-synth.md`
- `reports/synthetic/lh003-anomalous-synth.json`
- `reports/synthetic/lh003-anomalous-synth.md`

The script is a **development-only adapter** around existing synthetic test fixtures; it is **not** a job-package parser or production source-ingestion interface. Do not commit operator records, proprietary source documents, or real-well reports to Git.

## Engineering readability findings from generator review

1. **Previously:** evidence entries carried IDs and source IDs but omitted `time_basis` from the compiled report. **Now:** `time_basis` is retained in the JSON and shown beside the observation in Markdown. The timestamp remains absent for approximate/unknown events; reports explicitly say these appear after the verified chronology rather than in time order.
2. **Previously:** unverifiable measurements carried reason codes in JSON but the rendered Markdown did not show them. **Now:** each evidence entry with reasons prints the reasons, including why a rig standpipe channel cannot establish cement-unit discharge pressure.
3. The current report deliberately does not contain validated engineering calculations or an independently supported first physical deviation. The earliest screening candidate is **not** equated to the initiating failure.
4. The normal control has no fabricated fault mechanism. The anomalous case retains the two competing synthetic hypotheses, supporting/contradicting human-authored links, source IDs and unresolved evidence.
5. **Review deficiency still open:** the report currently prints IDs/short descriptions instead of a full evidence-locator table with page/row/channel provenance and model-specific drawing references. The test fixture has fictional source IDs only. Before real-case use, a document/evidence register with checkable source locations, revision IDs, raw sample metadata and authenticated engineering review is required.
6. **Review deficiency still open:** planned-versus-actual reconstruction and validated torque/drag/pressure/volume interpretations are not yet available. They must not be silently inferred from the existing synthetic cases. Job-package generation and UI remain deferred.

## Regression

New synthetic artifact tests: `tests/test_report_artifact_review.py`. They export the four artifacts into a pytest temporary directory (not the repository), check readable source references, uncertainty explanations, missing geometry, distinct pump domains and contradictory hypotheses.

Previously confirmed local regression **127 passed in 8.54s** after `7b2aa0d`. This change adds **6 new tests**; expected collection **133**, but actual test results remain to be verified.

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
py scripts/export_synthetic_reports.py --output-dir reports/synthetic
```

**Human review:** Inspect both Markdown files and ask whether an engineer can locate the claimed source evidence, see the conflicting interpretation, and identify why neither success nor a cause is proven. Any question requiring actual Baker Hughes specifications remains unsupported until source/revision gates are satisfied.
