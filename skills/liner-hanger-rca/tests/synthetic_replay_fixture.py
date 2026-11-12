"""Deterministic synthetic 16B-style replay used only by automated tests.

No historical rig measurements, customer data, or Baker Hughes setpoints.
The lightweight host page exercises the actual v1.5 annotation assets.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]


def synthetic_replay_html():
    start = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())
    rows = []
    for i in range(1100):
        rows.append([
            start + i * 60,  # timestamp
            1000 + i * .4, 0,  # bit-depth proxy, unused column
            110 + i % 17,      # hookload
            150 + i % 23, 0,   # rig SPP, unused column
            200 + i % 19,      # rig pump flow
            4 + i % 9,         # top-drive torque
            12 + i % 15,      # top-drive RPM
            40 + i % 10, 0,   # block height, unused column
            20 + i % 8,       # rig pump 2 strokes
        ])
    data = json.dumps({
        "headers": ["epoch", "depth", "unused", "hook", "spp", "unused",
                    "flow", "torque", "rpm", "block", "unused", "p2"],
        "meta": {"well": "SYNTHETIC-ANNOTATION-TEST", "data_file": "generated synthetic samples"},
        "rows": rows
    }, separators=(',', ':'))
    base = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Synthetic Liner Hanger Annotation Test</title><style>
body{font:14px system-ui;background:#102030;color:#f1f5f9;margin:0;padding:20px}
button,select,input{margin:4px;padding:5px}
.chart{padding:12px;min-width:640px;background:#1c3349;margin:12px 0}
.chart canvas{display:block;width:900px;max-width:100%;height:155px;background:#17283a}
.work{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:16px}
</style></head><body>
<h1>SYNTHETIC TEST ONLY — No real-world rig data</h1>
<input type="range" id="scrub" min="0" max="1099" value="0">
<select id="zoom"><option value="full">All</option><option value="60">60</option>
<option value="360">360</option></select>
<select id="speed"><option value="1">1</option><option value="120">120</option></select>
<button id="toggle">Play</button>
<div class="work"><div id="charts"><div class="chart"><canvas width="900" height="155"></canvas></div>
<div class="chart"><canvas width="900" height="155"></canvas></div></div>
<section><h3>Annotate the selected timestamp</h3>
<textarea id="noteText"></textarea><button id="save">Save</button>
<button id="export">Export</button><div id="noteList"></div></section></div>
<footer>All values are generated and have no operational meaning.</footer>
<script id="caseData" type="application/json">__DATA__</script>
<script>
(()=>{
const scrub=document.getElementById('scrub'),toggle=document.getElementById('toggle');
const speed=document.getElementById('speed');let timer=null;
toggle.addEventListener('click',()=>{
 if(timer){clearInterval(timer);timer=null;toggle.textContent='Play';return;}
 toggle.textContent='Pause';
 timer=setInterval(()=>{
   const next=Math.min(1099,Number(scrub.value)+(Number(speed.value)===120?1:1));
   scrub.value=String(next);scrub.dispatchEvent(new Event('input',{bubbles:true}));
   if(next===1099){clearInterval(timer);timer=null;toggle.textContent='Play'}
 },25);
});
})();
</script>
</body></html>'''
    base = base.replace('__DATA__', data)
    spec = importlib.util.spec_from_file_location(
        'synthetic_annotation_injector', ROOT / 'scripts' / 'add_annotation_workspace.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.install(base)
