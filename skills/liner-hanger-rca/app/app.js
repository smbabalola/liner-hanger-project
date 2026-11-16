/* Liner Hanger Investigation MVP — browser-only, no dependencies or network. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const channels=[
  ["depth","Depth","m MD"],["running_depth","Running-string depth","m MD"],
  ["spp","Standpipe pressure","psi"],["hookload","Hookload","klb"],
  ["torque","Torque","kft-lbf"],["rpm","RPM","rpm"],
  ["flow","Rig flow","gal/min"],["volume","Pumped volume","bbl"],
  ["returns","Returns","gal/min"]];
const synonyms={
  t:["t","timestamp","time","datetime","date_time"],
  depth:["depth","bit_depth","hole_depth","measured_depth"],
  running_depth:["running_depth","string_depth","running_string_depth","liner_shoe_depth"],
  spp:["spp","standpipe_pressure","pressure","standpipe"],
  hookload:["hookload","hook_load","hook"],
  torque:["torque","top_drive_torque"],
  rpm:["rpm","top_drive_rpm"],
  flow:["flow","pump_rate","pump_flow","flow_rate"],
  volume:["volume","pumped_volume","pump_volume"],
  returns:["returns","return_flow","flow_out"]
};
const units=Object.fromEntries(channels.map(x=>[x[0],x[2]]));
const defaultCase=()=>({schema:"liner-mvp-case-1",id:"",well:"",source:"",rows:[],events:[],rules:null,notes:[],evidence:[],warnings:[],columns:[],channel_units:{},telemetry_mapping:null,event_clock:null,assembly_tallies:{planned:[],as_run:[]},assembly_anchor:null,assembly_positions:null,case_kind:"imported"});
let data=defaultCase(),idx=0,timer=null,rangeStart=null,plotCanvases=[],pendingTelemetry=null;
let viewStart=0,viewEnd=null,playStartWall=0,playStartRecorded=0;
function viewBounds(){return [Math.max(0,viewStart),Math.min(data.rows.length-1,viewEnd??data.rows.length-1)]}
function setView(a,b){if(!data.rows.length)return;viewStart=Math.max(0,Math.floor(a));viewEnd=Math.min(data.rows.length-1,Math.max(viewStart+1,Math.ceil(b)));renderCharts();renderCursor()}
function resetView(){viewStart=0;viewEnd=null;renderCharts();renderCursor()}
function timeFraction(i,start,end){const a=Date.parse(data.rows[start].t),b=Date.parse(data.rows[end].t);return b>a?(Date.parse(data.rows[i].t)-a)/(b-a):0}
function pausePlayback(){
 if(timer!==null){clearInterval(timer);timer=null}
 $("play").textContent="▶ Play";
 $("playbackClock").textContent="Paused · recorded-sample cursor";
}
function sourceIndexAtOrBefore(utcMs){
 let lo=0,hi=data.rows.length;
 while(lo<hi){const mid=Math.floor((lo+hi)/2);
  if(Date.parse(data.rows[mid].t)<=utcMs)lo=mid+1;else hi=mid}
 return Math.max(0,lo-1);
}
function playbackStep(){
 if(!data.rows.length){pausePlayback();return}
 const last=data.rows.length-1,rate=Number($("speed").value)||1;
 const elapsed=(performance.now()-playStartWall)*rate;
 const target=playStartRecorded+elapsed;
 const end=Date.parse(data.rows[last].t);
 idx=target>=end?last:sourceIndexAtOrBefore(target);
 renderCursor();
 if(target>=end){pausePlayback();$("playbackClock").textContent="End of recorded job reached"}
 else $("playbackClock").textContent="Playing "+rate+"× recorded time · holding actual sample "+(idx+1)+"/"+data.rows.length;
}
function beginPlayback(){
 if(!data.rows.length){tab("import");msg("Load a case before replay");return}
 if(timer!==null){pausePlayback();return}
 if(idx>=data.rows.length-1)idx=0;
 playStartWall=performance.now();playStartRecorded=Date.parse(data.rows[idx].t);
 $("play").textContent="Ⅱ Pause";
 timer=setInterval(playbackStep,50);
 playbackStep();
}
function visibleIndexAt(fraction,start,end){const a=Date.parse(data.rows[start].t),b=Date.parse(data.rows[end].t),target=a+Math.max(0,Math.min(1,fraction))*(b-a);let nearestIndex=start,delta=Infinity;for(let j=start;j<=end;j++){const d=Math.abs(Date.parse(data.rows[j].t)-target);if(d<delta){delta=d;nearestIndex=j}}return nearestIndex}
const attachedSourceFiles=new Map();let previewUrl=null;
const esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safe=x=>String(x??"").replace(/[^a-z0-9_.-]+/gi,"_").slice(0,80)||"case";
const number=x=>x!==""&&x!==null&&x!==undefined&&Number.isFinite(Number(x))?Number(x):null;
const stamp=x=>new Date(x).toISOString().replace(".000Z","Z");
const fmt=x=>Number.isFinite(x)?Number(x).toLocaleString(undefined,{maximumFractionDigits:2}):"unavailable";
function msg(s){$("status").textContent=s}
function filename(name,text,type="application/json"){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement("a");a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)}
function headerNorm(s){return s.trim().toLowerCase().replace(/[\s-]+/g,"_").replace(/[^a-z0-9_]/g,"")}
function csvRecords(text){
  // RFC4180-style quoted fields, commas and newlines; preserve source row count.
  text=String(text).replace(/^\uFEFF/,"");let rec=[],row=[],cell="",quoted=false;
  for(let i=0;i<text.length;i++){let ch=text[i];
    if(ch==='"'){if(quoted&&text[i+1]==='"'){cell+='"';i++}else quoted=!quoted}
    else if(ch===","&&!quoted){row.push(cell);cell=""}
    else if((ch==="\n"||ch==="\r")&&!quoted){if(ch==="\r"&&text[i+1]==="\n")i++;row.push(cell);cell="";if(row.some(x=>x!==""))rec.push(row);row=[]}
    else cell+=ch;
  }
  if(quoted)throw Error("CSV contains an unterminated quoted field");
  if(cell!==""||row.length){row.push(cell);if(row.some(x=>x!==""))rec.push(row)}
  return rec;
}
function guessMapping(rawHeaders){
 const norm=rawHeaders.map(headerNorm),mapped={};
 for(const [key,variants] of Object.entries(synonyms)){
  const indices=norm.map((x,i)=>variants.includes(x)?i:-1).filter(x=>x>=0);
  if(indices.length===1)mapped[key]=indices[0];
 }
 return mapped;
}
function mapUnitLabels(){
 const unitLabels={t:["UTC or explicit offset"],depth:["m MD","ft MD"],running_depth:["m MD","ft MD"],
  spp:["psi","bar","kPa","MPa"],hookload:["klb","kN","tonne-force"],torque:["kft-lbf","kN·m","ft-lbf","N·m"],
  rpm:["rpm"],flow:["gal/min","L/min","bbl/min","m³/min"],volume:["bbl","L","m³"],
  returns:["gal/min","L/min","bbl/min","m³/min"]};
 return unitLabels;
}
function openTelemetryMapping(text,file){
 const table=csvRecords(text);
 if(table.length<2)throw Error("CSV needs a header and at least one timestamped row");
 const headers=table[0].map(x=>x.trim()),suggested=guessMapping(headers);
 pendingTelemetry={text,name:file.name,headers};
 const root=$("mappingFields");root.replaceChildren();
 const options=mapUnitLabels();
 for(const key of Object.keys(synonyms)){
  const wrap=document.createElement("div");wrap.className="field";
  const label=document.createElement("label");label.textContent=key==="t"?"Recorded timestamp (required)":channels.find(x=>x[0]===key)?.[1]||key;
  label.htmlFor="map-"+key;
  const sel=document.createElement("select");sel.id="map-"+key;sel.dataset.mappingKey=key;
  const blank=document.createElement("option");blank.value="";blank.textContent=key==="t"?"Select recorded time column":"Not present";sel.append(blank);
  headers.forEach((name,i)=>{const op=document.createElement("option");op.value=String(i);op.textContent=name||"Column "+(i+1);sel.append(op)});
  if(suggested[key]!==undefined)sel.value=String(suggested[key]);
  wrap.append(label,sel);
  if(key!=="t"){
   const unitLabel=document.createElement("label");unitLabel.htmlFor="unit-"+key;unitLabel.textContent="Source unit (must be confirmed)";
   const u=document.createElement("select");u.id="unit-"+key;u.dataset.unitKey=key;
   const unknown=document.createElement("option");unknown.value="";unknown.textContent="Unknown / not verified";u.append(unknown);
   for(const text of options[key]||[]){const op=document.createElement("option");op.value=text;op.textContent=text;u.append(op)}
   wrap.append(unitLabel,u);
  }
  root.append(wrap);
 }
 $("mappingSource").textContent="File: "+file.name+" · "+(table.length-1)+" raw data rows; no values or columns have been changed.";
 $("mappingStatus").textContent="Confirm each column's identity and source unit before importing.";
 $("telemetryMappingPanel").hidden=false;
}
function importCSV(text,source,explicit=null,sourceUnits=null){
 const table=csvRecords(text);if(table.length<2)throw Error("CSV needs a header and at least one timestamped row");
 const rawHeaders=table[0].map(x=>x.trim()),mapping=explicit||guessMapping(rawHeaders),found=Object.keys(mapping),warnings=[];
 if(mapping.t===undefined)throw Error("CSV needs a manually selected recorded timestamp column");
 const selected=Object.values(mapping);
 if(new Set(selected).size!==selected.length)throw Error("Each source column may only be mapped to one signal");
 for(const [key,index] of Object.entries(mapping)){
  if(!Object.hasOwn(synonyms,key)||!Number.isInteger(index)||index<0||index>=rawHeaders.length)
   throw Error("Invalid mapping for "+key);
 }
 const rows=[];
 for(const [i,record] of table.slice(1).entries()){
  const raw=(record[mapping.t]||"").trim();
  if(!/(?:Z|[+-]\d{2}:\d{2})$/i.test(raw))throw Error("CSV timestamp needs an explicit timezone offset at source row "+(i+2));
  const parsed=Date.parse(raw);
  if(!Number.isFinite(parsed))throw Error("Invalid timestamp at CSV row "+(i+2));
  const sample={t:stamp(parsed),source_row:i+2};
  for(const key of found){
   if(key==="t")continue;
   const rawValue=(record[mapping[key]]??"").trim();
   const parsedValue=rawValue===""?null:number(rawValue);
   if(rawValue!==""&&parsedValue===null)warnings.push("Non-numeric "+key+" at row "+(i+2)+" excluded");
   sample[key]=parsedValue;
  }
  rows.push(sample);
 }
 for(let i=1;i<rows.length;i++)if(Date.parse(rows[i].t)<=Date.parse(rows[i-1].t))
  throw Error("CSV timestamps must be unique and strictly increasing (row "+rows[i].source_row+")");
 if(mapping.running_depth===undefined)warnings.push("No verified running-string depth; schematic movement is illustrative only");
 if(mapping.spp===undefined)warnings.push("Standpipe pressure channel unavailable");
 if(mapping.hookload===undefined)warnings.push("Hookload channel unavailable");
 if(!source)warnings.push("Telemetry source/clock provenance missing");
 const verifiedUnits={};
 for(const key of found){
  if(key==="t")continue;
  const value=sourceUnits?.[key]||"";
  if(value)verifiedUnits[key]=value;
  else warnings.push("Source unit for "+key+" is not confirmed; quantitative procedure comparisons unavailable");
 }
 data.rows=rows;data.columns=found;data.warnings=[...new Set(warnings)];
 data.channel_units=verifiedUnits;data.telemetry_mapping={
  file_name:source,source_headers:rawHeaders,assignments:Object.fromEntries(
   Object.entries(mapping).map(([key,i])=>[key,{column_index:i,raw_header:rawHeaders[i],source_unit:verifiedUnits[key]||null}])),
  timestamps_require_offset:true,raw_original_not_embedded:true,engineer_verified:false
 };
 data.source=source||data.source;
 return {records:rows.length,usable:rows.length,found};
}
function acceptImportedCSV(text,source,mapping=null,sourceUnits=null){
 pausePlayback();loadState();const wasSynthetic=data.case_kind==="synthetic",hadAnnotations=data.notes.length>0;
 const result=importCSV(text,source,mapping,sourceUnits);
 invalidateEventClock("Telemetry stream replaced");
 if(wasSynthetic){
  data.events=[];data.rules=null;data.notes=[];data.evidence=[];data.case_kind="imported";
  data.id="";data.well="";data.warnings.push("Fictional case identity, procedure, events and annotations were cleared for real telemetry.");
  toFields();
 }else if(hadAnnotations){
  data.notes=[];data.warnings.push("Prior range annotations were cleared because telemetry was replaced; restore the previous case to recover them.");
 }
 idx=0;viewStart=0;viewEnd=null;describe();renderEvidence();renderCharts();renderEvents();findings();notes();renderCursor();persist();
 msg("Imported "+result.usable+" of "+result.records+" readings; previously entered independent sources were retained. Review units and clock alignment.");
 return result;
}
function validateCase(value){
  if(!value||value.schema!=="liner-mvp-case-1"||!Array.isArray(value.rows)||!Array.isArray(value.notes)||!Array.isArray(value.events))
    throw Error("Unsupported case JSON; expected liner-mvp-case-1");
  let before=0;for(const row of value.rows){const now=Date.parse(row.t);if(!Number.isFinite(now)||now<=before)throw Error("Case timestamps missing, invalid or unsorted");before=now}
  for(const note of value.notes)if(!Number.isInteger(note.a)||!Number.isInteger(note.b)||note.a>note.b||note.a<0||note.b>=value.rows.length)throw Error("Invalid persisted annotation range");
  data={...defaultCase(),...value};
}
function persist(){try{localStorage.setItem("liner_mvp_case_v1",JSON.stringify(data));return true}catch(e){return false}}
function loadState(){data.id=$("caseName").value.trim();data.well=$("wellName").value.trim();data.source=$("sourceLabel").value.trim()}
function toFields(){$("caseName").value=data.id;$("wellName").value=data.well;$("sourceLabel").value=data.source}
function current(){return data.rows[idx]}
function clockVerified(){return data.case_kind==="synthetic"||data.event_clock?.verified===true}
function alignedEventTime(event){
 if(!clockVerified()||!event?.time||!Number.isFinite(Date.parse(event.time)))return null;
 const shift=data.case_kind==="synthetic"?0:Number(data.event_clock.offset_minutes)*60000;
 if(!Number.isFinite(shift))return null;
 return new Date(Date.parse(event.time)+shift).toISOString();
}
function renderEventClock(){
 const review=data.event_clock||{};
 $("eventClockOffset").value=Number.isFinite(Number(review.offset_minutes))?String(review.offset_minutes):"0";
 $("eventClockSource").value=review.source||"";
 $("eventClockReviewer").value=review.reviewer||"";
 $("eventClockVerified").checked=review.verified===true;
 $("eventClockStatus").textContent=review.verified===true?
  "Investigator-declared correction "+review.offset_minutes+" min; not independently authenticated.":
  "Unverified: reported event times cannot be mapped to rig telemetry.";
}
function invalidateEventClock(reason){
 if(data.case_kind==="synthetic")return;
 if(data.event_clock?.verified===true){
  data.event_clock={...data.event_clock,verified:false};
  data.warnings.push(reason+"; prior event/rig clock verification withdrawn.");
 }
}
function saveEventClock(){
 const raw=$("eventClockOffset").value.trim(),offset=Number(raw),verified=$("eventClockVerified").checked;
 const source=$("eventClockSource").value.trim(),reviewer=$("eventClockReviewer").value.trim();
 if(raw===""||!Number.isFinite(offset)||Math.abs(offset)>1440)throw Error("Enter a finite correction within ±1440 minutes.");
 if(verified&&(!source||!reviewer))throw Error("A source clock comparison reference and reviewer are required before verification.");
 data.event_clock={offset_minutes:offset,verified,source,reviewer};
 renderEventClock();renderEvents();findings();persist();
}
function timestampAt(i){return data.rows[i]?.t||"unavailable"}

function closeDocumentPreview(){
 if(previewUrl){URL.revokeObjectURL(previewUrl);previewUrl=null}
 $("documentContent").replaceChildren();$("documentViewer").hidden=true;
}
async function fileDigest(file){
 if(!globalThis.crypto?.subtle?.digest)return null;
 try{
  const buffer=await file.arrayBuffer(),digest=await crypto.subtle.digest("SHA-256",buffer);
  return Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,"0")).join("");
 }catch(e){return null}
}
async function reattachSource(item,file){
 if(!file||file.name!==item.file_name||file.size!==item.size_bytes)
  throw Error("Selected file name or size does not match this source record");
 const hash=await fileDigest(file);
 if(item.sha256&&hash!==item.sha256)
  throw Error("Source fingerprint could not be verified or does not match: attachment rejected");
 attachedSourceFiles.set(item.source_id,file);
 renderEvidence();
}
async function previewSource(item){
 const file=attachedSourceFiles.get(item.source_id);
 if(!file)throw Error("Source file is not attached in this browser session; reattach the original");
 closeDocumentPreview();
 const ext=(item.file_name.toLowerCase().split(".").pop()||"");
 const frame=$("documentContent");
 $("documentTitle").textContent=item.source_id+" · "+item.file_name;
 $("documentStatus").textContent="Local document preview only; no content extraction or approved engineering interpretation. "+
   (item.sha256?"Registered SHA-256: "+item.sha256:"Fingerprint unavailable; source content not independently authenticated.");
 if(ext==="pdf"){
  previewUrl=URL.createObjectURL(file);
  const iframe=document.createElement("iframe");iframe.title="Local PDF source";iframe.src=previewUrl;
  iframe.style.width="100%";iframe.style.height="550px";iframe.style.border="1px solid #486075";
  frame.append(iframe);
 }else if(["png","jpg","jpeg"].includes(ext)){
  previewUrl=URL.createObjectURL(file);
  const img=document.createElement("img");img.alt="Local source image";img.src=previewUrl;
  img.style.maxWidth="100%";img.style.maxHeight="650px";frame.append(img);
 }else if(["txt","csv","json"].includes(ext)){
  const pre=document.createElement("pre");pre.style.whiteSpace="pre-wrap";pre.style.overflowWrap="anywhere";
  pre.style.maxHeight="400px";pre.style.overflow="auto";
  pre.textContent=(await file.text()).slice(0,100000);
  frame.append(pre);
  if(file.size>100000)$("documentStatus").textContent+=" First 100,000 characters only; open original to review the rest.";
 }else{
  $("documentStatus").textContent="Inline preview unavailable for this file type. Open the original locally; its metadata remains registered.";
 }
 $("documentViewer").hidden=false;
}
function renderEvidence(){
 const root=$("evidenceList");root.replaceChildren();
 const items=Array.isArray(data.evidence)?data.evidence:[];
 for(const item of items){
  const card=document.createElement("article");card.className="panel";card.style.margin="8px 0";card.style.padding="10px";
  const title=document.createElement("strong");title.textContent=item.source_id+" · "+item.kind.replaceAll("_"," ");card.append(title);
  const details=document.createElement("p");details.textContent=item.file_name+" · "+item.size_bytes+" bytes · "+item.review_status+
   " · SHA-256: "+(item.sha256||"unavailable");card.append(details);
  const note=document.createElement("p");note.className="sub";note.textContent="Original bytes not embedded. Keep the source file for independent review.";card.append(note);
  const attached=attachedSourceFiles.has(item.source_id);
  if(attached){
   const view=document.createElement("button");view.type="button";view.textContent="Preview local source";
   view.onclick=()=>previewSource(item).catch(e=>{$("evidenceStatus").textContent=e.message});
   card.append(view);
  }else{
   const reattach=document.createElement("input");reattach.type="file";
   reattach.setAttribute("aria-label","Reattach original "+item.source_id);
   reattach.onchange=async()=>{
    try{await reattachSource(item,reattach.files?.[0])}
    catch(e){$("evidenceStatus").textContent="Reattachment rejected: "+e.message}
   };card.append(reattach);
  }
  const remove=document.createElement("button");remove.type="button";remove.textContent="Remove from register";
  remove.onclick=()=>{if(["planned","as_run"].some(b=>assemblyRows(b).some(x=>x.source_id===item.source_id))){$("evidenceStatus").textContent="Cannot remove "+item.source_id+" while assembly tally components reference it; remove those components first.";return}attachedSourceFiles.delete(item.source_id);data.evidence=data.evidence.filter(x=>x.source_id!==item.source_id);closeDocumentPreview();renderEvidence();describe();persist()};card.append(remove);
  root.append(card);
 }
 $("evidenceStatus").textContent=items.length+" source file(s) registered; originals must be retained separately.";
 procedureSourceOptions();
 assemblySourceOptions();
}
async function registerEvidence(file,kind,source_id,review_status){
 if(!file)throw Error("Choose a source file first");
 $("evidenceStatus").textContent="Registering source and calculating fingerprint; please wait…";
 if(!source_id||!source_id.trim())throw Error("A source ID/reference is required");
 if(!["job_report","procedure","equipment","fluids","telemetry","other"].includes(kind))throw Error("Unsupported evidence category");
 if(!["unreviewed","source_identified"].includes(review_status))throw Error("Unsupported review declaration");
 if(!Array.isArray(data.evidence))data.evidence=[];
 if(data.evidence.some(x=>x.source_id===source_id))throw Error("Duplicate source ID; use a unique evidence reference");
 const allowed=/\.(pdf|csv|txt|json|xlsx|xls|png|jpe?g|docx?|)$/i;
 if(!/\.(pdf|csv|txt|json|xlsx|xls|png|jpe?g|docx?)$/i.test(file.name))throw Error("Unsupported evidence file extension");
 const sha256=await fileDigest(file);
 data.evidence.push({source_id,kind,review_status,file_name:file.name,size_bytes:file.size,
  media_type:file.type||"unknown",last_modified_ms:file.lastModified,sha256,
  original_bytes_embedded:false,authentication:"caller_supplied_not_verified"});
 attachedSourceFiles.set(source_id,file);
 renderEvidence();describe();persist();
}

const assemblyRoleLabels={drill_pipe:"Drill pipe",running_tool:"Running tool",liner:"Liner",other:"Other / unclassified"};
function assemblySourceOptions(){
 const select=$("assemblySource"),selected=select.value;
 select.replaceChildren();
 const blank=document.createElement("option");blank.value="";blank.textContent="Choose source document";select.append(blank);
 for(const src of data.evidence||[]){
  if(src.kind!=="equipment"&&src.kind!=="other")continue;
  const opt=document.createElement("option");opt.value=src.source_id;opt.textContent=src.source_id+" · "+src.file_name;select.append(opt);
 }
 if([...select.options].some(x=>x.value===selected))select.value=selected;
}
function assemblyRows(basis){
 const tallies=data.assembly_tallies||{};return Array.isArray(tallies[basis])?tallies[basis]:[];
}
function invalidateAssemblyPositions(){
 data.assembly_positions=null;
 $("tallyPositionList").replaceChildren();
 $("tallyBridgeStatus").textContent="Tally changed. Run the Python calculation again after verifying the as-run anchor.";
}
function renderAnchorEditor(){
 const current=$("anchorComponent").value,select=$("anchorComponent");
 select.replaceChildren();
 const empty=document.createElement("option");empty.value="";empty.textContent="Select as-run component";select.append(empty);
 for(const item of assemblyRows("as_run")){
  const option=document.createElement("option");option.value=item.component_id;option.textContent=item.component_id;select.append(option);
 }
 const review=data.assembly_anchor||{};
 select.value=[...select.options].some(x=>x.value===current)?current:review.component_id||"";
 $("anchorEnd").value=review.end||"top";
 $("anchorDepth").value=review.measured_depth??"";
 $("anchorUnit").value=review.depth_unit||"";
 $("anchorDatum").value=review.datum||"";
 $("anchorSource").value=review.source_ref||"";
 $("anchorReviewer").value=review.reviewer||"";
 $("anchorReviewed").checked=review.reviewed===true;
 renderTallyPositions();
}
function renderTallyPositions(){
 const root=$("tallyPositionList");root.replaceChildren();
 const result=data.assembly_positions;
 if(!result||!Array.isArray(result.boundaries)){
  $("tallyBridgeStatus").textContent="No Python-calculated static boundaries. Source review or local bridge required.";
  return;
 }
 $("tallyBridgeStatus").textContent="Python tally calculated (reviewer-declared, NOT engineering approved). No dynamic position or tool-state inference.";
 for(const item of result.boundaries){
  const p=document.createElement("p");p.className="sub";
  p.textContent=item.component_id+" · top "+(item.top_md_m??"unknown")+" m MD; bottom "+(item.bottom_md_m??"unknown")+" m MD · "+item.source_ref;
  root.append(p);
 }
}
async function evaluateTally(){
 const basis="as_run",components=assemblyRows(basis);
 const measured_depth=$("anchorDepth").value.trim(),depth_unit=$("anchorUnit").value,
  source_ref=$("anchorSource").value.trim(),datum=$("anchorDatum").value.trim(),
  reviewer=$("anchorReviewer").value.trim(),component_id=$("anchorComponent").value,
  end=$("anchorEnd").value,reviewed=$("anchorReviewed").checked;
 if(!components.length)throw Error("Enter an as-run component tally before calculating boundaries.");
 if(!component_id||!["top","bottom"].includes(end)||measured_depth===""||
   !Number.isFinite(Number(measured_depth))||Number(measured_depth)<0||!["m","ft"].includes(depth_unit)||
   !source_ref||!datum||!reviewer||!reviewed)
  throw Error("Component boundary, non-negative depth, explicit unit/datum/source, reviewer and check declaration are all required.");
 const anchor={component_id,end,measured_depth,depth_unit,datum,source_ref,reviewer,reviewed};
 data.assembly_anchor=anchor;invalidateAssemblyPositions();persist();
 $("tallyBridgeStatus").textContent="Requesting local Python BHA tally engine…";
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),3500);
 try{
  const response=await fetch("http://127.0.0.1:8766/v1/tally/positions",{
   method:"POST",headers:{"Content-Type":"application/json"},
   body:JSON.stringify({basis,components,anchor}),signal:controller.signal});
  const result=await response.json();
  if(!response.ok)throw Error(result.error||"Tally rejected");
  if(result.basis!=="as_run"||!Array.isArray(result.boundaries))throw Error("Unexpected tally response");
  data.assembly_positions=result;renderTallyPositions();persist();
 }finally{clearTimeout(timeout)}
}
function renderAssemblyTallies(){
 assemblySourceOptions();
 const root=$("assemblyComponentList");root.replaceChildren();
 for(const basis of ["planned","as_run"]){
  const entries=assemblyRows(basis),header=document.createElement("h3");
  header.textContent=(basis==="as_run"?"As run":"Planned")+" · "+entries.length+" component(s) in reported top-to-bottom order";root.append(header);
  for(const [i,item] of entries.entries()){
   const row=document.createElement("div");row.className="row";
   const label=document.createElement("span");label.textContent=(i+1)+". "+item.component_id+" · "+assemblyRoleLabels[item.role]+
    " · "+(item.length===null?"length unknown":item.length+" "+item.length_unit)+" · "+item.source_ref;row.append(label);
   const remove=document.createElement("button");remove.type="button";remove.textContent="Remove "+item.component_id;
   remove.onclick=()=>{data.assembly_tallies[basis].splice(i,1);data.assembly_tallies[basis].forEach((c,j)=>c.sequence=j+1);if(basis==="as_run"){data.assembly_anchor=null;invalidateAssemblyPositions()}renderAssemblyTallies();renderAssemblyDisplay();persist()};
   row.append(remove);root.append(row);
  }
 }
 renderAnchorEditor();
 $("assemblyBuilderStatus").textContent="Planned: "+assemblyRows("planned").length+
  " component(s); as run: "+assemblyRows("as_run").length+
  ". Source-linked inventory only; no unverified depth offsets.";
}
function addAssemblyComponent(){
 const basis=$("assemblyBasis").value,source=$("assemblySource").value,
  component_id=$("assemblyComponentId").value.trim(),role=$("assemblyRole").value,
  lengthText=$("assemblyLength").value.trim(),unit=$("assemblyUnit").value,
  page=$("assemblyPage").value.trim();
 if(!["planned","as_run"].includes(basis)||!Object.hasOwn(assemblyRoleLabels,role))throw Error("Invalid assembly basis or role.");
 if(!data.evidence.some(x=>x.source_id===source&&(x.kind==="equipment"||x.kind==="other")))
  throw Error("Register and select the drawing/tally source before adding a component.");
 if(!component_id||!page)throw Error("Component ID and source page/row reference are required.");
 if(assemblyRows(basis).some(x=>x.component_id===component_id))
  throw Error("Duplicate component ID in this tally; top-to-bottom sequence must be unambiguous.");
 const length=lengthText===""?null:Number(lengthText);
 if(length!==null&&(!Number.isFinite(length)||length<=0||!["m","ft"].includes(unit)))
  throw Error("A documented length must be positive with explicit m or ft unit.");
 if(length===null&&unit)throw Error("Leave the unit unselected when length is unknown.");
 if(!data.assembly_tallies)data.assembly_tallies={planned:[],as_run:[]};
 if(!Array.isArray(data.assembly_tallies[basis]))data.assembly_tallies[basis]=[];
 if(basis==="as_run"){data.assembly_anchor=null;invalidateAssemblyPositions()}
 data.assembly_tallies[basis].push({component_id,role,length,length_unit:length===null?null:unit,
  source_id:source,source_ref:source+" / "+page,sequence:data.assembly_tallies[basis].length+1});
 $("assemblyComponentId").value="";$("assemblyLength").value="";$("assemblyUnit").value="";$("assemblyPage").value="";
 renderAssemblyTallies();renderAssemblyDisplay();persist();
}
const originalAssemblyShapes=[...$("moving").childNodes].map(node=>node.cloneNode(true));
function renderAssemblyGeometry(components,basis){
 const moving=$("moving");
 if(!components.length){moving.replaceChildren(...originalAssemblyShapes.map(node=>node.cloneNode(true)));return}
 const ns="http://www.w3.org/2000/svg";
 moving.replaceChildren();
 // Symbolic component order only. Equal-size blocks are NOT physical lengths or downhole positions.
 const spacing=2,top=8,span=278,block=Math.max(5,(span-(components.length-1)*spacing)/components.length);
 const palette={drill_pipe:"#658dad",running_tool:"#f3b86d",liner:"#a890e1",other:"#8d9ba8"};
 for(const [i,item] of components.entries()){
  const rect=document.createElementNS(ns,"rect");rect.setAttribute("x","139");
  rect.setAttribute("y",String(top+i*(block+spacing)));rect.setAttribute("width","42");
  rect.setAttribute("height",String(block));rect.setAttribute("fill",palette[item.role]);
  rect.setAttribute("data-role",item.role);rect.setAttribute("data-component-id",item.component_id);
  const title=document.createElementNS(ns,"title");
  title.textContent=(basis==="planned"?"PLANNED only: ":"As-run reported: ")+item.component_id+
   " · "+(item.length===null?"length unknown":item.length+" "+item.length_unit)+" · "+item.source_ref+
   " · equal-size symbolic block, not to scale";
  rect.append(title);moving.append(rect);
 }
}
function renderAssemblyDisplay(){
 const basis=$("assemblyDisplayBasis").value||"as_run",components=assemblyRows(basis);
 const root=$("assemblyReplayComponents");root.replaceChildren();
 renderAssemblyGeometry(components,basis);
 if(!components.length){
  $("assemblyTallySummary").textContent=basis==="planned"?
   "No planned component tally. Generic assembly is illustrative only.":
   "No as-run component tally. Generic assembly is illustrative only; planned equipment is not evidence of actual installation.";
  return;
 }
 const verified=components.every(x=>x.length!==null&&["m","ft"].includes(x.length_unit));
 $("assemblyTallySummary").textContent=(basis==="as_run"?"As-run source-linked tally":"PLANNED tally — not proof of actual equipment")+
  "; "+components.length+" component(s) · "+(verified?"all entered lengths explicitly sourced":"one or more lengths unknown")+
  ". Colored blocks show top-to-bottom order at equal symbolic height, not actual component dimensions. Running-depth source remains a separate measurement, not a BHA anchor.";
 for(const item of components){
  const entry=document.createElement("p");entry.className="sub";entry.textContent=
   item.sequence+". "+assemblyRoleLabels[item.role]+" ("+item.component_id+") · "+
   (item.length===null?"length unknown":item.length+" "+item.length_unit)+" · "+item.source_ref;root.append(entry);
 }
}

function procedureSourceOptions(){
 const select=$("procedureSource"),choice=select.value;select.replaceChildren();
 const placeholder=document.createElement("option");placeholder.value="";placeholder.textContent="Choose a registered SOP";select.append(placeholder);
 for(const item of data.evidence||[]){
  if(item.kind!=="procedure")continue;
  const option=document.createElement("option");option.value=item.source_id;
  option.textContent=item.source_id+" · "+item.file_name;select.append(option);
 }
 if([...select.options].some(op=>op.value===choice))select.value=choice;
}
function ensureManualProcedure(){
 if(!data.rules||!Array.isArray(data.rules.rules))data.rules={
  procedure:{approved:false,revision:"",approval_reference:"",reviewer:""},telemetry_clock_alignment_verified:false,
  channel_units:{},rules:[],required_event_sequence:[],manual_input:true};
 if(!Array.isArray(data.rules.required_event_sequence))data.rules.required_event_sequence=[];
 if(!data.rules.channel_units)data.rules.channel_units={};
}
function renderProcedureSteps(){
 procedureSourceOptions();
 const root=$("procedureSteps");root.replaceChildren();
 const book=data.rules||{},entries=[
  ...(book.required_event_sequence||[]).map(x=>({...x,kind:"event"})),
  ...(book.rules||[]).map(x=>({...x,kind:"signal",code:x.id}))
 ];
 for(const item of entries){
  const article=document.createElement("article");article.className="panel";article.style.margin="7px 0";article.style.padding="10px";
  const strong=document.createElement("strong");strong.textContent=item.code+" · "+(item.step||"Unnamed step")+" · "+item.kind;article.append(strong);
  const p=document.createElement("p");p.textContent=(item.source_reference||"No page supplied")+
   " · "+(item.approved===true?"source declared reviewed":"draft/not verified");
  article.append(p);
  if(item.kind==="signal"){
   const second=document.createElement("p");second.textContent=item.channel+" "+item.operator+" "+item.value+" "+item.unit+
    " (from "+(item.window?.start||"?")+" to "+(item.window?.end||"?")+")";article.append(second);
  }
  if(book.manual_input===true){
   const remove=document.createElement("button");remove.type="button";remove.textContent="Remove this draft step";
   remove.onclick=()=>{
    if(item.kind==="event")book.required_event_sequence=book.required_event_sequence.filter(x=>x.code!==item.code);
    else book.rules=book.rules.filter(x=>x.id!==item.code);
    book.procedure.approved=false;book.telemetry_clock_alignment_verified=false;
    (book.rules||[]).forEach(x=>x.approved=false);
    (book.required_event_sequence||[]).forEach(x=>x.approved=false);
    renderProcedureSteps();describe();findings();persist();
   };article.append(remove);
  }
  root.append(article);
 }
 $("procedureStatus").textContent=entries.length+" source-linked step(s) entered. "+(
   book.procedure?.approved===true?"Investigator declares source procedure checked; external approval unverified.":"Draft/unreviewed — deviations cannot be confirmed.");
}
function addManualProcedureStep(){
 const source=$("procedureSource").value,revision=$("procedureRevision").value.trim(),
  page=$("procedurePage").value.trim(),code=$("procedureCode").value.trim(),
  step=$("procedureStep").value.trim(),kind=$("procedureCheck").value;
 if(!source||!data.evidence.some(x=>x.kind==="procedure"&&x.source_id===source))
  throw Error("Register and select the applicable SOP source file first");
 if(!revision||!page||!code||!step)throw Error("Procedure revision, page/section, code and step label are required");
 if(!/^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$/.test(code))throw Error("Step code must be 1–80 letters, digits, dots, dashes or underscores");
 // Do not overwrite a separately imported rulebook with draft steps.
 if(data.rules?.manual_input!==true&&data.rules&&(
   data.rules.rules?.length||data.rules.required_event_sequence?.length))
  throw Error("A separate JSON procedure is already loaded; export that case before starting an independent manual rulebook");
 ensureManualProcedure();const book=data.rules;
 if(book.procedure.approval_reference&&book.procedure.approval_reference!==source)
  throw Error("This case already uses another procedure source; create a separate case or clear the draft");
 if(book.procedure.revision&&book.procedure.revision!==revision)
  throw Error("Procedure revision changed: do not mix different SOP revisions in one rulebook");
 if(book.rules.some(x=>x.id===code)||book.required_event_sequence.some(x=>x.code===code))
  throw Error("Step code already exists");
 const ref=source+" / "+page;
 if(kind==="event"){
  book.required_event_sequence.push({code,step,approved:false,source_reference:ref});
 }else{
  const channel=$("procedureChannel").value,operator=$("procedureOperator").value,
   unit=$("procedureUnit").value.trim(),raw=$("procedureThreshold").value.trim(),
   start=$("procedureStart").value.trim(),end=$("procedureEnd").value.trim(),
   value=number(raw);
  if(raw===""||value===null||!unit)throw Error("Documented numeric limit and source unit are required");
  if(!/(?:Z|[+-]\d{2}:\d{2})$/i.test(start)||!/(?:Z|[+-]\d{2}:\d{2})$/i.test(end)||
    !Number.isFinite(Date.parse(start))||!Number.isFinite(Date.parse(end))||Date.parse(end)<=Date.parse(start))
    throw Error("Valid chronological start/end timestamps with explicit timezone are required");
  book.rules.push({id:code,step,description:"Investigator-entered source-linked comparison; not automatically OEM approved",
   approved:false,source_reference:ref,channel,operator,value,unit,window:{
    start:new Date(start).toISOString(),end:new Date(end).toISOString()}});
  book.channel_units[channel]=data.channel_units?.[channel]||"";
 }
 book.procedure={approved:false,revision,approval_reference:source,reviewer:""};
 book.telemetry_clock_alignment_verified=false;
 (book.rules||[]).forEach(x=>x.approved=false);
 (book.required_event_sequence||[]).forEach(x=>x.approved=false);
 $("procedurePage").value="";$("procedureCode").value="";$("procedureStep").value="";
 renderProcedureSteps();describe();findings();persist();
}
function saveManualProcedureReview(){
 if(!data.rules||data.rules.manual_input!==true)throw Error("Enter draft steps through this form before recording review");
 const book=data.rules,verified=$("procedureApprovalChecked").checked,
  clock=$("procedureClockChecked").checked,reviewer=$("procedureReviewer").value.trim();
 if((verified||clock)&&!reviewer)throw Error("A reviewer identifier is required for source/clock declarations");
 if(verified&&!data.evidence.some(x=>x.kind==="procedure"&&x.source_id===book.procedure.approval_reference))
  throw Error("The registered SOP source must remain attached to the case");
 book.procedure.approved=verified;book.procedure.reviewer=reviewer;
 book.telemetry_clock_alignment_verified=clock;
 for(const rule of book.rules){rule.approved=verified;
  book.channel_units[rule.channel]=data.channel_units?.[rule.channel]||"";}
 for(const step of book.required_event_sequence)step.approved=verified;
 $("procedureReviewPanel").hidden=true;renderProcedureSteps();findings();persist();
}
function describe(){
 $("importSummary").textContent=data.rows.length+" timestamped samples, "+data.events.length+" reported events, "+
 (data.rules?.rules?.length||0)+" procedure rules, "+data.notes.length+" annotations, "+(data.evidence?.length||0)+" evidence files. Case: "+(data.id||"unnamed")+".";
 $("diagnostics").replaceChildren();
 for(const warning of data.warnings){const p=document.createElement("p");p.className="danger";p.textContent="⚠ "+warning;$("diagnostics").append(p)}
 const p=document.createElement("p");p.textContent="Mapped: "+(data.columns.join(", ")||"none")+". Original units are not inferred or converted.";$("diagnostics").append(p);
}
function renderCharts(){
 const root=$("charts");root.replaceChildren();plotCanvases=[];
 const available=channels.filter(x=>data.columns.includes(x[0]));
 if(!available.length){root.textContent="No supported numeric channels found.";return}
 for(const [key,name,unit] of available){
  const box=document.createElement("div");box.className="chart";
  const label=document.createElement("strong");const sourceUnit=data.case_kind==="synthetic"?unit:(data.channel_units?.[key]||"unknown unit");label.textContent=name+" ("+sourceUnit+"; original reading, no conversion)";
  const value=document.createElement("span");value.className="tag";value.style.float="right";box.append(label,value);
  const canvas=document.createElement("canvas");canvas.width=540;canvas.height=112;canvas.setAttribute("aria-label",name+" trend");box.append(canvas);root.append(box);
  const indexAt=e=>{const bounds=canvas.getBoundingClientRect(),[start,end]=viewBounds();return visibleIndexAt((e.clientX-bounds.left)/bounds.width,start,end)};
  let pressed=null;
  canvas.addEventListener("pointerdown",e=>{pressed={index:indexAt(e),x:e.clientX};canvas.setPointerCapture(e.pointerId)});
  canvas.addEventListener("pointerup",e=>{
    if(!pressed)return;const a=pressed.index,b=indexAt(e),distance=Math.abs(e.clientX-pressed.x);
    pressed=null;
    if(distance>=12&&Math.abs(b-a)>=1){pausePlayback();tab("notes");openNote(Math.min(a,b),Math.max(a,b));return}
    pausePlayback();idx=b;renderCursor();
  });
  canvas.addEventListener("pointermove",e=>{
    if(pressed)return;const point=indexAt(e),hit=data.notes.find(n=>point>=n.a&&point<=n.b);
    canvas.title=hit?hit.title+" — "+hit.kind+"; open Notes to edit":"Click to replay; drag to annotate a time range";
  });plotCanvases.push({key,canvas,value});
 }
}
function drawCharts(){
 for(const {key,canvas,value} of plotCanvases){
  const ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);ctx.strokeStyle="#314d62";ctx.beginPath();ctx.moveTo(0,h-16);ctx.lineTo(w,h-16);ctx.stroke();
  const [start,end]=viewBounds(),visible=data.rows.slice(start,end+1),vals=visible.map(r=>r[key]);const valid=vals.filter(Number.isFinite);
  value.textContent=fmt(current()?.[key]);if(!valid.length)continue;
  let lo=Math.min(...valid),hi=Math.max(...valid);if(lo===hi){lo-=1;hi+=1}
  ctx.strokeStyle="#79cbea";ctx.lineWidth=1.5;ctx.beginPath();let connected=false;
  vals.forEach((v,i)=>{if(!Number.isFinite(v)){connected=false;return}
   const x=timeFraction(start+i,start,end)*w,y=(h-18)-(v-lo)/(hi-lo)*(h-27);
   if(connected)ctx.lineTo(x,y);else ctx.moveTo(x,y);connected=true;
  });ctx.stroke();
  for(const m of data.notes){if(m.b<start||m.a>end)continue;const a=timeFraction(Math.max(start,m.a),start,end)*w,b=timeFraction(Math.min(end,m.b),start,end)*w;ctx.fillStyle="rgba(255,195,126,.17)";ctx.fillRect(a,0,Math.max(2,b-a),h-15)}
  ctx.strokeStyle="#ffcb90";ctx.beginPath();ctx.moveTo(timeFraction(idx,start,end)*w,0);ctx.lineTo(timeFraction(idx,start,end)*w,h-12);ctx.stroke();
 }
}
function assembly(){
 const sample=current();const svg=$("moving"),label=$("assemblyStatus");
 if(!sample){svg.setAttribute("transform","translate(0 0)");label.textContent="No case loaded";return}
 const unitVerified=data.case_kind==="synthetic"||!!data.channel_units?.running_depth;
 let observedIndex=-1;
 if(unitVerified){for(let j=idx;j>=0;j--){if(Number.isFinite(data.rows[j].running_depth)){observedIndex=j;break}}}
 if(observedIndex>=0){
  const depth=data.rows[observedIndex].running_depth;
  const valid=data.rows.map(r=>r.running_depth).filter(Number.isFinite),min=Math.min(...valid),max=Math.max(...valid);
  const y=40+(max>min?(depth-min)/(max-min)*35:0);
  svg.setAttribute("transform","translate(0 "+y+")");
  label.textContent=(observedIndex===idx?"Running-depth-sourced movement at ":"Holding last recorded running depth (sample "+(observedIndex+1)+", "+timestampAt(observedIndex)+") at ")+fmt(depth)+" "+(data.channel_units?.running_depth||"m MD")+". Assembly geometry remains schematic, not to scale; no depth interpolation.";
 }else{
  svg.setAttribute("transform","translate(0 0)");
  label.textContent="No confirmed running-string depth AND unit. Assembly is a stationary schematic; hole/bit depth cannot establish liner-hanger position.";
 }
}
function renderCursor(){
 if(!data.rows.length)return;
 idx=Math.max(0,Math.min(data.rows.length-1,idx));$("seek").max=data.rows.length-1;$("seek").value=idx;
 $("cursorTime").textContent=timestampAt(idx)+" · sample "+(idx+1)+"/"+data.rows.length;
 $("noteFrom").max=$("noteTo").max=data.rows.length-1;
 $("cursorValues").textContent=channels.filter(x=>data.columns.includes(x[0])).map(x=>x[1]+": "+fmt(current()[x[0]])+" "+(data.case_kind==="synthetic"?x[2]:(data.channel_units?.[x[0]]||"unit unverified"))).join("  ·  ");
 drawCharts();assembly();
 const [a,b]=viewBounds();$("visibleRange").textContent=data.rows.length?("Viewing "+timestampAt(a)+" – "+timestampAt(b)+" · "+(b-a+1)+" samples"):"No range";
 document.querySelectorAll("#timeline button").forEach(b=>b.classList.toggle("active",Number(b.dataset.sample)===idx));
}
function nearest(t){if(!data.rows.length)return 0;let closest=0,best=Infinity;
 data.rows.forEach((r,i)=>{const d=Math.abs(Date.parse(r.t)-Date.parse(t));if(d<best){best=d;closest=i}});return closest}
function renderEvents(){
 const root=$("timeline");root.replaceChildren();
 if(!data.events.length){root.textContent="No job chronology supplied.";return}
 for(const event of data.events){
  const button=document.createElement("button");button.type="button";
  const matched=alignedEventTime(event),index=matched&&data.rows.length?nearest(matched):null;
  button.dataset.sample=index??-1;
  button.disabled=index===null;
  button.textContent=(event.time||"Time not verified")+" · "+(event.label||event.description||"Reported event")+
    " — source: "+(event.source||"not supplied")+
    (matched?" · aligned rig time: "+matched+" (reviewer-declared)": " · clock not verified / time unavailable");
  button.onclick=()=>{if(index!==null){pausePlayback();idx=index;renderCursor()}};
  root.append(button)
 }
}
function runRules(){
 const out=[];const book=data.rules;if(!book||!Array.isArray(book.rules))return out;
 const approved=book.procedure?.approved===true&&!!book.procedure.revision&&!!book.procedure.approval_reference;
 const aligned=book.telemetry_clock_alignment_verified===true;
 for(const rule of book.rules){
  const entry={id:rule.id||"rule",step:rule.step||"",description:rule.description||"",status:"unverifiable",reasons:[],instances:[],source:rule.source_reference||""};
  if(!approved)entry.reasons.push("Job-specific procedure approval/revision/reference not independently established");
  if(rule.approved!==true)entry.reasons.push("Rule approval missing");
  if(!rule.source_reference)entry.reasons.push("Procedure step/source missing");
  if(!aligned)entry.reasons.push("Clock alignment not verified");
  if(!data.columns.includes(rule.channel))entry.reasons.push("Channel missing");
  if(!["<","<=",">",">=","between"].includes(rule.operator)||number(rule.value)===null||rule.operator==="between"&&number(rule.upper)===null)entry.reasons.push("Invalid comparator/threshold");
  if(!book.channel_units?.[rule.channel]||book.channel_units[rule.channel]!==rule.unit||(!["synthetic"].includes(data.case_kind)&&data.channel_units?.[rule.channel]!==rule.unit))
    entry.reasons.push("Rule unit not verified against source channel");
  const start=Date.parse(rule.window?.start||""),end=Date.parse(rule.window?.end||"");
  if(!Number.isFinite(start)||!Number.isFinite(end)||end<=start)entry.reasons.push("Invalid observation window");
  if(entry.reasons.length){out.push(entry);continue}
  const records=data.rows.filter(r=>Date.parse(r.t)>=start&&Date.parse(r.t)<end);
  const values=records.filter(r=>Number.isFinite(r[rule.channel]));
  if(!records.length||values.length/records.length<Number(rule.min_coverage??.8)){entry.reasons.push("Signal coverage insufficient");out.push(entry);continue}
  const complies=v=>{const a=Number(rule.value),b=Number(rule.upper);switch(rule.operator){case "<":return v<a;case "<=":return v<=a;case ">":return v>a;case ">=":return v>=a;default:return v>=a&&v<=b}};
  const failures=values.filter(r=>!complies(r[rule.channel]));
  entry.status=failures.length?"deviation_candidate":"met";
  // Consecutive failing samples are displayed separately; never bridge over a gap.
  let group=[];function flush(){if(!group.length)return;
   entry.instances.push({start:group[0].t,end:group[group.length-1].t,count:group.length,
      low:Math.min(...group.map(r=>r[rule.channel])),high:Math.max(...group.map(r=>r[rule.channel]))});group=[]}
  for(const row of records){
   const failed=Number.isFinite(row[rule.channel])&&!complies(row[rule.channel]);
   if(!failed){flush();continue}
   if(group.length&&Date.parse(row.t)-Date.parse(group[group.length-1].t)>Number(rule.max_gap_minutes??5.2)*60000)flush();
   group.push(row);
  }flush();out.push(entry);
 }
 // Procedure-event checks are *reported chronology*, not proof of a downhole step.
 // Absence from an incomplete log remains an evidence gap, never an asserted omission.
 const required=book.required_event_sequence;
 if(Array.isArray(required)){
  let previous=null;
  for(const requiredStep of required){
   const id=requiredStep.code;
   const entry={id:"EVENT-"+(id||"?"),step:requiredStep.step||id||"Reported event",
    description:"Chronological reported procedure step (not independently verified)",
    source:requiredStep.source_reference||"",status:"unverifiable",instances:[],reasons:[]};
   if(!approved||!aligned||!clockVerified()||requiredStep.approved!==true||!entry.source)
    entry.reasons.push("Approved source/clock alignment or step reference not established");
   if(!id||typeof id!=="string")entry.reasons.push("Required event code missing");
   const matching=data.events.filter(e=>e.code===id);
   if(!matching.length)entry.reasons.push("Required step not found in supplied chronology; absence does not prove omission");
   if(matching.length>1)entry.reasons.push("Duplicate reported step events; exact sequence requires engineer review");
   if(matching.length===1){
    const t=Date.parse(alignedEventTime(matching[0])||"");
    if(!Number.isFinite(t)||!matching[0].source)entry.reasons.push("Reported event time/source or clock reconciliation not verified");
    else if(!entry.reasons.length){
     entry.status=previous!==null&&t<previous?"reported_order_question":"reported_in_sequence";
     if(entry.status==="reported_order_question")
      entry.reasons.push("Reported event precedes a previous required step; confirm chronology and procedure");
    }
    if(Number.isFinite(t))previous=t;
   }
   out.push(entry);
  }
 }
 return out;
}
function findings(){
 const results=runRules();const root=$("findings");root.replaceChildren();
 $("ruleSummary").textContent=results.length?results.filter(r=>r.status==="deviation_candidate"||r.status==="reported_order_question").length+
 " rule(s) with apparent deviation candidates; "+results.filter(r=>r.status==="unverifiable").length+
 " unverifiable. All findings require independent review.":"No job-specific procedure rulebook loaded. Compliance cannot be assessed.";
 for(const r of results){
  const box=document.createElement("article");box.className=r.status==="deviation_candidate"||r.status==="reported_order_question"?"flag":r.status==="met"||r.status==="reported_in_sequence"?"met":"gap";
  const h=document.createElement("strong");h.textContent=r.id+" · "+r.step+" · "+r.status.replace(/_/g," ");box.append(h);
  const p=document.createElement("p");p.textContent=r.description+" · source: "+(r.source||"unavailable");box.append(p);
  for(const reason of r.reasons){const x=document.createElement("p");x.className="danger";x.textContent=reason;box.append(x)}
  for(const instance of r.instances){const x=document.createElement("button");x.type="button";x.textContent=instance.start+" to "+instance.end+
   " · "+instance.count+" failing reading(s) · "+fmt(instance.low)+"–"+fmt(instance.high);
   x.onclick=()=>{pausePlayback();idx=nearest(instance.start);tab("replay");renderCursor()};box.append(x)}
  root.append(box);
 }
 return results;
}
function notes(){
 const root=$("notesList");root.replaceChildren();
 if(!data.notes.length){root.textContent="No annotations yet.";return}
 for(const [i,n] of data.notes.entries()){
  const block=document.createElement("article");const head=document.createElement("strong");head.textContent=n.title+" · "+n.kind;block.append(head);
  const p=document.createElement("p");p.textContent=timestampAt(n.a)+" — "+timestampAt(n.b)+" · "+(n.source||"No external source");block.append(p);
   const review=document.createElement("p");review.textContent="Confidence: "+(n.confidence||"undetermined")+" · Disposition: "+(n.disposition||"open")+" · Reviewer: "+(n.reviewer||"unassigned");block.append(review);
   if(n.alternative){const alternative=document.createElement("p");alternative.textContent="Alternative / contrary evidence: "+n.alternative;block.append(alternative)}
  const body=document.createElement("p");body.textContent=n.body;block.append(body);
  const edit=document.createElement("button");edit.textContent="Edit";edit.onclick=()=>openNote(n.a,n.b,i);block.append(edit);
  const jump=document.createElement("button");jump.textContent="Go to range";jump.onclick=()=>{pausePlayback();idx=n.a;tab("replay");renderCursor()};block.append(jump);
  root.append(block);
 }
}
function openNote(a,b,edit=null){
 if(!data.rows.length){msg("Load telemetry before creating time-specific annotations");tab("import");return}
 a=Math.max(0,Math.min(data.rows.length-1,Number(a)||0));b=Math.max(a,Math.min(data.rows.length-1,Number(b)||a));
 $("noteFrom").value=a;$("noteTo").value=b;$("editIndex").value=edit===null?"":String(edit);
 const n=edit===null?null:data.notes[edit];$("noteTitle").value=n?.title||"";$("noteBody").value=n?.body||"";
 $("noteKind").value=n?.kind||"observation";$("noteSource").value=n?.source||"";
  $("noteAlternative").value=n?.alternative||"";$("noteConfidence").value=n?.confidence||"undetermined";$("noteDisposition").value=n?.disposition||"open";$("noteReviewer").value=n?.reviewer||"";
 $("noteInterval").textContent=timestampAt(a)+" — "+timestampAt(b)+" (recorded sample indices "+a+"–"+b+")";
 $("noteDialog").showModal();
}
function report(){
 const check=runRules(),lines=[
 "# Liner Hanger Investigation — Draft",
 "",
 "**Case:** "+(data.id||"unspecified"),"**Well:** "+(data.well||"unspecified"),
 "**Case source:** "+(data.source||"not supplied"),
 "**Status:** DRAFT — NOT INDEPENDENTLY ENGINEERING APPROVED",
 "**Root cause:** UNDETERMINED; no automatic conclusion",
 "",
 "## Registered source documents",
 ...(data.evidence||[]).map(x=>"- "+x.source_id+" ["+x.kind+"] "+x.file_name+
  " · "+x.review_status+" · SHA-256: "+(x.sha256||"unavailable")+" · original bytes not embedded"),
 ...(data.evidence?.length?[]:["No source documents registered"]),
 "",
 "## Telemetry and boundaries",
 "Samples: "+data.rows.length+". Channels: "+(data.columns.join(", ")||"none")+".",
 "Source channel mapping (no unit conversion):",
 ...Object.entries(data.telemetry_mapping?.assignments||{}).map(([key,x])=>
  "- "+key+" ← "+x.raw_header+" [source unit: "+(x.source_unit||"unverified")+"]"),
 "Mapped source file: "+(data.telemetry_mapping?.file_name||"not supplied")+
 " · original CSV bytes not embedded; source unit assertions require review.",
 "First timestamp: "+(data.rows[0]?.t||"unavailable"),
 "Last timestamp: "+(data.rows[data.rows.length-1]?.t||"unavailable"),
 ...data.warnings.map(w=>"- Evidence gap: "+w),
 "",
 "## Chronological reported events",
 "Event/rig clock check: "+(clockVerified()?"investigator-declared; source "+(data.event_clock?.source||"synthetic only")+"; reviewer "+(data.event_clock?.reviewer||"fictional"):"unverified; no aligned event interpretation")+
 " · correction "+(clockVerified()?(data.event_clock?.offset_minutes??0):"not applied")+" minutes.",
 ...data.events.map(e=>"- Reported: "+(e.time||"Time unverified")+"; aligned to rig: "+(alignedEventTime(e)||"unverified")+" — "+(e.label||e.description||"Event")+" [source: "+(e.source||"not supplied")+"]"),
 "",
 "## Assembly tally (source linked, independent of depth positioning)",
 ...["planned","as_run"].flatMap(b=>["### "+(b==="as_run"?"As run":"Planned") ,...(assemblyRows(b).length?assemblyRows(b).map(x=>"- "+x.sequence+". "+x.component_id+" ["+x.role+"] "+(x.length===null?"length unknown":x.length+" "+x.length_unit)+" · "+x.source_ref):["No "+b+" component tally entered."])]),
  "Source-listed lengths do not establish actual downhole placement or activation.",
 "As-run anchor review: "+(data.assembly_anchor?(JSON.stringify(data.assembly_anchor)):"not supplied")+".",
 "Python tally static boundaries: "+(data.assembly_positions?"investigator-declared, not engineering approved":"not calculated; no verified positions")+".",
 ...(data.assembly_positions?.boundaries||[]).map(x=>"- "+x.component_id+" top "+(x.top_md_m??"unknown")+" m MD; bottom "+(x.bottom_md_m??"unknown")+" m MD; source "+x.source_ref),
 "",
 "## Entered operating procedure",
 "Source: "+(data.rules?.procedure?.approval_reference||"not supplied")+
 " · Revision: "+(data.rules?.procedure?.revision||"not supplied")+
 " · Investigator review: "+(data.rules?.procedure?.approved===true?"declared by investigator, not externally authenticated":"not declared")+
 " · Clock alignment: "+(data.rules?.telemetry_clock_alignment_verified===true?"investigator declared":"not verified")+
 " · Reviewer declaration: "+(data.rules?.procedure?.reviewer||"not supplied"),
 ...(data.rules?.required_event_sequence||[]).map(x=>"- Required reported step "+x.code+" · "+x.step+" · "+x.source_reference),
 ...(data.rules?.rules||[]).map(x=>"- Measured rule "+x.id+" · "+x.step+" · "+x.channel+" "+x.operator+" "+x.value+" "+x.unit+
  " · "+x.source_reference),
 "",
 "## Procedure comparison",
 ];
 if(!check.length)lines.push("No procedure rulebook supplied. Compliance cannot be verified.");
 for(const r of check){
  lines.push("### "+r.id+" · "+r.step+" — "+r.status, r.description,
   "Source: "+(r.source||"not supplied"),...r.reasons.map(x=>"- Unresolved: "+x));
  for(const item of r.instances)lines.push("- Apparent deviation window: "+item.start+" to "+item.end+
   ", "+item.count+" readings, observed "+fmt(item.low)+"–"+fmt(item.high)+". Engineer review required.");
 }
 lines.push("","## Annotated evidence");
 if(!data.notes.length)lines.push("No engineer annotations recorded.");
 for(const n of data.notes)lines.push("- **"+n.title+"** ("+n.kind+") "+timestampAt(n.a)+" to "+timestampAt(n.b)+
  "\n  - "+(n.body||"No explanation recorded")+"\n  - Source: "+(n.source||"not supplied")+"\n  - Alternative/contrary evidence: "+(n.alternative||"not recorded")+"\n  - Confidence: "+(n.confidence||"undetermined")+"\n  - Disposition: "+(n.disposition||"open")+"\n  - Reviewer: "+(n.reviewer||"unassigned"));
 lines.push("","## Competing explanations / unknowns",
 "Surface signals and procedure flags alone cannot confirm hanger actuation or internal failure.",
 "Possible alternative mechanisms must be reviewed against job-specific OEM documents and independent rig reports.",
 "Missing readings, unverifiable clock alignment and unreviewed rulebook declarations remain unresolved.",
 "","## Human review","Reviewer: not assigned.","Engineering approval: NOT COMPLETED.",
 "","_Offline engineering demonstration only. No live operating instructions or OEM setpoints are provided._");
 return lines.join("\n")+"\n";
}
function tab(name){
 if(name!=="replay")pausePlayback();
 document.querySelectorAll(".tab").forEach(x=>x.hidden=x.id!==name);
 document.querySelectorAll("[data-tab]").forEach(x=>x.classList.toggle("active",x.dataset.tab===name));
 // Import forms may be long: reset scroll so the new replay canvas is in view and interactive.
 document.documentElement.scrollTop=0;document.body.scrollTop=0;
 if(name==="replay")renderCursor();if(name==="deviations")findings();if(name==="notes")notes();if(name==="report")$("reportText").value=report();
}
function loadData(next){
 pausePlayback();
 if(timer){clearInterval(timer);timer=null;$("play").textContent="▶ Play"}
 attachedSourceFiles.clear();closeDocumentPreview();validateCase(next);idx=0;viewStart=0;viewEnd=null;toFields();describe();renderEvidence();renderProcedureSteps();renderEventClock();renderAssemblyTallies();renderAssemblyDisplay();renderCharts();renderEvents();findings();notes();renderCursor();persist();
 msg("Loaded "+data.rows.length+" recorded samples into "+(data.id||"case")+". Data are not independently authenticated.");
}
function demo(anomaly){
 const start=Date.parse("2026-11-10T09:00:00Z"),rows=[];
 for(let i=0;i<61;i++){
  rows.push({t:stamp(start+i*60000),source_row:i+2,depth:1500+i*.5,running_depth:1450+i*.5,
   spp:120+(anomaly&&i>=24&&i<=30?110:0)+(i%3),
   hookload:118+(anomaly&&i>=24&&i<=30?-19:0)+(i%4),
   torque:2.3+(i%3)*.1,rpm:12+(i%2),flow:170+(i%3),
   volume:i*.9,returns:169+(i%3)});
 }
 const rules={procedure:{approved:true,revision:"SYNTHETIC-v1",approval_reference:"FICTIONAL-TRAINING-ONLY"},
  telemetry_clock_alignment_verified:true,channel_units:{spp:"psi"},
  rules:[{id:"SYNTHETIC-PRESSURE-01",step:"Example circulation monitoring",description:"Illustrative pressure ceiling, not a Baker Hughes/OEM limit",
   approved:true,source_reference:"FICTIONAL-EXAMPLE/P1",channel:"spp",operator:"<=",value:180,unit:"psi",
   window:{start:stamp(start+10*60000),end:stamp(start+50*60000)},min_coverage:.9,max_gap_minutes:1.5}]};
 const events=[{time:stamp(start+5*60000),label:"Assembly running",source:"SYNTHETIC-JOB-LOG"},
  {time:stamp(start+23*60000),label:anomaly?"Pressure increase reported — investigate":"Circulation continued normally",source:"SYNTHETIC-JOB-LOG"},
  {time:stamp(start+52*60000),label:"Operation stopped for review",source:"SYNTHETIC-JOB-LOG"}];
 return {schema:"liner-mvp-case-1",id:anomaly?"SYNTHETIC-MVP-ANOMALOUS":"SYNTHETIC-MVP-NORMAL",well:"Fictional Well A",
  source:"SYNTHETIC-UTC-NO-RIG-DATA",rows,events,rules,notes:[],columns:channels.map(x=>x[0]),
  warnings:["All case readings, procedure approvals and limits are fictional demonstrations, not OEM specifications."],
  case_kind:"synthetic",verified_physics:false};
}
document.querySelectorAll("[data-tab]").forEach(b=>b.onclick=()=>tab(b.dataset.tab));
$("addEvidence").onclick=async()=>{
 try{loadState();await registerEvidence($("evidenceFile").files[0],
  $("evidenceType").value,$("evidenceReference").value.trim(),$("evidenceReview").value);
  $("evidenceFile").value="";$("evidenceReference").value="";
 }catch(err){$("evidenceStatus").textContent="Evidence not added: "+err.message}
};
$("closeDocument").onclick=closeDocumentPreview;
$("addAssemblyComponent").onclick=()=>{try{addAssemblyComponent()}catch(e){$("assemblyBuilderStatus").textContent="Component rejected: "+e.message}};
$("assemblyDisplayBasis").onchange=renderAssemblyDisplay;
$("evaluateTally").onclick=async()=>{
 try{await evaluateTally()}
 catch(e){$("tallyBridgeStatus").textContent="Tally not calculated: "+(e.name==="AbortError"?"local bridge timed out":e.message)+
  ". Start the optional local Python bridge to enable source-gated boundaries."}
};
$("saveEventClock").onclick=()=>{
 try{saveEventClock()}catch(e){$("eventClockStatus").textContent="Clock review rejected: "+e.message}
};
$("normal").onclick=()=>{loadData(demo(false));tab("replay")};
$("anomalous").onclick=()=>{loadData(demo(true));tab("replay")};
$("restore").onclick=()=>{try{const value=localStorage.getItem("liner_mvp_case_v1");if(!value)throw Error("No saved local case");loadData(JSON.parse(value))}catch(e){msg(e.message)}};
$("saveCase").onclick=()=>{loadState();msg(persist()?"Saved case in this browser. Export JSON for portable backup.":"Browser storage unavailable; export JSON for backup.")};
$("exportCase").onclick=$("downloadCase").onclick=()=>{loadState();filename(safe(data.id)+".json",JSON.stringify(data,null,2))};
$("caseFile").onchange=async e=>{try{loadData(JSON.parse(await e.target.files[0].text()));tab("replay")}catch(err){msg("Case import rejected: "+err.message)}};
$("telemetryFile").onchange=async e=>{
 try{
  const file=e.target.files?.[0];if(!file)return;
  const text=await file.text(),table=csvRecords(text);
  if(table.length<2)throw Error("CSV needs a header and at least one timestamped row");
  const mapping=guessMapping(table[0]);
  if(mapping.t===undefined||Object.keys(mapping).length<=1){
   openTelemetryMapping(text,file);
   msg("Review the source headers: select a timestamp and map each measured channel.");
  }else{
   // Known column names preserve the earlier quick-import path, but units remain unverified.
   acceptImportedCSV(text,file.name,mapping,{});
   $("telemetryMappingPanel").hidden=true;
  }
 }catch(err){msg("CSV import rejected: "+err.message)}
};
$("reviewMapping").onclick=async()=>{
 try{
  const file=$("telemetryFile").files?.[0];
  if(!file)throw Error("Select a telemetry CSV before reviewing column mappings");
  openTelemetryMapping(await file.text(),file);
  msg("Review all selected source columns and confirm their units; original readings are not modified.");
 }catch(e){msg(e.message)}
};
$("applyMapping").onclick=()=>{
 try{
  if(!pendingTelemetry)throw Error("No pending CSV source");
  const mapping={},sourceUnits={};
  for(const el of document.querySelectorAll("#mappingFields [data-mapping-key]")){
   if(el.value!=="")mapping[el.dataset.mappingKey]=Number(el.value);
  }
  for(const el of document.querySelectorAll("#mappingFields [data-unit-key]")){
   if(el.value)sourceUnits[el.dataset.unitKey]=el.value;
  }
  acceptImportedCSV(pendingTelemetry.text,pendingTelemetry.name,mapping,sourceUnits);
  pendingTelemetry=null;$("telemetryMappingPanel").hidden=true;
 }catch(err){$("mappingStatus").textContent="Mapping rejected: "+err.message}
};
$("cancelMapping").onclick=()=>{pendingTelemetry=null;$("telemetryMappingPanel").hidden=true};
$("addEvent").onclick=()=>{
 const label=$("eventLabel").value.trim(),source=$("eventSource").value.trim(),raw=$("eventTime").value.trim();
 if(!label||!source){$("eventStatus").textContent="Action and report/page source reference are both required.";return}
 if(raw&&!/(?:Z|[+-]\d{2}:\d{2})$/i.test(raw)){
  $("eventStatus").textContent="Use a timestamp with explicit UTC Z or timezone offset, or leave time unknown.";return}
 const time=raw?Date.parse(raw):NaN;
 if(raw&&!Number.isFinite(time)){$("eventStatus").textContent="Invalid reported timestamp; nothing added.";return}
 invalidateEventClock("Reported chronology changed");
 data.events.push({time:raw?new Date(time).toISOString():null,label,source,code:$("eventCode").value.trim()||undefined,
  time_status:raw?"reported_unverified":"unknown",evidence_class:"reported_not_measured"});
 renderEventClock();renderEvents();findings();describe();persist();
 $("eventLabel").value="";$("eventTime").value="";$("eventCode").value="";
 $("eventStatus").textContent="Reported event registered. Time and event are source assertions, not verified downhole actions.";
};
$("eventsFile").onchange=async e=>{
 try{const events=JSON.parse(await e.target.files[0].text());if(!Array.isArray(events)||events.some(x=>typeof x!=="object"||x===null))
   throw Error("Expected JSON array of {time,label,source} events");
 invalidateEventClock("Reported chronology changed");data.events.push(...events);renderEventClock();renderEvents();findings();describe();persist();msg("Added "+events.length+" reported events to the case; times are source assertions.")
 }catch(err){msg("Event import rejected: "+err.message)}
};
$("procedureCheck").onchange=()=>{$("procedureSignalInputs").hidden=$("procedureCheck").value!=="signal"};
$("addProcedureStep").onclick=()=>{try{addManualProcedureStep()}catch(e){$("procedureStatus").textContent="Draft step not saved: "+e.message}};
$("markProcedureReview").onclick=()=>{
 $("procedureReviewPanel").hidden=!$("procedureReviewPanel").hidden;
 if(!$("procedureReviewPanel").hidden){
  $("procedureApprovalChecked").checked=data.rules?.procedure?.approved===true;
  $("procedureClockChecked").checked=data.rules?.telemetry_clock_alignment_verified===true;
  $("procedureReviewer").value=data.rules?.procedure?.reviewer||"";
 }
};
$("saveProcedureReview").onclick=()=>{try{saveManualProcedureReview()}catch(e){$("procedureStatus").textContent="Review not saved: "+e.message}};
$("rulesFile").onchange=async e=>{
 try{const book=JSON.parse(await e.target.files[0].text());if(!book||!Array.isArray(book.rules))throw Error("Expected a rulebook object with rules array");
 data.rules=book;renderProcedureSteps();findings();describe();persist();msg("Loaded "+book.rules.length+" user-supplied procedure rules; approvals not authenticated.")
 }catch(err){msg("Procedure import rejected: "+err.message)}
};
$("seek").oninput=e=>{pausePlayback();idx=Number(e.target.value);renderCursor()};
$("zoomIn").onclick=()=>{if(!data.rows.length)return;const [a,b]=viewBounds(),span=Math.max(2,Math.floor((b-a)/2));setView(Math.max(0,idx-Math.floor(span/2)),Math.min(data.rows.length-1,idx+Math.ceil(span/2)))};
$("zoomOut").onclick=()=>{if(!data.rows.length)return;const [a,b]=viewBounds(),span=b-a+1;setView(Math.max(0,a-Math.ceil(span/2)),Math.min(data.rows.length-1,b+Math.ceil(span/2)))};
$("zoomReset").onclick=resetView;
$("start").onclick=()=>{pausePlayback();idx=0;renderCursor()};
$("prev").onclick=()=>{pausePlayback();idx--;renderCursor()};
$("next").onclick=()=>{pausePlayback();idx++;renderCursor()};
$("play").onclick=beginPlayback;
$("speed").onchange=()=>{if(timer!==null){playStartRecorded=Date.parse(data.rows[idx].t);playStartWall=performance.now();playbackStep()}};
$("newNote").onclick=()=>openNote(idx,idx);
$("rangeNote").onclick=()=>openNote($("noteFrom").value,$("noteTo").value);
$("cancelNote").onclick=()=>$("noteDialog").close();
$("noteForm").onsubmit=e=>{
 e.preventDefault();const i=$("editIndex").value,n={
  a:Number($("noteFrom").value),b:Number($("noteTo").value),
  title:$("noteTitle").value.trim(),body:$("noteBody").value.trim(),
  source:$("noteSource").value.trim(),kind:$("noteKind").value,
  alternative:$("noteAlternative").value.trim(),confidence:$("noteConfidence").value,
  disposition:$("noteDisposition").value,reviewer:$("noteReviewer").value.trim()};
 if(!n.title)return;
 if(i!=="")data.notes[Number(i)]=n;else data.notes.push(n);
 $("noteDialog").close();persist();notes();renderCursor();
};
$("downloadReport").onclick=()=>{loadState();$("reportText").value=report();filename(safe(data.id)+"_investigation.md",report(),"text/markdown")};
tab("import");describe();renderEvidence();renderProcedureSteps();renderEventClock();renderAssemblyTallies();renderAssemblyDisplay();
})();
