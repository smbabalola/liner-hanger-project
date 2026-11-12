# BHA tally backend v0.1 — manual and Excel intake

**Status:** Implementation committed for Windows regression; NOT yet engineering-validated or accepted. No graphical editor added.

The common deterministic contract is in `skills/liner-hanger-rca/scripts/bha_tally.py`. Tests are in `skills/liner-hanger-rca/tests/test_bha_tally.py`.

## What exists

- `manual_tally(basis, rows, anchor)` accepts explicitly sourced, ordered, top-to-bottom components.
- `excel_tally(path, basis=..., mapping=..., sheet_name=..., anchor=...)` reads a named worksheet from **.xlsx** with explicit column mapping. Requires `openpyxl`. The import produces a **candidate** object; it cannot overwrite an accepted tally.
- `Tally.position_m(component_id, "top"|"bottom")` returns a **measured depth in metres relative to the stated datum**, or `None` if the reference cannot be reached through known actual lengths. It does **not** calculate TVD, tool internal offsets, stretch, space-out, packer movement or pressure ratings.
- `tally_diff(existing, candidate)` reports changed/add/remove components and a changed depth anchor for explicit review.
- Separate `planned` and `as_run` basis are required. No LinerForge inferred tool lengths are used.

**Geometry convention:** Components are ordered top-to-bottom; the **top** and **bottom** of each component are boundaries, and the anchor gives a known component boundary MD (not a free-floating hole depth). Depth increases downwards. A value is available only when every length *between* its boundary and the anchor is documented. A known top boundary can therefore be reported even if the length of that component is unknown. This is nominal tally geometry, not proof of where a downhole tool actually sat.

**Source gate:** Equipment `manufacturer_id`, family, model and revision are evidence identifiers, **not** approved Baker Hughes dimensions. Tool slip/packer/seat internal offsets are not calculated until documented and independently validated. Original Excel rows and source-sheet references should be retained in a future evidence store.

## Run locally

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
py -m pip install openpyxl
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

Existing 14 tests should remain green; 12 additional contract cases are included, with Excel-dependent cases requiring `openpyxl`. **No new test result has been claimed yet.**

## Acceptance gaps

1. User to run regression on the existing Windows checkout and report failures, passes and skips.
2. Review test cases against actual as-run tally conventions, especially boundaries, datum and field mapping.
3. Require genuine source-linked component reference offsets before slip/packer/seat/shoe MD claims.
4. Improve import audit (original workbook digest, cell references, sheet selection), stronger schema/error reporting and acceptance workflow in later tasks.
5. Only after independent engineering review can a geometry calculation be described as validated for an operational configuration.

No source PDFs, confidential operator files, actual customer well measurements or manufacturer-setpoint values are included.
