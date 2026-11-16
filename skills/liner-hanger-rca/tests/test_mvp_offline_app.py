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
            page.locator("#noteDialog").wait_for(state="visible")
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
            page.wait_for_function("document.querySelector(\'#status\').textContent.includes(\'Imported 2 of 2\')")
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
            page.wait_for_function("document.querySelector(\'#status\').textContent.includes(\'strictly increasing\')")
            assert "strictly increasing" in page.locator("#status").inner_text()
            wrong = tmp_path / "bad.json"
            wrong.write_text(json.dumps({"schema": "not-supported", "rows": []}))
            page.locator("#caseFile").set_input_files(wrong)
            page.wait_for_function("document.querySelector(\'#status\').textContent.includes(\'Unsupported case JSON\')")
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
            page.wait_for_function("document.querySelector(\'#evidenceStatus\').textContent.includes(\'1 source file(s) registered\')")
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
            page.wait_for_function("document.querySelector(\'#evidenceStatus\').textContent.includes(\'1 source file(s) registered\')")
            page.locator("#evidenceReference").fill("LOG-1")
            page.locator("#evidenceFile").set_input_files(file)
            page.locator("#addEvidence").click()
            assert "Duplicate source ID" in page.locator("#evidenceStatus").inner_text()
            assert page.locator("#evidenceList article").count() == 1
            assert not errors, errors
        finally:
            instance.close()


def test_manual_job_log_entry_preserves_unverified_clock_and_source():
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            page.locator('[data-tab="import"]').click()
            before = page.locator("#timeline button").count()
            page.locator("#eventLabel").fill("Reported ball dropped")
            page.locator("#eventSource").fill("SYNTHETIC-DAILY-LOG/P4")
            page.locator("#eventTime").fill("2026-11-10T09:25:00Z")
            page.locator("#addEvent").click()
            page.wait_for_function("document.querySelector(\'#eventStatus\').textContent.includes(\'registered\')")
            assert "registered" in page.locator("#eventStatus").inner_text()
            page.locator('[data-tab="replay"]').click()
            assert page.locator("#timeline button").count() == before + 1
            assert "Reported ball dropped" in page.locator("#timeline").inner_text()
            page.locator('[data-tab="report"]').click()
            assert "SYNTHETIC-DAILY-LOG/P4" in page.locator("#reportText").input_value()
            page.reload()
            page.locator("#restore").click()
            page.locator('[data-tab="replay"]').click()
            assert "Reported ball dropped" in page.locator("#timeline").inner_text()
            assert not errors, errors
        finally:
            instance.close()


def test_manual_event_rejects_naive_clock_and_missing_provenance():
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            page.locator('[data-tab="import"]').click()
            page.locator("#eventLabel").fill("Reported circulation")
            page.locator("#eventSource").fill("")
            page.locator("#addEvent").click()
            page.wait_for_function("document.querySelector(\'#eventStatus\').textContent.includes(\'required\')")
            assert "required" in page.locator("#eventStatus").inner_text()
            page.locator("#eventSource").fill("FICTIONAL-P2")
            page.locator("#eventTime").fill("2026-11-10T09:20:00")
            page.locator("#addEvent").click()
            page.wait_for_function("document.querySelector(\'#eventStatus\').textContent.includes(\'timezone offset\')")
            assert "timezone offset" in page.locator("#eventStatus").inner_text()
            assert not errors, errors
        finally:
            instance.close()


