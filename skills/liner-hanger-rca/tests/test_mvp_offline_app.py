"""End-to-end offline app gates, actual browser interactions; no network/data."""
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "index.html"
JS = ROOT / "app" / "app.js"


def test_offline_app_assets_and_no_network_dependencies():
    html = APP.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    assert '<script src="app.js"></script>' in html
    assert "https://" not in html and "http://" not in html
    assert 'fetch(' not in js and 'XMLHttpRequest' not in js
    for label in ("telemetryFile", "eventsFile", "rulesFile", "seek", "charts",
                  "assembly", "findings", "noteDialog", "downloadReport"):
        assert 'id="' + label + '"' in html


def browser():
    pw = pytest.importorskip("playwright.sync_api")
    chromium = shutil.which("chromium") or shutil.which("google-chrome")
    return pw, chromium


def start_page(driver, chromium):
    browser = driver.chromium.launch(
        headless=True, executable_path=chromium, args=["--no-sandbox"])
    page = browser.new_page(accept_downloads=True, viewport={"width": 1320, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(APP.as_uri())
    return browser, page, errors


def test_normal_case_full_replay_and_report():
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            assert page.locator("#charts canvas").count() >= 7
            assert page.locator("#cursorTime").inner_text().startswith("2026-11-10")
            assert "Running-depth-sourced" in page.locator("#assemblyStatus").inner_text()
            page.locator("#next").click()
            assert "sample 2/61" in page.locator("#cursorTime").inner_text()
            page.locator('[data-tab="deviations"]').click()
            assert "0 rule(s)" in page.locator("#ruleSummary").inner_text()
            assert "deviation_candidate" not in page.locator("#findings").inner_text()
            page.locator('[data-tab="report"]').click()
            report = page.locator("#reportText").input_value()
            assert "SYNTHETIC-MVP-NORMAL" in report
            assert "Root cause:** UNDETERMINED" in report
            assert "Engineering approval: NOT COMPLETED." in report
            assert "deviation_candidate" not in report
            assert not errors, errors
        finally:
            instance.close()


def test_anomaly_deviation_annotation_persistence_and_report_export():
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#anomalous").click()
            page.locator('[data-tab="deviations"]').click()
            assert "1 rule(s)" in page.locator("#ruleSummary").inner_text()
            assert page.locator("#findings article.flag").count() == 1
            assert "deviation candidate" in page.locator("#findings article.flag").inner_text()
            page.locator("#findings article.flag button").first.click()
            assert "sample 25/61" in page.locator("#cursorTime").inner_text()
            page.locator('[data-tab="notes"]').click()
            page.locator("#noteFrom").fill("23")
            page.locator("#noteTo").fill("31")
            page.locator("#rangeNote").click()
            assert page.locator("#noteDialog").is_visible()
            page.locator("#noteTitle").fill("Pressure rise during circulation")
            page.locator("#noteBody").fill("Surface signal. Check flow path and approved job log; do not infer the hanger preset.")
            page.locator("#noteSource").fill("SYNTHETIC-JOB-LOG / 24-31")
            page.locator('#noteForm button[type="submit"]').click()
            assert page.locator("#notesList article").count() == 1
            page.locator("#saveCase").click() if not page.locator("#saveCase").is_hidden() else None
            page.reload()
            page.locator("#restore").click()
            page.locator('[data-tab="notes"]').click()
            assert page.locator("#notesList article").count() == 1
            assert "Pressure rise during circulation" in page.locator("#notesList").inner_text()
            page.locator('[data-tab="report"]').click()
            report = page.locator("#reportText").input_value()
            assert "deviation_candidate" in report
            assert "Pressure rise during circulation" in report
            assert "SYNTHETIC-JOB-LOG / 24-31" in report
            with page.expect_download() as event:
                page.locator("#downloadReport").click()
            download = event.value
            assert download.suggested_filename.endswith("_investigation.md")
            assert not errors, errors
        finally:
            instance.close()


def test_import_csv_and_refuse_unverified_procedure_comparison(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            csv_path = tmp_path / "recorded.csv"
            csv_path.write_text(
                'timestamp,depth,spp,hookload\n'
                '2026-11-10T09:00:00Z,1510,120,115\n'
                '2026-11-10T09:01:00Z,1511,125,116\n',
                encoding="utf-8",
            )
            page.locator("#caseName").fill("IMPORT-TEST")
            page.locator("#telemetryFile").set_input_files(csv_path)
            assert "Imported 2 of 2" in page.locator("#status").inner_text()
            assert "No verified running-string depth" in page.locator("#diagnostics").inner_text()
            page.locator('[data-tab="replay"]').click()
            assert page.locator("#charts canvas").count() == 3
            assert "stationary schematic" in page.locator("#assemblyStatus").inner_text()
            page.locator('[data-tab="deviations"]').click()
            assert "Compliance cannot be assessed" in page.locator("#ruleSummary").inner_text()
            assert not errors, errors
        finally:
            instance.close()


def test_reject_duplicate_timestamps_and_unsupported_case_without_crash(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            invalid = tmp_path / "dup.csv"
            invalid.write_text(
                "timestamp,spp\n2026-11-10T09:00:00Z,10\n2026-11-10T09:00:00Z,15\n")
            page.locator("#telemetryFile").set_input_files(invalid)
            assert "strictly increasing" in page.locator("#status").inner_text()
            wrong = tmp_path / "bad.json"
            wrong.write_text(json.dumps({"schema": "not-supported", "rows": []}))
            page.locator("#caseFile").set_input_files(wrong)
            assert "Unsupported case JSON" in page.locator("#status").inner_text()
            assert not errors, errors
        finally:
            instance.close()


def test_chart_drag_opens_interval_annotation_modal():
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            canvas = page.locator("#charts canvas").first
            bounds = canvas.bounding_box()
            x1 = bounds["x"] + bounds["width"] * .3
            x2 = bounds["x"] + bounds["width"] * .5
            y = bounds["y"] + bounds["height"] * .45
            page.mouse.move(x1, y)
            page.mouse.down()
            page.mouse.move(x2, y, steps=8)
            page.mouse.up()
            assert page.locator("#noteDialog").is_visible()
            assert "recorded sample indices" in page.locator("#noteInterval").inner_text()
            page.locator("#noteTitle").fill("Direct chart selection")
            page.locator('#noteForm button[type="submit"]').click()
            page.locator('[data-tab="notes"]').click()
            assert page.locator("#notesList article").count() == 1
            assert not errors, errors
        finally:
            instance.close()


def test_reported_procedure_sequence_distinguishes_missing_from_out_of_order(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            page.locator('[data-tab="import"]').click()
            sequence = tmp_path / "steps.json"
            book = json.loads((ROOT / "examples" / "synthetic_procedure_demo_rules.json").read_text())
            # Do not use published/commercial rig rules for this synthetic UI sequence test.
            book = {
                "procedure": {"approved": True, "revision": "FICTIONAL-1",
                              "approval_reference": "SYNTHETIC-NOT-OEM"},
                "telemetry_clock_alignment_verified": True,
                "channel_units": {},
                "rules": [],
                "required_event_sequence": [
                    {"code": "A", "step": "Run liner", "approved": True,
                     "source_reference": "FICTIONAL/STEP-A"},
                    {"code": "B", "step": "Circulate", "approved": True,
                     "source_reference": "FICTIONAL/STEP-B"},
                    {"code": "C", "step": "Release", "approved": True,
                     "source_reference": "FICTIONAL/STEP-C"}
                ]
            }
            rules = tmp_path / "rules.json"
            rules.write_text(json.dumps(book))
            page.locator("#rulesFile").set_input_files(rules)
            events = [
                {"code": "A", "time": "2026-11-10T09:20:00Z",
                 "label": "Run liner", "source": "SYNTHETIC-LOG"},
                {"code": "B", "time": "2026-11-10T09:10:00Z",
                 "label": "Circulate", "source": "SYNTHETIC-LOG"}
            ]
            sequence.write_text(json.dumps(events))
            page.locator("#eventsFile").set_input_files(sequence)
            page.locator('[data-tab="deviations"]').click()
            displayed = page.locator("#findings").inner_text()
            assert "reported order question" in displayed
            assert "not found in supplied chronology" in displayed
            assert page.locator("#findings article.flag").count() == 1
            assert page.locator("#findings article.gap").count() == 1
            assert not errors, errors
        finally:
            instance.close()


def test_standalone_copy_and_case_json_roundtrip(tmp_path):
    """App must not rely on skill scripts, original checkout or cloud service."""
    copied = tmp_path / "standalone_liner_mvp"
    shutil.copytree(ROOT / "app", copied)
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance = driver.chromium.launch(headless=True, executable_path=chromium,
                                          args=["--no-sandbox"])
        try:
            page = instance.new_page(accept_downloads=True)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((copied / "index.html").as_uri())
            page.locator("#anomalous").click()
            with page.expect_download() as event:
                page.locator('[data-tab="import"]').click()
                page.locator("#exportCase").click()
            save_to = tmp_path / "exported_case.json"
            event.value.save_as(save_to)
            saved = json.loads(save_to.read_text(encoding="utf-8"))
            assert saved["schema"] == "liner-mvp-case-1"
            assert len(saved["rows"]) == 61
            assert saved["id"] == "SYNTHETIC-MVP-ANOMALOUS"
            page.reload()
            page.locator("#caseFile").set_input_files(save_to)
            page.locator('[data-tab="deviations"]').click()
            assert "1 rule(s)" in page.locator("#ruleSummary").inner_text()
            assert page.locator("#findings article.flag").count() == 1
            assert not errors, errors
        finally:
            instance.close()



def test_independent_source_files_have_persistent_provenance_not_embedded_binary(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            page.locator('[data-tab="import"]').click()
            pdf = tmp_path / "procedure.pdf"
            pdf.write_bytes(b"%PDF-1.4\n% synthetic fixture not a licensed manual\n")
            page.locator("#evidenceType").select_option("procedure")
            page.locator("#evidenceReference").fill("SYNTHETIC-SOP-A")
            page.locator("#evidenceFile").set_input_files(pdf)
            page.locator("#addEvidence").click()
            assert "1 source file(s) registered" in page.locator("#evidenceStatus").inner_text()
            assert "SYNTHETIC-SOP-A" in page.locator("#evidenceList").inner_text()
            assert "Original bytes not embedded" in page.locator("#evidenceList").inner_text()
            page.reload()
            page.locator("#restore").click()
            page.locator('[data-tab="import"]').click()
            assert "SYNTHETIC-SOP-A" in page.locator("#evidenceList").inner_text()
            page.locator('[data-tab="report"]').click()
            assert "SYNTHETIC-SOP-A" in page.locator("#reportText").input_value()
            page.locator('[data-tab="import"]').click()
            with page.expect_download() as downloaded:
                page.locator("#exportCase").click()
            target = tmp_path / "case.json"
            downloaded.value.save_as(target)
            case = json.loads(target.read_text())
            assert len(case["evidence"]) == 1
            entry = case["evidence"][0]
            assert entry["kind"] == "procedure"
            assert entry["original_bytes_embedded"] is False
            assert entry["sha256"] is None or len(entry["sha256"]) == 64
            assert "%PDF-" not in target.read_text()
            assert not errors, errors
        finally:
            instance.close()


def test_duplicate_evidence_id_is_rejected_without_overwriting_original(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            page.locator('[data-tab="import"]').click()
            file = tmp_path / "daily.txt"
            file.write_text("Fictional daily report", encoding="utf-8")
            page.locator("#evidenceReference").fill("LOG-1")
            page.locator("#evidenceFile").set_input_files(file)
            page.locator("#addEvidence").click()
            page.locator("#evidenceReference").fill("LOG-1")
            page.locator("#evidenceFile").set_input_files(file)
            page.locator("#addEvidence").click()
            assert "Duplicate source ID" in page.locator("#evidenceStatus").inner_text()
            assert page.locator("#evidenceList article").count() == 1
            assert not errors, errors
        finally:
            instance.close()
