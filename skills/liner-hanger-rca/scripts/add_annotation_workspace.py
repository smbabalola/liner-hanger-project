#!/usr/bin/env python3
"""Embed the offline v1.5 contextual annotations into a 16B-style replay.

Usage:
  python scripts/add_annotation_workspace.py --html examples/utah_forge_16B_78_32/replay.html
  python scripts/add_annotation_workspace.py --html input.html --output annotated.html

Idempotent, uses only the two reusable assets inside this same skill package.
Does not alter telemetry, event data, approved rules, or running-string kinematics.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CSS = (HERE / 'assets' / 'annotation_workspace.css').read_text(encoding='utf-8')
JS = (HERE / 'assets' / 'annotation_workspace.js').read_text(encoding='utf-8')

TOOLBAR = '''
<!-- Liner Hanger Investigation Skill v1.5: in-chart annotations -->
<div id="iw-toolbar"><button id="iw-mark" type="button" class="iw-main">Select chart range</button>
<button id="iw-point" type="button">Mark point at cursor</button>
<button id="iw-fullwindow" type="button">Mark ±5 min</button>
<button id="iw-openSidebar" type="button" aria-expanded="false" aria-controls="iw-sidebar">Annotations <span id="iw-count">0 saved</span></button>
<label class="iw-playback-toggle" for="iw-replayAnnotations"><input id="iw-replayAnnotations" type="checkbox" checked> Show annotations during playback</label>
<span class="iw-instruction" id="iw-mode">Select a range, then drag directly across a chart. Click saved highlights to edit.</span></div>
'''

WORKSPACE = '''
<!-- One annotation interface: contextual editor, collapsible sidebar, replay cues -->
<div id="iw-workspace">
 <div id="iw-modal" class="iw-overlay" hidden>
   <div class="iw-backdrop" id="iw-backdrop"></div>
   <section id="iw-dialog" class="iw-dialog" role="dialog" aria-modal="true" aria-labelledby="iw-formtitle" tabindex="-1">
    <header class="iw-dialoghead"><div><span class="iw-eyebrow">ENGINEERING EVIDENCE</span><h2>Chart annotation</h2></div><button type="button" id="iw-close" aria-label="Close annotation editor">✕</button></header>
    <div class="iw-dialogbody"><h3>Selected telemetry</h3>
  <div class="iw-chip" id="iw-selected">No time window selected</div>
  <p class="iw-meta" id="iw-evidence">Select a range on any chart above, or mark ±5 minutes around the playback cursor.</p>
  <label class="iw-field" for="iw-channel">Signal to inspect
   <select id="iw-channel"><option value="1">Bit Depth (casing position proxy)</option><option value="3" selected>Hook load (klb)</option><option value="4">Rig standpipe pressure (psi)</option><option value="6">Rig pump flow (gal/min)</option><option value="7">Top-drive torque (kft·lbf)</option><option value="8">Top-drive RPM</option><option value="9">Block height (ft)</option><option value="11">Pump 2 strokes/min</option></select>
  </label>
  <div class="iw-zoomwrap"><canvas id="iw-detail" aria-label="Zoomable detailed telemetry chart" height="180"></canvas></div>
  <div class="iw-actions"><button type="button" id="iw-zoomBack">Zoom back/reset</button><button type="button" id="iw-zoomUse">Annotate zoomed range</button><span id="iw-detailhint" class="iw-subtle">Drag across this detailed chart to zoom in further.</span></div>
  <p id="iw-rangeStats" class="iw-meta">Measurement range not selected.</p>
  <h3 id="iw-formtitle">New engineering annotation</h3>
  <div class="iw-inline"><label class="iw-field">Finding category<select id="iw-kind"><option value="observation">Measured observation</option><option value="interpretation">Engineering interpretation</option><option value="procedure_question">Procedure question (not a confirmed deviation)</option><option value="screening">Unreviewed signal-screening prompt</option><option value="data_gap">Missing / uncertain evidence</option></select></label>
  <label class="iw-field">Review status<select id="iw-statusType"><option value="open">Open / requires review</option><option value="review_requested">Review requested</option><option value="accepted">Engineer accepted</option><option value="rejected">Engineer rejected</option><option value="resolved">Resolved / documented</option></select></label></div>
  <label class="iw-field">Finding title<input id="iw-title" type="text" maxlength="180" placeholder="e.g. Hookload change while running casing"></label>
  <label class="iw-field">Engineer / reviewer name<input id="iw-author" type="text" maxlength="120" placeholder="Name or initials (optional)"></label>
  <label class="iw-field">Observation, alternatives, investigation notes<textarea id="iw-notes" placeholder="What was recorded? What might explain it? Which evidence supports or contradicts that interpretation? What would falsify it?"></textarea></label>
  <label class="iw-field">Source documents / procedure references<input id="iw-references" type="text" maxlength="600" placeholder="Daily report reference, page number, job procedure revision, equipment ID, etc."></label>
  <label class="iw-field">Attach supporting files (PDF, photos, documents, text)
   <input id="iw-files" type="file" multiple aria-label="Attach supporting evidence" accept=".pdf,.png,.jpg,.jpeg,.webp,.txt,.csv,.doc,.docx,.xlsx,.json"></label>
  <div id="iw-pendingFiles"></div>
  <div class="iw-warning">Files are held in this browser session. To preserve them, <b>Export evidence JSON</b> before closing; the browser's local draft store retains notes but not the file bytes. Maximum 6 MB per attachment, 18 MB per finding.</div>
  <div class="iw-actions"><button class="iw-main" id="iw-save" type="button">Save annotation</button><button id="iw-cancel" type="button">Clear editor</button></div>
  <div id="iw-status" class="iw-status" role="status"></div></div>
   </section>
 </div>
 <aside id="iw-sidebar" class="iw-sidebar" aria-label="Engineering annotation register" hidden>
  <header class="iw-dialoghead"><div><span class="iw-eyebrow">INVESTIGATION NOTEBOOK</span><h2>Annotations</h2></div><button type="button" id="iw-closeSidebar" aria-label="Close notebook panel">✕</button></header>
  <div class="iw-sidebody"><p class="iw-subtle">Click a saved entry to inspect or edit its marked interval. System suggestions require engineer review.</p><h3>Evidence register and exports</h3>
  <div class="iw-actions"><button id="iw-export" type="button" class="iw-main">Export evidence JSON</button><button id="iw-report" type="button">Generate printable report</button></div>
  <label class="iw-field">Import / restore an exported evidence JSON<input type="file" id="iw-import" accept=".json,application/json"></label>
  <p class="iw-subtle">The report includes all saved findings, time intervals, signal ranges, evidence references, reviewer status and attachment names. The JSON evidence bundle contains attachments where available. Nothing is sent to a server.</p>
  <div id="iw-filebrowser" class="iw-card" hidden></div>
  <label class="iw-field" for="iw-filter">Filter annotations<select id="iw-filter"><option value="all">All annotations</option><option value="observation">Measured observations</option><option value="interpretation">Engineering interpretations</option><option value="procedure_question">Procedure questions</option><option value="screening">Unreviewed prompts</option><option value="data_gap">Missing evidence</option></select></label>
  <h3>Saved engineering annotations</h3><div id="iw-list" class="iw-list"></div>
  <h3>Optional signal screening</h3>
  <p class="iw-subtle">Screen the <b>recorded 1-minute summaries</b> for unusually large adjacent-minute changes in pressure/hookload and near-zero RPM. This creates review suggestions only. It is not procedure checking or failure detection.</p>
  <button id="iw-scan" type="button">Find review candidates</button>
  <div id="iw-suggestions" class="iw-suggestions"></div></div>
 </aside>
 <div id="iw-hover" class="iw-hover" role="tooltip" hidden></div>
 <div id="iw-playNotice" class="iw-playNotice" role="status" aria-live="off" hidden><div><span class="iw-eyebrow">SAVED ANNOTATION</span><strong id="iw-playTitle"></strong><small id="iw-playMeta"></small></div><button id="iw-pauseInspect" type="button">Pause &amp; inspect</button><button id="iw-dismissNotice" type="button" aria-label="Dismiss notification">✕</button></div>
</div>
'''


def install(original: str) -> str:
    if 'id="iw-dialog"' in original and 'id="iw-workspace"' in original:
        return original  # v1.5 already installed
    if 'id="iw-workspace"' in original:
        # Upgrade earlier v1.4 HTML without stacking two notebooks/scripts.
        # Keep the source Pason data and all original replay controls unchanged.
        old = original
        original = re.sub(r'/\* Liner Hanger Investigation Skill — engineer evidence notebook \(v1\.4\) \*/.*?(?=</style>)', '', original, count=1, flags=re.S)
        original = re.sub(r'<!-- Liner Hanger Investigation Skill v1\.4: engineer annotation toolbar -->.*?(?=<div class="work">)', '', original, count=1, flags=re.S)
        original = re.sub(r'<section id="iw-workspace".*?</section>\s*(?=<footer>)', '', original, count=1, flags=re.S)
        original = re.sub(r'<script>\s*/\* Liner Hanger Investigation Skill — v1\.4, engineer-controlled evidence notebook\..*?</script>\s*(?=</body>)', '', original, count=1, flags=re.S)
        if 'id="iw-workspace"' in original or 'engineer-controlled evidence notebook' in original:
            raise ValueError('Existing annotation version could not be safely upgraded; source untouched')
        if original == old:
            raise ValueError('Unsupported annotation integration; refusing to duplicate notebook')
    if 'id="caseData"' not in original or 'id="charts"' not in original:
        raise ValueError('Expected 16B-style replay with caseData and charts; no changes written')
    if '</style>' not in original or '</body>' not in original or '<div class="work">' not in original or '<footer>' not in original:
        raise ValueError('Unsupported HTML layout; no changes written')
    # Keep the older observation handlers present for backward compatibility but
    # hide the duplicate UI; engineers should see one annotation workflow.
    original = re.sub(
        r'<h3>Annotate the selected timestamp</h3>(.*?)(?=</section></div>\s*<footer>)',
        lambda match: '<h3>Engineering annotation workspace</h3><p class="hint">Use Select chart range and drag on a curve to open an annotation form beside the chart.</p><div id="iw-legacy" hidden>' + match.group(1) + '</div>',
        original,
        count=1, flags=re.S)
    updated = original.replace('</style>',  '\n' + CSS + '\n</style>', 1)
    updated = updated.replace('<div class="work">', TOOLBAR + '<div class="work">', 1)
    updated = updated.replace('<footer>', WORKSPACE + '\n<footer>', 1)
    updated = updated.replace('</body>', '<script>\n' + JS + '\n</script>\n</body>', 1)
    return updated


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--html',required=True,type=Path)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    out=args.output or args.html
    result=install(args.html.read_text(encoding='utf-8'))
    out.write_text(result,encoding='utf-8')
    print(f'Updated offline investigation replay: {out} ({len(result):,} characters)')

if __name__=='__main__':main()
