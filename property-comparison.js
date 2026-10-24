/* Compare reported facts without merging identities or allocating group totals. */
window.PropertyComparison=(()=>{
 const text=v=>typeof v==='string'?v:typeof v==='number'?String(v):'';
 const e=v=>text(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const number=v=>v===null||v===undefined||typeof v==='boolean'||typeof v==='string'&&!v.trim()||!Number.isFinite(Number(v))?null:Number(v);
 const url=v=>{try{const u=new URL(text(v));return u.protocol==='https:'?u.href:null;}catch(_){return null;}};
 function build(r){
  if(!r||typeof r.id!=='string'||!r.id)throw Error('A source record is required');
  const certs=Array.isArray(r.certificates)?r.certificates:[];
  const observations=certs.slice(0,1000).map(c=>({certificate_id:text(c.id),submitted:text(c.submitted)||null,reported_floor:text(c.floor)||null,reported_interiors:Array.isArray(c.interiors)?c.interiors.map(text):[],heated_area_m2:number(c.heated_area_m2),reported_object_scope:text(c.object_scope)||null,source_url:url(c.source_url)}));
  const sources=[url(r.source_url),url(r.source),...observations.map(o=>o.source_url),...(Array.isArray(r.municipal_refs)?r.municipal_refs.map(v=>url(v.source)):[])].filter(Boolean);
  return {id:r.id,title:text(r.title),kind:text(r.kind),reported_scope:text(r.scope)||null,reported_address:text(r.address)||(['entrance','civic'].includes(r.kind)?text(r.title):null),reported_members:Array.isArray(r.members)?r.members.filter(Array.isArray).map(m=>m.map(text)):[],source_table:text(r.source_table)||null,source_date:text(r.source_snapshot||r.source_timestamp||r.source_updated)||null,reported_height_m:number(r.reported_height_m),reported_building_floors:text(r.floor_raw)||null,geometry_type:text(r.geometry?.type)||null,observation_count:certs.length,observations,observations_truncated:certs.length>1000,source_urls:[...new Set(sources)],current_access_verified:false};
 }
 function report(a,b){return {schema:'torino-source-comparison-v1',record_count:2,records:[build(a),build(b)],interpretation:{identity_equivalence_confirmed:false,current_legal_access_confirmed:false,group_totals_split:false,notes:'Reported source observations only. Different dates, scopes or geometry do not establish a cadastral change. Heated areas belong to each attested object; no per-subalterno split is inferred.'}};}
 // Equality is literal source-value equality, never property equivalence.
 const fields=['kind','id','reported_scope','reported_members','reported_address','source_date','observation_count','reported_floor','reported_interiors','heated_area_m2','reported_object_scope','reported_height_m','reported_building_floors','geometry_type','source_urls'];
 const observed=new Set(['reported_floor','reported_interiors','heated_area_m2','reported_object_scope']);
 const absent=v=>v===null||v===undefined||v===''||Array.isArray(v)&&(!v.length||v.some(absent));
 function assess(a,b){
  return fields.map(field=>{
   const values=r=>observed.has(field)?r.observations.map(o=>o[field]):r[field];
   const left=values(a),right=values(b);
   // A blank cadastral section remains unreported, even when other members exist.
   const missing=absent(left)||absent(right)||observed.has(field)&&(a.observations_truncated||b.observations_truncated);
   const canonical=v=>Array.isArray(v)?v.map(canonical).sort():v;
   return {field,status:missing?'incomplete':JSON.stringify(canonical(left))===JSON.stringify(canonical(right))?'same':'different'};
  });
 }
 function bind(container){
  const filter=container.querySelector('[data-comparison-filter]');
  if(!filter)return;
  filter.onchange=()=>{let count=0;container.querySelectorAll('tr[data-comparison-status]').forEach(row=>{row.hidden=filter.value!=='all'&&row.dataset.comparisonStatus!==filter.value;if(!row.hidden)count++;});container.querySelector('[data-comparison-visible]').textContent=String(count);};
 }
 function render(a,b,lang='en'){
  const t=(it,en)=>lang==='it'?it:en,unknown=t('Non riportato / sconosciuto','Not reported / unknown');
  const kinds={property:t('Immobile / gruppo','Property / group'),parcel:t('Particella','Parcel'),entrance:t('Civico','Civic'),civic:t('Civico','Civic'),building:t('Edificio','Building'),volume:t('Parte volumetrica','Volumetric part'),site:t('Complesso','Complex')};
  const scope=v=>({cadastral_property:t('Identità catastale riportata','Reported cadastral identity'),group:t('Gruppo attestato','Attested group'),whole_building:t('Intero edificio attestato','Attested whole building'),reported_cadastral_reference:t('Riferimento da inventario','Inventory reference')})[v]||v||unknown;
  const list=rows=>rows.length?rows.map(v=>`<div>${e(v)}</div>`).join(''):`<span class="comparison-unknown">${unknown}</span>`;
  const observation=(r,field,format=v=>e(v))=>{const rows=r.observations.slice(0,12);return rows.length?rows.map(o=>`<article><small>${e(o.certificate_id)} · ${e(o.submitted?.slice(0,10)||unknown)}</small><div>${o[field]===null||Array.isArray(o[field])&&!o[field].length?`<span class="comparison-unknown">${unknown}</span>`:format(o[field])}</div></article>`).join('')+(r.observation_count>12?`<small>${t('Prime 12 osservazioni; esporta il JSON per il dettaglio acquisito.','First 12 observations; export JSON for the acquired detail.')}</small>`:''):`<span class="comparison-unknown">${unknown}</span>`;};
  const rows=[
   [t('Tipo di oggetto','Object type'),r=>e(kinds[r.kind]||r.kind)],
   [t('Chiave di fonte','Source key'),r=>`<code>${e(r.id)}</code>`],
   [t('Ambito riportato','Reported scope'),r=>e(scope(r.reported_scope))],
   [t('Identificativi riportati','Reported cadastral identities'),r=>list(r.reported_members.map(m=>m.join(' / ')))],
   [t('Indirizzo riportato','Reported address'),r=>e(r.reported_address||unknown)],
   [t('Data della fonte','Source date'),r=>e(r.source_date||unknown)],
   [t('Osservazioni acquisite','Acquired certificate observations'),r=>e(r.observation_count)],
   [t('Piano dichiarato · per certificato','Reported property floor · per certificate'),r=>observation(r,'reported_floor')],
   [t('Interni dichiarati · per certificato','Reported interiors · per certificate'),r=>observation(r,'reported_interiors',v=>e(v.join(', ')))],
   [t('Superficie riscaldata dell’oggetto attestato · m²','Heated area of each attested object · m²'),r=>observation(r,'heated_area_m2',v=>e(v)+' m²')],
   [t('Ambito originale · per certificato','Original scope · per certificate'),r=>observation(r,'reported_object_scope')],
   [t('Altezza di fonte · m','Reported source height · m'),r=>r.reported_height_m===null?unknown:e(r.reported_height_m)],
   [t('Piani dell’edificio · valore originale','Building floors · original value'),r=>e(r.reported_building_floors||unknown)],
   [t('Tipo di geometria acquisita','Acquired geometry type'),r=>e(r.geometry_type||unknown)],
   [t('Fonti originali','Original sources'),r=>r.source_urls.slice(0,10).map((u,i)=>`<a href="${e(u)}" target="_blank" rel="noopener">${t('Fonte','Source')} ${i+1} ↗</a>`).join(' · ')||unknown]
  ];
  const assessment=assess(a,b),counts=Object.fromEntries(['different','same','incomplete'].map(k=>[k,assessment.filter(v=>v.status===k).length]));
  const statusLabel={different:t('Valori diversi','Different values'),same:t('Valori uguali','Same values'),incomplete:t('Dati incompleti','Incomplete data')};
  const dates=r=>[...new Set(r.observations.map(o=>o.submitted?.slice(0,10)).filter(v=>/^\d{4}-\d{2}-\d{2}$/.test(v)))].sort();
  const period=r=>{const d=dates(r);return d.length?e(d[0])+(d.length>1?' → '+e(d.at(-1)):''):unknown;};
  const overview=`<section class="comparison-overview" aria-label="${t('Lettura rapida','At a glance')}"><div class="comparison-counts">${['different','same','incomplete'].map(k=>`<div class="comparison-count ${k}"><b>${counts[k]}</b><span>${statusLabel[k]}</span></div>`).join('')}</div><p>${t('Confronto letterale dei valori riportati; non una misura di accuratezza. Date e certificati restano separati.','Literal comparison of reported values; not an accuracy measure. Dates and certificates remain separate.')}</p><div class="comparison-period"><span>${t('Date certificati · riferimento','Certificate dates · reference')}: <b>${period(a)}</b></span><span>${t('Date certificati · selezione','Certificate dates · selection')}: <b>${period(b)}</b></span></div><label>${t('Mostra campi','Show fields')} <select data-comparison-filter><option value="all">${t('Tutti','All')}</option>${['different','incomplete','same'].map(k=>`<option value="${k}">${statusLabel[k]}</option>`).join('')}</select></label><small role="status"><span data-comparison-visible>${rows.length}</span> / ${rows.length} ${t('campi visibili','fields visible')}</small></section>`;
  return `<p class="comparison-scope-note">${t('Confronto di osservazioni, non equivalenza catastale o accesso attuale. Superfici di gruppi o interi edifici non sono divise tra i subalterni. Una sezione vuota non è riportata dalla fonte.','Comparison of observations, not cadastral equivalence or current access. Group or whole-building areas are not divided among subalterni. A blank section is unreported by the source.')}</p>${overview}<div class="comparison-table-wrap"><table><thead><tr><th>${t('Campo','Field')}</th><th><small>${t('Riferimento','Reference')}</small>${e(a.title||a.id)}</th><th><small>${t('Selezione','Selection')}</small>${e(b.title||b.id)}</th></tr></thead><tbody>${rows.map(([name,value],i)=>`<tr data-comparison-status="${assessment[i].status}"><th scope="row">${name}<span class="comparison-status ${assessment[i].status}">${statusLabel[assessment[i].status]}</span></th><td>${value(a)}</td><td>${value(b)}</td></tr>`).join('')}</tbody></table></div><p class="comparison-footer-note">${t('Geometrie, recensioni locali e note non sono incluse nell’esportazione. Nessuna posizione individuale dell’appartamento o ingresso legale è confermato.','Geometry, local reviews and notes are excluded from export. No individual apartment position or legal entrance is confirmed.')}</p>`;
 }
 return {build,report,render,assess,bind};
})();
