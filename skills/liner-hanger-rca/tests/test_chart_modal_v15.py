"""V1.5 chart-first annotation regression tests (browser test optional)."""
from pathlib import Path
import importlib.util
import shutil
import pytest
from synthetic_replay_fixture import synthetic_replay_html

ROOT=Path(__file__).resolve().parents[1]
HTML=synthetic_replay_html()


def _injector():
    p=ROOT/'scripts/add_annotation_workspace.py'
    spec=importlib.util.spec_from_file_location('mod_annotations_v15',p)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contextual_editor_and_notebook_are_in_one_skill():
    html=HTML
    for tag in ['id="iw-modal"','id="iw-dialog"','id="iw-sidebar"','id="iw-hover"',
                'id="iw-playNotice"','id="iw-point"','id="iw-mark"','id="iw-replayAnnotations"',
                'id="iw-filter"','id="iw-export"','id="iw-report"']:
        assert html.count(tag)==1,tag
    assert html.count('id="iw-workspace"')==1
    assert html.count('id="caseData"')==1
    assert 'schema_version:\'1.5.0\'' in html
    assert _injector().install(html)==html


def _browser():
    pw=pytest.importorskip('playwright.sync_api')
    chromium=shutil.which('chromium') or shutil.which('google-chrome')
    # Use Playwright-managed Chromium when no system browser is found.
    return pw,chromium


def test_modal_chart_range_and_hover_reopen():
    pw,executable=_browser()
    with pw.sync_playwright() as driver:
        browser=driver.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
        try:
            page=browser.new_page(viewport={'width':1360,'height':850})
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            page.set_content(HTML)
            page.locator('#scrub').fill('950')
            page.locator('#zoom').select_option('60')
            page.locator('#iw-mark').click()
            canvas=page.locator('#charts .chart canvas').first
            r=canvas.bounding_box()
            a=(r['x']+r['width']*.25,r['y']+r['height']*.4)
            b=(r['x']+r['width']*.58,a[1])
            page.mouse.move(*a);page.mouse.down();page.mouse.move(*b,steps=5);page.mouse.up()
            assert page.locator('#iw-modal').is_visible()
            page.locator('#iw-title').fill('Engineering chart window')
            page.locator('#iw-notes').fill('Observed telemetry requires corroboration against the original 10-second file.')
            page.locator('#iw-save').click()
            assert page.locator('#iw-modal').is_hidden()
            page.mouse.move(r['x']+r['width']*.43,a[1]);page.wait_for_timeout(220)
            assert page.locator('#iw-hover').is_visible()
            page.mouse.click(r['x']+r['width']*.43,a[1]);assert page.locator('#iw-modal').is_visible()
            assert page.locator('#iw-title').input_value()=='Engineering chart window'
            page.locator('#iw-close').click()
            page.locator('#iw-openSidebar').click();assert page.locator('#iw-sidebar').is_visible()
            assert page.locator('#iw-list .iw-entry').count()==1
            assert not errors,errors
        finally:browser.close()


def test_playback_cue_does_not_force_a_modal():
    pw,executable=_browser()
    with pw.sync_playwright() as driver:
        browser=driver.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
        try:
            page=browser.new_page(viewport={'width':1200,'height':800})
            page.set_content(HTML)
            page.locator('#scrub').fill('140');page.locator('#iw-point').click()
            page.locator('#iw-title').fill('Check drill pipe event')
            page.locator('#iw-notes').fill('No assumption about cause or equipment capability.')
            page.locator('#iw-save').click()
            page.locator('#scrub').fill('134')
            page.locator('#speed').select_option('120');page.locator('#toggle').click()
            page.wait_for_timeout(450)
            assert page.locator('#iw-playNotice').is_visible()
            assert page.locator('#iw-modal').is_hidden()
            page.locator('#iw-pauseInspect').click()
            assert page.locator('#iw-modal').is_visible()
            assert 'Play' in page.locator('#toggle').inner_text()
        finally:browser.close()

