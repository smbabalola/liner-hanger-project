"""Static/injection regression tests for the reusable offline annotation module."""
from pathlib import Path
import importlib.util
import subprocess
import shutil
from synthetic_replay_fixture import synthetic_replay_html

ROOT=Path(__file__).resolve().parents[1]

def _module():
    spec=importlib.util.spec_from_file_location('annotation_injector',ROOT/'scripts'/'add_annotation_workspace.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sample():
    return '''<!doctype html><html><head><style>.work{display:grid}</style></head><body><div class="work"></div><section><h3>Annotate the selected timestamp</h3><textarea id="noteText"></textarea><button id="save">Save</button><button id="export">Export</button><div id="noteList"></div></section></div><footer>Evidence</footer><script id="caseData" type="application/json">{"rows":[[1,2]],"meta":{"well":"test"}}</script><div id="charts"></div></body></html>'''


def test_install_is_self_contained_and_preserves_source():
    text=_sample();out=_module().install(text)
    assert 'id="iw-workspace"' in out
    assert 'id="iw-mark"' in out
    assert 'id="iw-detail"' in out
    assert 'id="iw-files"' in out
    assert 'id="iw-import"' in out
    assert 'id="iw-report"' in out
    assert 'id="caseData"' in out and 'id="charts"' in out
    assert 'id="iw-legacy" hidden' not in out or 'id="noteText"' in out
    assert len(out)>len(text)+25000


def test_install_is_idempotent():
    once=_module().install(_sample());twice=_module().install(once)
    assert once==twice


def test_unsupported_replay_not_silently_modified():
    try:_module().install('<html><head><style></style></head><body></body></html>')
    except ValueError as err:assert 'caseData' in str(err)
    else:assert False,'Unsupported input was incorrectly accepted'


def test_javascript_has_valid_syntax_if_node_available():
    exe=shutil.which('node')
    if not exe:return
    subprocess.run([exe,'--check',str(ROOT/'assets'/'annotation_workspace.js')],check=True)


def test_example_contains_one_self_contained_notebook():
    s=synthetic_replay_html()
    assert s.count('id="iw-workspace"')==1
    assert s.count('id="caseData"')==1
    assert s.count('id="iw-mark"')==1
    assert 'id="iw-legacy" hidden' in s
    assert 'SYNTHETIC TEST ONLY' in s
