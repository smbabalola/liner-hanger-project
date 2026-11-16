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
const defaultCase=()=>({schema:"liner-mvp-case-1",id:"",well:"",source:"",rows:[],events:[],rules:null,notes:[],evidence:[],warnings:[],columns:[],case_kind:"imported"});
let data=defaultCase(),idx=0,timer=null,rangeStart=null,plotCanvases=[];
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
function importCSV(text,source){
  const table=csvRecords(text);if(table.length<2)throw Error("CSV needs a header and at least one timestamped row");
  const header=table[0].map(headerNorm),mapping={},found=[],warnings=[];
  for(const [key,options] of Object.entries(synonyms)){
    let matches=header.map((h,i)=>options.includes(h)?i:-1).filter(i=>i>=0);
    if(matches.length>1)warnings.push("Ambiguous "+key+" headers: first matching column used");
    if(matches.length){mapping[key]=matches[0];found.push(key)}
  }
  if(mapping.t===undefined)throw Error("CSV needs a timestamp column (t, timestamp or time)");
  const rows=[],invalid=[];let rawCount=0;
  table.slice(1).forEach((record,i)=>{
    rawCount++;
    let raw=record[mapping.t],ts=Date.parse(raw||"");
    if(!Number.isFinite(ts)){invalid.push("Invalid timestamp at CSV row "+(i+2));return}
    const sample={t:stamp(ts),source_row:i+2};
    for(const key of Object.keys(mapping)){if(key==="t")continue;
      const value=record[mapping[key]]??"";
      sample[key]=value.trim()===""?null:number(value.trim());
      if(value.trim()!==""&&sample[key]===null)warnings.push("Non-numeric "+key+" at row "+(i+2)+" excluded");
    }
    rows.push(sample);
  });
  if(invalid.length)throw Error(invalid.slice(0,4).join("; ")+"; correct timestamp/timezone errors before importing");
  for(let i=1;i<rows.length;i++)if(Date.parse(rows[i].t)<=Date.parse(rows[i-1].t))
    throw Error("CSV timestamps must be unique and strictly increasing (row "+rows[i].source_row+")");
  if(!rows.length)throw Error("CSV has no valid readings");
  if(!/[zZ]$|[+-]\d\d:\d\d$/.test(String(table[1][mapping.t]||"")))
    warnings.push("Timestamp timezone not specified: local-browser interpretation, verify before procedure comparisons");
  if(mapping.running_depth===undefined)warnings.push("No verified running-string depth; schematic movement is illustrative only");
  if(!Object.keys(mapping).some(x=>x==="spp"))warnings.push("Standpipe pressure channel unavailable");
  if(!Object.keys(mapping).some(x=>x==="hookload"))warnings.push("Hookload channel unavailable");
  if(!data.source)warnings.push("Telemetry source/clock provenance missing");
  data.rows=rows;data.columns=found;data.warnings=[...new Set(warnings)];data.source=source||data.source;
  return {records:rawCount,usable:rows.length,found};
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
function timestampAt(i){return data.rows[i]?.t||"unavailable"}
function renderEvidence(){
 const root=$("evidenceList");root.replaceChildren();
 const items=Array.isArray(data.evidence)?data.evidence:[];
 for(const item of items){
  const card=document.createElement("article");card.className="panel";card.style.margin="8px 0";card.style.padding="10px";
  const title=document.createElement("strong");title.textContent=item.source_id+" · "+item.kind.replaceAll("_"," ");card.append(title);
  const details=document.createElement("p");details.textContent=item.file_name+" · "+item.size_bytes+" bytes · "+item.review_status+
   " · SHA-256: "+(item.sha256||"unavailable");card.append(details);
  const note=document.createElement("p");note.className="sub";note.textContent="Original bytes not embedded. Keep the source file for independent review.";card.append(note);
  const remove=document.createElement("button");remove.type="button";remove.textContent="Remove from register";
  remove.onclick=()=>{data.evidence=data.evidence.filter(x=>x.source_id!==item.source_id);renderEvidence();describe();persist()};card.append(remove);
  root.append(card);
 }
 $("evidenceStatus").textContent=items.length+" source file(s) registered; originals must be retained separately.";
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
 let sha256=null;
 if(globalThis.crypto?.subtle?.digest){
  try{const digest=await crypto.subtle.digest("SHA-256",await file.arrayBuffer());
   sha256=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,"0")).join("");
  }catch(e){sha256=null}
 }
 data.evidence.push({source_id,kind,review_status,file_name:file.name,size_bytes:file.size,
  media_type:file.type||"unknown",last_modified_ms:file.lastModified,sha256,
  original_bytes_embedded:false,authentication:"caller_supplied_not_verified"});
 renderEvidence();describe();persist();
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
  const label=document.createElement("strong");label.textContent=name+" ("+unit+"; units must be independently confirmed)";
  const value=document.createElement("span");value.className="tag";value.style.float="right";box.append(label,value);
  const canvas=document.createElement("canvas");canvas.width=540;canvas.height=112;canvas.setAttribute("aria-label",name+" trend");box.append(canvas);root.append(box);
  const indexAt=e=>{const bounds=canvas.getBoundingClientRect();return Math.min(data.rows.length-1,
   Math.max(0,Math.round((e.clientX-bounds.left)/bounds.width*(data.rows.length-1))))};
  let pressed=null;
  canvas.addEventListener("pointerdown",e=>{pressed={index:indexAt(e),x:e.clientX};canvas.setPointerCapture(e.pointerId)});
  canvas.addEventListener("pointerup",e=>{
    if(!pressed)return;const a=pressed.index,b=indexAt(e),distance=Math.abs(e.clientX-pressed.x);
    pressed=null;
    if(distance>=12&&Math.abs(b-a)>=1){tab("notes");openNote(Math.min(a,b),Math.max(a,b));return}
    idx=b;renderCursor();
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
  const vals=data.rows.map(r=>r[key]);const valid=vals.filter(Number.isFinite);
  value.textContent=fmt(current()?.[key]);if(!valid.length)continue;
  let lo=Math.min(...valid),hi=Math.max(...valid);if(lo===hi){lo-=1;hi+=1}
  ctx.strokeStyle="#79cbea";ctx.lineWidth=1.5;ctx.beginPath();let connected=false;
  vals.forEach((v,i)=>{if(!Number.isFinite(v)){connected=false;return}
   const x=i*w/Math.max(1,vals.length-1),y=(h-18)-(v-lo)/(hi-lo)*(h-27);
   if(connected)ctx.lineTo(x,y);else ctx.moveTo(x,y);connected=true;
  });ctx.stroke();
  for(const m of data.notes){const a=m.a*w/Math.max(1,vals.length-1),b=m.b*w/Math.max(1,vals.length-1);ctx.fillStyle="rgba(255,195,126,.17)";ctx.fillRect(a,0,Math.max(2,b-a),h-15)}
  ctx.strokeStyle="#ffcb90";ctx.beginPath();ctx.moveTo(idx*w/Math.max(1,vals.length-1),0);ctx.lineTo(idx*w/Math.max(1,vals.length-1),h-12);ctx.stroke();
 }
}
function assembly(){
 const sample=current();const svg=$("moving"),label=$("assemblyStatus");
 if(!sample){svg.setAttribute("transform","translate(0 0)");label.textContent="No case loaded";return}
 let verified=Number.isFinite(sample.running_depth),depth=sample.running_depth;
 if(verified){
  const valid=data.rows.map(r=>r.running_depth).filter(Number.isFinite),min=Math.min(...valid),max=Math.max(...valid);
  const y=40+(max>min?(depth-min)/(max-min)*35:0);
  svg.setAttribute("transform","translate(0 "+y+")");
  label.textContent="Running-depth-sourced movement at "+fmt(depth)+" m MD. Assembly geometry remains schematic, not to scale.";
 }else{
  svg.setAttribute("transform","translate(0 0)");
  label.textContent="No verified running-string depth. Assembly is a stationary schematic; hole/bit depth cannot establish liner-hanger position.";
 }
}
function renderCursor(){
 if(!data.rows.length)return;
 idx=Math.max(0,Math.min(data.rows.length-1,idx));$("seek").max=data.rows.length-1;$("seek").value=idx;
 $("cursorTime").textContent=timestampAt(idx)+" · sample "+(idx+1)+"/"+data.rows.length;
 $("noteFrom").max=$("noteTo").max=data.rows.length-1;
 $("cursorValues").textContent=channels.filter(x=>data.columns.includes(x[0])).map(x=>x[1]+": "+fmt(current()[x[0]])+" "+x[2]).join("  ·  ");
 drawCharts();assembly();
 document.querySelectorAll("#timeline button").forEach(b=>b.classList.toggle("active",Number(b.dataset.sample)===idx));
}
function nearest(t){if(!data.rows.length)return 0;let closest=0,best=Infinity;
 data.rows.forEach((r,i)=>{const d=Math.abs(Date.parse(r.t)-Date.parse(t));if(d<best){best=d;closest=i}});return closest}