def test_independent_event_and_procedure_inputs_survive_later_real_csv(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            events = tmp_path / "events.json"
            events.write_text(json.dumps([
                {"time":"2026-11-10T09:01:00Z","label":"Circulation reported",
                 "source":"FICTIONAL-DAILY/P2"}
            ]))
            rules = tmp_path / "rules.json"
            rules.write_text(json.dumps({
                "procedure":{"approved":False,"revision":"DRAFT","approval_reference":"FICTIONAL"},
                "telemetry_clock_alignment_verified":False,"channel_units":{"spp":"psi"},
                "rules":[{"id":"DRAFT","step":"circulation","channel":"spp","unit":"psi",
                          "operator":"<=","value":500,"source_reference":"FICTIONAL",
                          "window":{"start":"2026-11-10T09:00:00Z","end":"2026-11-10T09:02:00Z"}}]
            }))
            telemetry = tmp_path / "surface.csv"
            telemetry.write_text(
                "timestamp,spp\n2026-11-10T09:00:00Z,100\n2026-11-10T09:01:00Z,110\n")
            page.locator("#eventsFile").set_input_files(events)
            page.wait_for_function("document.querySelector(\'#importSummary\').textContent.includes(\'1 reported events\')")
            page.locator("#rulesFile").set_input_files(rules)
            page.wait_for_function("document.querySelector(\'#status\').textContent.includes(\'Loaded 1 user-supplied procedure rules\')")
            page.locator("#telemetryFile").set_input_files(telemetry)
            page.wait_for_function("document.querySelector(\'#status\').textContent.includes(\'Imported 2 of 2\')")
            assert "Imported 2 of 2" in page.locator("#status").inner_text()
            page.locator('[data-tab="replay"]').click()
            assert "Circulation reported" in page.locator("#timeline").inner_text()
            page.locator('[data-tab="deviations"]').click()
            assert page.locator("#findings article.gap").count() >= 1
            assert "unverifiable" in page.locator("#findings").inner_text()
            assert not errors, errors
        finally:
            instance.close()


def test_demo_rules_cannot_leak_into_real_csv_case(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#anomalous").click()
            page.locator('[data-tab="import"]').click()
            telemetry = tmp_path / "real_like.csv"
            telemetry.write_text(
                "timestamp,spp\n2026-11-10T09:00:00Z,90\n2026-11-10T09:01:00Z,95\n")
            page.locator("#telemetryFile").set_input_files(telemetry)
            page.locator('[data-tab="deviations"]').click()
            assert "No job-specific procedure rulebook" in page.locator("#ruleSummary").inner_text()
            page.locator('[data-tab="import"]').click()
            page.wait_for_function("document.querySelector(\'#diagnostics\').textContent.includes(\'Fictional case identity\')")
            assert "Fictional case identity" in page.locator("#diagnostics").inner_text()
            assert not errors, errors
        finally:
            instance.close()



def test_nonstandard_rig_csv_mapping_and_units_survive_case_roundtrip(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            rig = tmp_path / "vendor_export.csv"
            rig.write_text(
                "RigDateTime,SPP Sensor 1,Surface Hook (klb),Liner Running Position\n"
                "2026-11-10T09:00:00Z,234,118,1500\n"
                "2026-11-10T09:01:00Z,240,119,1501\n",
                encoding="utf-8")
            page.locator("#telemetryFile").set_input_files(rig)
            page.locator("#telemetryMappingPanel").wait_for(state="visible")
            assert page.locator("#telemetryMappingPanel").is_visible()
            page.locator("#map-t").select_option("0")
            page.locator("#map-spp").select_option("1")
            page.locator("#unit-spp").select_option("psi")
            page.locator("#map-hookload").select_option("2")
            page.locator("#unit-hookload").select_option("klb")
            page.locator("#map-running_depth").select_option("3")
            page.locator("#unit-running_depth").select_option("m MD")
            page.locator("#applyMapping").click()
            assert page.locator("#telemetryMappingPanel").is_hidden()
            assert "Imported 2 of 2" in page.locator("#status").inner_text()
            page.locator('[data-tab="replay"]').click()
            assert page.locator("#charts canvas").count() == 3
            assert "Running-depth-sourced" in page.locator("#assemblyStatus").inner_text()
            assert "psi; original reading" in page.locator("#charts").inner_text()
            assert "klb; original reading" in page.locator("#charts").inner_text()
            page.locator('[data-tab="report"]').click()
            report = page.locator("#reportText").input_value()
            assert "SPP Sensor 1" in report
            assert "psi" in report
            page.locator('[data-tab="import"]').click()
            with page.expect_download() as download:
                page.locator("#exportCase").click()
            backup = tmp_path / "case.json"
            download.value.save_as(backup)
            parsed = json.loads(backup.read_text())
            assert parsed["telemetry_mapping"]["assignments"]["spp"]["raw_header"] == "SPP Sensor 1"
            assert parsed["channel_units"]["spp"] == "psi"
            assert parsed["rows"][0]["spp"] == 234
            assert parsed["rows"][0]["source_row"] == 2
            page.reload()
            page.locator("#caseFile").set_input_files(backup)
            page.locator('[data-tab="replay"]').click()
            assert "Running-depth-sourced" in page.locator("#assemblyStatus").inner_text()
            assert not errors, errors
        finally:
            instance.close()


def test_rig_mapping_rejects_source_column_reuse_and_timezone_free_time(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            path = tmp_path / "odd.csv"
            path.write_text("LoggedAt,Column A\n2026-11-10T09:00:00Z,100\n")
            page.locator("#telemetryFile").set_input_files(path)
            page.locator("#map-t").select_option("0")
            page.locator("#map-spp").select_option("0")
            page.locator("#applyMapping").click()
            assert "Each source column may only be mapped" in page.locator("#mappingStatus").inner_text()
            assert page.locator("#telemetryMappingPanel").is_visible()
            page.locator("#map-spp").select_option("1")
            page.locator("#applyMapping").click()
            assert page.locator("#telemetryMappingPanel").is_hidden()
            bad = tmp_path / "no-zone.csv"
            bad.write_text("DateRecorded,PressureRead\n2026-11-10T09:00:00,200\n")
            page.locator("#telemetryFile").set_input_files(bad)
            page.locator("#map-t").select_option("0")
            page.locator("#map-spp").select_option("1")
            page.locator("#applyMapping").click()
            assert "explicit timezone offset" in page.locator("#mappingStatus").inner_text()
            assert page.locator("#telemetryMappingPanel").is_visible()
            assert not errors, errors
        finally:
            instance.close()


def test_real_case_procedure_remains_unverifiable_until_units_confirmed(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            source = tmp_path / "rig.csv"
            source.write_text("timestamp,spp\n2026-11-10T09:00:00Z,110\n2026-11-10T09:01:00Z,230\n")
            page.locator("#telemetryFile").set_input_files(source)
            page.wait_for_function("document.querySelector('#status').textContent.includes('Imported 2 of 2')")
            rulebook = {
                "procedure":{"approved":True,"revision":"SYNTHETIC","approval_reference":"TEST-ONLY"},
                "telemetry_clock_alignment_verified":True,
                "channel_units":{"spp":"psi"},
                "rules":[{"id":"R-1","step":"Synthetic test","description":"Test-only",
                "channel":"spp","unit":"psi","operator":"<=","value":150,
                "approved":True,"source_reference":"FICTIONAL",
                "window":{"start":"2026-11-10T09:00:00Z","end":"2026-11-10T09:02:00Z"}}]
            }
            book = tmp_path / "rules.json"
            book.write_text(json.dumps(rulebook))
            page.locator("#rulesFile").set_input_files(book)
            page.locator('[data-tab="deviations"]').click()
            assert page.locator("#findings article.gap").count() == 1
            assert "unit not verified" in page.locator("#findings").inner_text().lower()
            assert page.locator("#findings article.flag").count() == 0
            assert not errors, errors
        finally:
            instance.close()



def test_depth_without_confirmed_unit_does_not_move_or_claim_position(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            rig = tmp_path / "incomplete_unit.csv"
            rig.write_text("timestamp,running_depth,spp\n"
                           "2026-11-10T09:00:00Z,1400,200\n"
                           "2026-11-10T09:01:00Z,1405,210\n")
            page.locator("#telemetryFile").set_input_files(rig)
            page.wait_for_function("document.querySelector('#status').textContent.includes('Imported 2 of 2')")
            page.locator('[data-tab="replay"]').click()
            assert "No confirmed running-string depth AND unit" in page.locator("#assemblyStatus").inner_text()
            assert "unknown unit" in page.locator("#charts").inner_text()
            page.locator("#next").click()
            assert "No confirmed running-string depth AND unit" in page.locator("#assemblyStatus").inner_text()
            assert not errors, errors
        finally:
            instance.close()


def test_manual_sop_source_sequence_and_report_from_browser(tmp_path):
    """A job PDF can be registered and its steps entered without editing JSON."""
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            rig = tmp_path / "source_measurements.csv"
            rig.write_text("timestamp,spp\n2026-11-10T09:00:00Z,120\n"
                           "2026-11-10T09:22:00Z,135\n")
            page.locator("#caseName").fill("PROCEDURE-REVIEW-TEST")
            page.locator("#telemetryFile").set_input_files(rig)
            page.wait_for_function("document.querySelector('#status').textContent.includes('Imported 2 of 2')")
            sop = tmp_path / "SOP.pdf"
            sop.write_bytes(b"%PDF-1.4\nSynthetic source placeholder, no BH material\n")
            page.locator("#evidenceType").select_option("procedure")
            page.locator("#evidenceReference").fill("SYNTHETIC-SOP-REV-A")
            page.locator("#evidenceFile").set_input_files(sop)
            page.locator("#addEvidence").click()
            page.wait_for_function(
                "document.querySelector('#evidenceStatus').textContent.includes('1 source file(s) registered')")
            page.locator("#procedureSource").select_option("SYNTHETIC-SOP-REV-A")
            page.locator("#procedureRevision").fill("Rev A")
            page.locator("#procedurePage").fill("P 3, Step 2")
            page.locator("#procedureCode").fill("DROP-BALL")
            page.locator("#procedureStep").fill("Record ball-drop operation")
            page.locator("#addProcedureStep").click()
            assert "1 source-linked step(s)" in page.locator("#procedureStatus").inner_text()
            assert page.locator("#procedureSteps article").count() == 1
            page.locator('[data-tab="deviations"]').click()
            assert "unverifiable" in page.locator("#findings").inner_text()
            assert "Required step not found" in page.locator("#findings").inner_text()
            page.locator('[data-tab="import"]').click()
            page.locator("#eventLabel").fill("Reported ball dropped")
            page.locator("#eventSource").fill("FICTIONAL-DAILY-LOG/P3")
            page.locator("#eventTime").fill("2026-11-10T09:22:00Z")
            page.locator("#eventCode").fill("DROP-BALL")
            page.locator("#addEvent").click()
            assert "registered" in page.locator("#eventStatus").inner_text()
            page.locator("#markProcedureReview").click()
            page.locator("#procedureApprovalChecked").check()
            page.locator("#procedureClockChecked").check()
            page.locator("#procedureReviewer").fill("Test reviewer, fictional")
            page.locator("#saveProcedureReview").click()
            page.locator('[data-tab="deviations"]').click()
            assert "reported in sequence" in page.locator("#findings").inner_text()
            page.locator('[data-tab="report"]').click()
            report = page.locator("#reportText").input_value()
            assert "SYNTHETIC-SOP-REV-A / P 3, Step 2" in report
            assert "Reported ball dropped" in report
            assert "Reviewer declaration: Test reviewer, fictional" in report
            assert "not externally authenticated" in report
            assert not errors, errors
        finally:
            instance.close()


def test_manual_sop_no_invented_limits_and_source_review_is_explicit(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            rig = tmp_path / "source_measurements.csv"
            rig.write_text("timestamp,spp\n2026-11-10T09:00:00Z,120\n"
                           "2026-11-10T09:22:00Z,135\n")
            page.locator("#caseName").fill("PROCEDURE-REVIEW-TEST")
            page.locator("#telemetryFile").set_input_files(rig)
            page.wait_for_function("document.querySelector('#status').textContent.includes('Imported 2 of 2')")
            page.locator("#procedureRevision").fill("Rev A")
            page.locator("#procedurePage").fill("P 2")
            page.locator("#procedureCode").fill("SET-01")
            page.locator("#procedureStep").fill("Apply documented setting pressure")
            page.locator("#addProcedureStep").click()
            assert "Register and select" in page.locator("#procedureStatus").inner_text()
            sop = tmp_path / "fictional.txt"
            sop.write_text("Synthetic procedure placeholder")
            page.locator("#evidenceType").select_option("procedure")
            page.locator("#evidenceReference").fill("SOP-A")
            page.locator("#evidenceFile").set_input_files(sop)
            page.locator("#addEvidence").click()
            page.wait_for_function(
                "document.querySelector('#evidenceStatus').textContent.includes('1 source file(s) registered')")
            page.locator("#procedureSource").select_option("SOP-A")
            page.locator("#procedureCheck").select_option("signal")
            page.locator("#procedureChannel").select_option("spp")
            page.locator("#procedureOperator").select_option("<=")
            page.locator("#procedureThreshold").fill("")
            page.locator("#procedureUnit").fill("psi")
            page.locator("#procedureStart").fill("2026-11-10T09:20:00Z")
            page.locator("#procedureEnd").fill("2026-11-10T09:30:00Z")
            page.locator("#addProcedureStep").click()
            assert "Documented numeric limit" in page.locator("#procedureStatus").inner_text()
            assert page.locator("#procedureSteps article").count() == 0
            page.locator("#procedureThreshold").fill("185")
            page.locator("#addProcedureStep").click()
            assert page.locator("#procedureSteps article").count() == 1
            page.locator('[data-tab="deviations"]').click()
            assert "unverifiable" in page.locator("#findings").inner_text()
            assert page.locator("#findings article.flag").count() == 0
            page.locator('[data-tab="report"]').click()
            assert "SET-01" in page.locator("#reportText").input_value()
            assert "not declared" in page.locator("#reportText").input_value()
            assert not errors, errors
        finally:
            instance.close()


def test_local_evidence_viewer_requires_original_reattachment_after_reload(tmp_path):
    """Text source preview is temporary, provenance persists without raw contents."""
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            page.locator('[data-tab="import"]').click()
            source = tmp_path / "source_report.txt"
            source.write_text("Fictional job note: pumps stopped at 10:15; confirm rig log.")
            page.locator("#evidenceType").select_option("job_report")
            page.locator("#evidenceReference").fill("FICTIONAL-RIG-LOG")
            page.locator("#evidenceFile").set_input_files(source)
            page.locator("#addEvidence").click()
            page.wait_for_function(
                "document.querySelector('#evidenceStatus').textContent.includes('1 source file(s) registered')")
            page.locator("#evidenceList button", has_text="Preview local source").click()
            page.locator("#documentViewer").wait_for(state="visible")
            assert page.locator("#documentViewer").is_visible()
            assert "pumps stopped at 10:15" in page.locator("#documentContent").inner_text()
            page.locator("#closeDocument").click()
            assert page.locator("#documentViewer").is_hidden()
            with page.expect_download() as event:
                page.locator("#exportCase").click()
            saved = tmp_path / "saved_case.json"
            event.value.save_as(saved)
            assert "pumps stopped" not in saved.read_text()
            page.reload()
            page.locator("#caseFile").set_input_files(saved)
            page.locator('[data-tab="import"]').click()
            page.wait_for_function("document.querySelector(\'#evidenceList\').textContent.includes(\'FICTIONAL-RIG-LOG\')")
            assert page.locator("#evidenceList button", has_text="Preview local source").count() == 0
            page.locator("#evidenceList input[type=file]").set_input_files(source)
            page.locator("#evidenceList button", has_text="Preview local source").wait_for()
            page.locator("#evidenceList button", has_text="Preview local source").click()
            page.locator("#documentViewer").wait_for(state="visible")
            assert "pumps stopped at 10:15" in page.locator("#documentContent").inner_text()
            assert not errors, errors
        finally:
            instance.close()


def test_evidence_reattachment_rejects_wrong_file(tmp_path):
    pw, chromium = browser()
    with pw.sync_playwright() as driver:
        instance, page, errors = start_page(driver, chromium)
        try:
            page.locator("#normal").click()
            page.locator('[data-tab="import"]').click()
            original = tmp_path / "procedure.txt"
            original.write_text("Fictional original SOP")
            page.locator("#evidenceType").select_option("procedure")
            page.locator("#evidenceReference").fill("SOP-REVIEW")
            page.locator("#evidenceFile").set_input_files(original)
            page.locator("#addEvidence").click()
            page.wait_for_function(
                "document.querySelector('#evidenceStatus').textContent.includes('1 source file(s) registered')")
            page.reload()
            page.locator("#restore").click()
            page.locator('[data-tab="import"]').click()
            wrong = tmp_path / "different.txt"
            wrong.write_text("Fictional different SOP")
            page.locator("#evidenceList input[type=file]").set_input_files(wrong)
            assert "Reattachment rejected" in page.locator("#evidenceStatus").inner_text()
            assert page.locator("#evidenceList button", has_text="Preview local source").count() == 0
            assert not errors, errors
        finally:
            instance.close()
