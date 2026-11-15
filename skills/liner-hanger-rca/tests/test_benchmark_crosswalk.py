"""No synthetic or self-generated case here represents field validation."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from benchmark_crosswalk import BenchmarkError, REQUIRED_BASIS, assess_benchmark


def manifest():
    # Fictional independently sourced scenario purely for exercising the gate.
    return {
        "schema_version": "lh-calc02-benchmark-v1",
        "source": {"source_type": "published_independent", "title": "FICTIONAL SCHEMA TEST",
                   "public_locator": "fictional:unit-test", "exact_table_figure_or_dataset": "test-row",
                   "independence_statement": "written independently for test coverage",
                   "reproduction_permission": "synthetic test data only"},
        "basis": {**{key: "explicit fictional source crosswalk" for key in REQUIRED_BASIS},
                  "movement_mode": "pickup", "contact_model_and_regime": "constant-side soft string"},
        "comparison": {"observable": "top_pickup_tension_n", "unit": "N", "mode": "pickup",
                       "physical_equivalence_review": "reviewed_comparable",
                       "reviewer_or_basis_reference": "fictional test basis, not qualified review",
                       "reference_value": 10000.0, "model_value": 10001.0,
                       "absolute_tolerance": 2.0, "relative_tolerance": 0,
                       "tolerance_rationale": "synthetic acceptance boundary"},
    }


def test_numerical_agreement_never_field_approval():
    report = assess_benchmark(manifest())
    assert report["status"] == "numerical_agreement_only"
    assert report["engineering_acceptance"] is False


def test_disagreement_is_explicit():
    data = manifest()
    data["comparison"]["model_value"] = 10002.01
    assert assess_benchmark(data)["status"] == "numerical_disagreement"


@pytest.mark.parametrize("key", REQUIRED_BASIS)
def test_each_missing_physical_basis_fails_closed(key):
    data = manifest()
    del data["basis"][key]
    with pytest.raises(BenchmarkError, match="missing physical crosswalk"):
        assess_benchmark(data)


@pytest.mark.parametrize("field", ["title", "public_locator", "exact_table_figure_or_dataset",
                                  "independence_statement", "reproduction_permission"])
def test_each_missing_source_fails_closed(field):
    data = manifest()
    data["source"][field] = ""
    with pytest.raises(BenchmarkError, match="missing source evidence"):
        assess_benchmark(data)


@pytest.mark.parametrize("reference,model", [(float('nan'),1), (1,float('inf')), (True,1), (1,None)])
def test_nonfinite_or_non_numeric_fails_closed(reference, model):
    data = manifest()
    data["comparison"].update(reference_value=reference,model_value=model)
    with pytest.raises(BenchmarkError):
        assess_benchmark(data)


@pytest.mark.parametrize("override", [
    {"observable": "rig_hookload"}, {"unit": "lbf"}, {"mode": "rotation"},
    {"physical_equivalence_review": "assumed"}, {"reviewer_or_basis_reference": ""},
    {"absolute_tolerance": -1}, {"relative_tolerance": float('inf')},
    {"absolute_tolerance": 0, "relative_tolerance": 0}, {"tolerance_rationale": ""},
])
def test_invalid_comparison_fails_closed(override):
    data = manifest()
    data["comparison"].update(override)
    with pytest.raises(BenchmarkError):
        assess_benchmark(data)


def test_self_reference_rejected():
    data = manifest()
    data["source"]["independence_statement"] = "same solver"
    with pytest.raises(BenchmarkError):
        assess_benchmark(data)


def test_rotation_requires_torque_units():
    data = manifest()
    data["basis"]["movement_mode"] = "rotation"
    data["comparison"].update(observable="rotation_contact_torque_nm", mode="rotation", unit="N*m")
    assert assess_benchmark(data)["unit"] == "N*m"


def test_cli_missing_evidence_is_nonzero(tmp_path):
    file = tmp_path / "incomplete.json"
    file.write_text(json.dumps({"schema_version": "lh-calc02-benchmark-v1"}), encoding="utf-8")
    cmd = [sys.executable, str(ROOT / "scripts" / "benchmark_crosswalk.py"), str(file)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "evidence_incomplete"


def test_schema_version_required():
    data = manifest()
    data["schema_version"] = "unknown"
    with pytest.raises(BenchmarkError):
        assess_benchmark(data)


def test_huge_integer_fails_closed_without_overflow():
    data = manifest()
    data["comparison"]["model_value"] = 10**400
    with pytest.raises(BenchmarkError, match="finite float"):
        assess_benchmark(data)
