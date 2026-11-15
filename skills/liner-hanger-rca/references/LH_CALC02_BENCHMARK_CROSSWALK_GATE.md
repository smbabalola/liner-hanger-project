# LH-CALC-02 — external benchmark comparability gate (research only)

**Implemented 2026-11-15; acceptance OPEN, not a reproduced field benchmark.**

The portable standard-library-only `scripts/benchmark_crosswalk.py` rejects a numerical agreement claim if an independently published or qualified source, complete physical input/output crosswalk, movement mode, explicit unit conversion, contact law or numerical tolerance rationale is missing. It does not run or change the existing force solver. It accepts the solver's **separately computed** model scalar as a manifest input; it never fills unknown published parameters or equates distinct models automatically.

## CLI, status and evidence

From `skills/liner-hanger-rca`:

```powershell
py scripts/benchmark_crosswalk.py path/to/authorized-benchmark.json
py -m pytest -q tests/test_benchmark_crosswalk.py
py -m pytest -rs -q tests
```

- Exit **2** and `evidence_incomplete`: missing or noncomparable source/physics/numerics; this is not a failed force-physics comparison.
- Exit **1** and `numerical_disagreement`: fully declared input crosswalk with difference exceeding the explicit tolerance.
- Exit **0** and `numerical_agreement_only`: compared declared scalar values fall within declared tolerances. **Engineering acceptance remains false under every outcome**, including exit 0. The programme acceptance gate requires review of original sources, model applicability, actual errors and independent qualified sign-off.

## Schema v1

```json
{
  "schema_version": "lh-calc02-benchmark-v1",
  "source": {
    "source_type": "published_independent",
    "title": "REPLACE WITH ACTUAL TITLE",
    "public_locator": "DOI or authorized dataset locator",
    "exact_table_figure_or_dataset": "exact source output location",
    "independence_statement": "why this is independent from this model",
    "reproduction_permission": "permissions and evidence for recorded values"
  },
  "basis": {
    "survey_stations_md_inc_azi_tvd": "source location and station crosswalk",
    "survey_interpolation": "great circle or other interpolation equivalence",
    "wellbore_geometry": "hole/casing model and evidence",
    "pipe_geometry_mass_and_flood_state": "pipe outer/inner radius, mass, flooded condition",
    "fluid_density": "source fluid buoyancy data",
    "friction_basis": "axial/rotational coefficient and contact law",
    "contact_model_and_regime": "contact side, loss/transfer, stiffness applicability",
    "movement_mode": "pickup",
    "bottom_boundary_condition": "sourced bottom tension and applied torque",
    "measured_output_location": "top-of-string, sensor/reference depth",
    "unit_system": "original and converted units",
    "gravity_and_buoyancy": "source gravity and pressure/buoyancy conditions"
  },
  "comparison": {
    "observable": "top_pickup_tension_n",
    "unit": "N",
    "mode": "pickup",
    "physical_equivalence_review": "reviewed_comparable",
    "reviewer_or_basis_reference": "identified reviewer or explicit check reference",
    "reference_value": 0,
    "model_value": 0,
    "absolute_tolerance": 1,
    "relative_tolerance": 0,
    "tolerance_rationale": "why tolerance is defensible"
  }
}
```

**The numbers 0, 0 and 1 above are placeholders demonstrating the JSON shape, not a valid benchmark.** Do not run the template as an external validation claim. For rotation contact torque, use `observable=rotation_contact_torque_nm`, `mode=rotation`, `unit=N*m`. A reference in lbf or ft-lbf must first be explicitly converted to SI with a documented source and conversion calculation.

## Independent isolated test execution

37 test cases were run in a reconstructed **isolated copy of exactly these two new files**, using local Python/pytest, resulting in **37 passed** (including 12 missing physical-basis fields, 5 source-evidence omissions, malformed/nonfinite/oversized numeric values, mode/unit errors, CLI exit behaviour and no implied field acceptance). This is **not** an execution of the repository's existing 568 expected tests, nor a proof that the new files pass together with the entire skill on Windows or GitHub Actions. The full suite must be run in a genuine checkout and its actual count recorded.

## Open physical and approval gate

Candidates A–E in `LH_CALC02_EXTERNAL_BENCHMARK_REGISTER.md` remain **unreproduced**. A complete published nonzero-weight 3D inclination+azimuth force comparison (or authorized actual-well reference) is still required, with a contact-state/stiffness applicability assessment and suitably qualified human review. Do not use this script to self-certify field/OEM approval or to import proprietary Baker Hughes documents into public Git.
