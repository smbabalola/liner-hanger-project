# LH-002 controlled skill import

Source: pre-existing `liner-hanger-investigation-skill-v1.5.zip`.

Install contents of this ZIP into the **root** of `C:\dev\liner-hanger-project` (not inside a second project folder). It will create `skills/liner-hanger-rca/`. The original tool scripts, tests, references and synthetic fixture data are preserved without modification.

The large Utah FORGE 16A and 16B raw CSVs/preview are intentionally excluded from this minimal Git-tracked package. The 16B `replay.html` is retained because existing annotation tests require it. It depicts **full-length casing** and must not be used to validate Baker Hughes mechanical failure diagnostics. The 16B historical replay may carry third-party source rights; inspect those before publishing the repository.

No Baker Hughes copyrighted original PDFs are included. No engineering settings are certified. The `SKILL.md` title and historical method remain as in source v1.5. Future BH-specific functionality must be a separately reviewed extension, not a rewrite of the original baseline.

## Verify locally

```powershell
cd C:\dev\liner-hanger-project\skills\liner-hanger-rca
py -m pip install pytest
py -m pytest -q tests
```

If browser tests are skipped due to missing Playwright or Chromium, report them as skipped, not passed. To test the browser paths, install `playwright` and the browser (or use a compatible system Chromium). One playback browser test was observed to fail transiently once and pass on a repeat; investigate flakiness before considering browser coverage fully stable.

## Local import (safe)

1. Pull the current project `main` branch.
2. Extract this ZIP to the project root **after verifying** `skills/liner-hanger-rca` does not already exist.
3. Run the tests above and report the output.
4. Inspect git changes; then commit only the sanitized skill and audit files after confirming repository visibility and example-data rights.

Source-file SHA-256 values are recorded in `docs/LH-002-import-manifest.json`.