function renderEvents(){
 const root=$("timeline");root.replaceChildren();
 if(!data.events.length){root.textContent="No job chronology supplied.";return}
 for(const event of data.events){
  const button=document.createElement("button");button.type="button";
  const index=Number.isFinite(Date.parse(event.time))?nearest(event.time):null;
  button.dataset.sample=index??-1;
  button.textContent=(event.time||"Time not verified")+" · "+(event.label||event.description||"Reported event")+
    " — source: "+(event.source||"not supplied");
  button.onclick=()=>{if(index!==null){idx=index;renderCursor()}};
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
  if(!book.channel_units?.[rule.channel]||book.channel_units[rule.channel]!==rule.unit)
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
   if(!approved||!aligned||requiredStep.approved!==true||!entry.source)
    entry.reasons.push("Approved source/clock alignment or step reference not established");
   if(!id||typeof id!=="string")entry.reasons.push("Required event code missing");
   const matching=data.events.filter(e=>e.code===id);
   if(!matching.length)entry.reasons.push("Required step not found in supplied chronology; absence does not prove omission");
   if(matching.length>1)entry.reasons.push("Duplicate reported step events; exact sequence requires engineer review");
   if(matching.length===1){
    const t=Date.parse(matching[0].time||"");
    if(!Number.isFinite(t)||!matching[0].source)entry.reasons.push("Reported event time or source not verified");
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
   x.onclick=()=>{idx=nearest(instance.start);tab("replay");renderCursor()};box.append(x)}
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
  const body=document.createElement("p");body.textContent=n.body;block.append(body);
  const edit=document.createElement("button");edit.textContent="Edit";edit.onclick=()=>openNote(n.a,n.b,i);block.append(edit);
  const jump=document.createElement("button");jump.textContent="Go to range";jump.onclick=()=>{idx=n.a;tab("replay");renderCursor()};block.append(jump);
  root.append(block);
 }
}
function openNote(a,b,edit=null){
 if(!data.rows.length){msg("Load telemetry before creating time-specific annotations");tab("import");return}
 a=Math.max(0,Math.min(data.rows.length-1,Number(a)||0));b=Math.max(a,Math.min(data.rows.length-1,Number(b)||a));
 $("noteFrom").value=a;$("noteTo").value=b;$("editIndex").value=edit===null?"":String(edit);
 const n=edit===null?null:data.notes[edit];$("noteTitle").value=n?.title||"";$("noteBody").value=n?.body||"";
 $("noteKind").value=n?.kind||"observation";$("noteSource").value=n?.source||"";
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
 "First timestamp: "+(data.rows[0]?.t||"unavailable"),
 "Last timestamp: "+(data.rows[data.rows.length-1]?.t||"unavailable"),
 ...data.warnings.map(w=>"- Evidence gap: "+w),
 "",
 "## Chronological reported events",
 ...data.events.map(e=>"- "+(e.time||"Time unverified")+" — "+(e.label||e.description||"Event")+" [source: "+(e.source||"not supplied")+"]"),
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
  "\n  - "+(n.body||"No explanation recorded")+"\n  - Source: "+(n.source||"not supplied"));
 lines.push("","## Competing explanations / unknowns",
 "Surface signals and procedure flags alone cannot confirm hanger actuation or internal failure.",
 "Possible alternative mechanisms must be reviewed against job-specific OEM documents and independent rig reports.",
 "Missing readings, unverifiable clock alignment and unreviewed rulebook declarations remain unresolved.",
 "","## Human review","Reviewer: not assigned.","Engineering approval: NOT COMPLETED.",
 "","_Offline engineering demonstration only. No live operating instructions or OEM setpoints are provided._");
 return lines.join("\n")+"\n";
}
function tab(name){
 document.querySelectorAll(".tab").forEach(x=>x.hidden=x.id!==name);
 document.querySelectorAll("[data-tab]").forEach(x=>x.classList.toggle("active",x.dataset.tab===name));
 if(name==="replay")renderCursor();if(name==="deviations")findings();if(name==="notes")notes();if(name==="report")$("reportText").value=report();
}
function loadData(next){
 if(timer){clearInterval(timer);timer=null;$("play").textContent="▶ Play"}
 validateCase(next);idx=0;toFields();describe();renderEvidence();renderCharts();renderEvents();findings();notes();renderCursor();persist();
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
$("normal").onclick=()=>{loadData(demo(false));tab("replay")};
$("anomalous").onclick=()=>{loadData(demo(true));tab("replay")};
$("restore").onclick=()=>{try{const value=localStorage.getItem("liner_mvp_case_v1");if(!value)throw Error("No saved local case");loadData(JSON.parse(value))}catch(e){msg(e.message)}};
$("saveCase").onclick=()=>{loadState();msg(persist()?"Saved case in this browser. Export JSON for portable backup.":"Browser storage unavailable; export JSON for backup.")};
$("exportCase").onclick=$("downloadCase").onclick=()=>{loadState();filename(safe(data.id)+".json",JSON.stringify(data,null,2))};
$("caseFile").onchange=async e=>{try{loadData(JSON.parse(await e.target.files[0].text()));tab("replay")}catch(err){msg("Case import rejected: "+err.message)}};
$("telemetryFile").onchange=async e=>{
 try{loadState();const result=importCSV(await e.target.files[0].text(),data.source||e.target.files[0].name);
   data.events=[];data.rules=null;data.notes=[];idx=0;describe();renderCharts();renderEvents();findings();notes();renderCursor();persist();
   msg("Imported "+result.usable+" of "+result.records+" readings; review diagnostics before procedure comparison.");
 }catch(err){msg("CSV import rejected: "+err.message)}
};
$("addEvent").onclick=()=>{
 const label=$("eventLabel").value.trim(),source=$("eventSource").value.trim(),raw=$("eventTime").value.trim();
 if(!label||!source){$("eventStatus").textContent="Action and report/page source reference are both required.";return}
 if(raw&&!(/(?:Z|[+-]\d{2}:\d{2})$/i.test(raw))){$("eventStatus").textContent="Use a timestamp with explicit UTC Z or timezone offset, or leave time unknown.";return}
 const time=raw?Date.parse(raw):NaN;
 if(raw&&!Number.isFinite(time)){$("eventStatus").textContent="Invalid reported timestamp; nothing added.";return}
 const event={time:raw?new Date(time).toISOString():null,label,source,
   time_status:raw?"reported_unverified":"unknown",
   evidence_class:"reported_not_measured"};
 data.events.push(event);
 renderEvents();describe();persist();
 $("eventLabel").value="";$("eventTime").value="";
 $("eventStatus").textContent="Reported event registered. Time and event are source assertions, not verified downhole actions.";
};
$("eventsFile").onchange=async e=>{
 try{const events=JSON.parse(await e.target.files[0].text());if(!Array.isArray(events)||events.some(x=>typeof x!=="object"||x===null))
   throw Error("Expected JSON array of {time,label,source} events");
 data.events=events;renderEvents();describe();persist();msg("Loaded "+events.length+" reported events; times are source assertions.")
 }catch(err){msg("Event import rejected: "+err.message)}
};
$("rulesFile").onchange=async e=>{
 try{const book=JSON.parse(await e.target.files[0].text());if(!book||!Array.isArray(book.rules))throw Error("Expected a rulebook object with rules array");
 data.rules=book;findings();describe();persist();msg("Loaded "+book.rules.length+" user-supplied procedure rules; approvals not authenticated.")
 }catch(err){msg("Procedure import rejected: "+err.message)}
};
$("seek").oninput=e=>{idx=Number(e.target.value);renderCursor()};
$("start").onclick=()=>{idx=0;renderCursor()};
$("prev").onclick=()=>{idx--;renderCursor()};
$("next").onclick=()=>{idx++;renderCursor()};
$("play").onclick=()=>{
 if(timer){clearInterval(timer);timer=null;$("play").textContent="▶ Play";return}
 if(!data.rows.length){tab("import");msg("Load a case before replay");return}
 $("play").textContent="Ⅱ Pause";timer=setInterval(()=>{
  idx+=Number($("speed").value)||1;if(idx>=data.rows.length-1){idx=data.rows.length-1;clearInterval(timer);timer=null;$("play").textContent="▶ Play"}
  renderCursor();
 },220)
};
$("newNote").onclick=()=>openNote(idx,idx);
$("rangeNote").onclick=()=>openNote($("noteFrom").value,$("noteTo").value);
$("cancelNote").onclick=()=>$("noteDialog").close();
$("noteForm").onsubmit=e=>{
 e.preventDefault();const i=$("editIndex").value,n={
  a:Number($("noteFrom").value),b:Number($("noteTo").value),
  title:$("noteTitle").value.trim(),body:$("noteBody").value.trim(),
  source:$("noteSource").value.trim(),kind:$("noteKind").value};
 if(!n.title)return;
 if(i!=="")data.notes[Number(i)]=n;else data.notes.push(n);
 $("noteDialog").close();persist();notes();renderCursor();
};
$("downloadReport").onclick=()=>{loadState();$("reportText").value=report();filename(safe(data.id)+"_investigation.md",report(),"text/markdown")};
tab("import");describe();renderEvidence();
})();
