/* Local v2 property evidence and relationship review. No company measurements. */
"use strict";
window.PropertyRegistry = (() => {
  const state = {summary:null,addresses:null,investigation:null,investigationSummary:null,review:null,reviewSummary:null,legacy:false,parcel:null,property:null,sequence:0,api:false,filters:{query:"",kind:"all",entrance:null}};
  const local = ["localhost","127.0.0.1"].includes(location.hostname);
  const api = "http://127.0.0.1:8766";
  const label = (it,en) => tr(it,en);
  const fmt = (x,d=0) => number(x,d);
  const safe = x => esc(x == null ? "—" : String(x));
  const kinds = {
    cadastral_property:["Immobile catastale","Cadastral property"],
    whole_building:["Intero edificio attestato","Whole-building attestation"],
    group:["Gruppo attestato","Attested group"]
  };
  const flagLabels = {
    conflicting_reported_interiors:["Interni riportati discordanti: verificare le date e gli oggetti", "Conflicting reported interiors: check dates and attested objects"],
    missing_subalterno_or_identity:["Identità catastale incompleta","Incomplete cadastral identity"],
    multiple_eligible_certificates_review_renewals:["Più APE ammissibili: verificare rinnovi","Multiple eligible APEs: review renewals"],
    overlapping_cadastral_memberships:["Identificatori condivisi con altri gruppi","Identifiers overlap other attested groups"],
    cadastral_section_alias_requires_review:["Sezioni catastali discordanti o non indicate","Conflicting or unreported cadastral sections"],
    entrance_match_unresolved:["Ingresso ancora da collegare","Entrance link unresolved"]
  };
  const translate = pair => label(...pair);
  async function json(url,options={}) {
    const response=await fetch(url,{cache:"no-store",...options});
    if(!response.ok)throw Error(`HTTP ${response.status}`);
    return response.json();
  }
  async function parcelData(fp) {
    if(local){
      try {const data=await json(`${api}/api/parcel/${fp}`,{signal:AbortSignal.timeout(3000)});state.api=true;return data;}
      catch(_){state.api=false;}
    }
    return json(`data/registry/parcels/${fp}.json`);
  }
  async function render(el) {
    if(window.PropertyWorkbench&&!state.legacy){
      try{
        return await PropertyWorkbench.render(el,state.parcel||selected||'1175/434',{
          advanced:fp=>{state.parcel=fp;state.legacy=true;render(el);},
          context:(fp,id)=>{state.parcel=fp;state.property=id;},
          map:fp=>{state.parcel=fp;setTab('map');if(lotByFp.has(fp))selectLot(fp,null,{fit:true});},
          entrance:(id,fp)=>{const e=entById.get(String(id));if(e){state.parcel=fp;setTab('map');selectLot(fp,e.id,{fit:true});openStreet(e);}}
        });
      }catch(error){el.classList.remove('property-workbench-host');}
    }
    el.classList.remove('property-workbench-host');
    const sequence=++state.sequence;
    el.innerHTML=`<div class="empty">${label("Caricamento registro…","Loading property register…")}</div>`;
    try {
      state.summary ||= await json("data/registry/summary.json");
      const summary=state.summary;
      const fp=state.parcel || selected || summary.parcels.find(p=>p.properties)?.parcel;
      const data=await parcelData(fp);
      state.addresses=data.address_evidence||null;
      if(local){
        try {state.addresses=await json(api+"/api/address-evidence/"+fp,{signal:AbortSignal.timeout(3000)});}catch(_){}
      }
      state.investigation=null;
      if(local){
        try {
          const [details,summary]=await Promise.all([json(api+'/api/investigation/'+fp),state.investigationSummary||json(api+'/api/investigation')]);
          state.investigation=details;state.investigationSummary=summary;
        }catch(_){}
      }
      if(!state.investigation){
        try {
          const [details,investigationSummary]=await Promise.all([json('data/investigation/parcels/'+fp+'.json'),state.investigationSummary||json('data/investigation/summary.json')]);
          state.investigation=details;state.investigationSummary=investigationSummary;
        }catch(_){}
      }
      state.review=null;
      if(local){
        try{
          const [details,reviewSummary]=await Promise.all([json(api+'/api/property-review/'+fp,{signal:AbortSignal.timeout(5000)}),state.reviewSummary||json(api+'/api/property-review',{signal:AbortSignal.timeout(5000)})]);
          state.review=details;state.reviewSummary=reviewSummary;
        }catch(_){}
      }
      if(sequence!==state.sequence)return;
      state.parcel=fp;
      if(!data.properties.some(p=>p.id===state.property))state.property=data.properties[0]?.id || null;
      draw(el,summary,data);
    } catch(error){
      if(sequence!==state.sequence)return;
      el.innerHTML=`<h1>${label("Registro immobili","Property register")}</h1><p class="context-note">${label("Il registro locale non è disponibile.","The local register is unavailable.")} ${safe(error.message)}</p>`;
    }
  }
  function draw(el,summary,data) {
    const onDate=new Date().toLocaleDateString('en-CA',{timeZone:'Europe/Rome'});
    const identityIndex=IdentityEvidence.index(data,onDate);
    const visibleProperties=IdentityEvidence.filter(data,identityIndex,state.filters);
    if(!visibleProperties.some(p=>p.id===state.property))state.property=visibleProperties[0]?.id||null;
    const p=data.properties.find(x=>x.id===state.property);
    const c=p && data.certificates.find(x=>x.id===p.latest_certificate);
    const count=summary.counts;
    el.innerHTML=`<div class="registry-heading"><div><div class="eyebrow">${label("VERSIONE 2 · EVIDENZE PUBBLICHE","VERSION 2 · PUBLIC EVIDENCE")}</div><h1>${label("Registro immobili e collegamenti","Property register & relationships")}</h1></div><button type="button" class="btn outline" id="registryMap">${label("Torna alla mappa","Back to map")}</button></div>
      <p class="page-lead">${label("Immobile, attestato e appartamento non sono conteggi equivalenti. I collegamenti proposti restano da verificare.","A property, certificate and apartment are different counts. Proposed links remain subject to review.")}</p>
      <div class="summary-strip registry-counts"><div><b>${fmt(count.properties)}</b><small>${label("identità immobiliari / gruppi","property / group identities")}</small></div><div><b>${fmt(count.certificates)}</b><small>${label("record APE dopo riconciliazione","certificate records after matching")}</small></div><div><b>${fmt(count.parcels_with_evidence)} / ${fmt(count.parcels)}</b><small>${label("lotti con evidenze APE","parcels with APE evidence")}</small></div><div><b>${fmt(count.street_queries_capped)}</b><small>${label("ricerche con possibile limite 500","searches possibly capped at 500")}</small></div></div>
      <div class="registry-toolbar"><label for="registrySearch">${label("Lotto o indirizzo","Parcel or address")}</label><input id="registrySearch" type="search" placeholder="1175/434 · Cordero" autocomplete="off"><select id="registryParcel" aria-label="${label("Lotto nel registro","Registry parcel")}"></select><button type="button" class="btn outline" id="registryExport">${label("Esporta evidenze del lotto","Export parcel evidence")}</button><small id="registryMatches"></small></div>
      <div class="registry-source-note">${summary.bulk_source?`${label("File regionale acquisito integralmente", "Published regional file acquired in full")}: ${fmt(summary.bulk_source.rows_read)} ${label("righe lette; selezione per chiavi catastali. Ultimo invio Torino nel file", "rows read; selection by cadastral keys. Latest Torino submission in file")}: ${safe(summary.bulk_source.latest_torino_submission)}.`:label("Acquisizione tabella regionale ancora in corso. Il registro usa al momento le ricerche pubbliche disponibili.","Regional table acquisition is still running. This register currently uses the available public searches.")} ${label("Data di riferimento","Reference date")}: ${safe(summary.as_of)}. ${state.api?label("Revisioni salvate nel database locale.","Reviews saved in the local database."):label("Revisione non disponibile: sola lettura.","Review service unavailable: read-only.")}</div>
      <section id="parcelIdentityDossier" class="registry-dossier"></section><div class="registry-layout"><aside class="registry-list"><h2>${safe(data.parcel)} · ${fmt(visibleProperties.length)} / ${fmt(data.properties.length)} ${label("immobili / gruppi","properties / groups")}</h2>${visibleProperties.length?visibleProperties.map(x=>`<button type="button" class="registry-property ${x.id===state.property?"selected":""}" data-property="${safe(x.id)}" aria-pressed="${x.id===state.property}"><strong>${label("Subalterni","Subalterni")} ${x.members.map(m=>safe(m[4]||label("non indicato","not reported"))).join(" + ")}</strong><span>${safe(x.address)} ${safe(x.civic||"")}</span><small>${label("Piano","Floor")} ${safe(x.floor)} · ${fmt(x.heated_area_m2,2)} m² · ${x.certificates.length} APE</small>${x.flags.length?`<em>${x.flags.length} ${label("verifiche aperte","open checks")}</em>`:""}</button>`).join(""):`<p class="empty">${label("Nessun immobile corrisponde ai filtri, oppure nessuna evidenza acquisita. Ciò non dimostra l'assenza di appartamenti.","No property matches the filters, or no evidence has been acquired. This does not establish an absence of apartments.")}</p>`}</aside>
      <section class="registry-detail">${p?propertyHtml(p,c,data):`<h2>${label("Copertura mancante","Missing coverage")}</h2><p>${label("Seleziona un lotto con evidenze o verifica la fonte.","Select a parcel with evidence or check the source.")}</p>`}</section></div>
      ${data.unresolved_certificates?.length?`<details class="registry-warning"><summary>${data.unresolved_certificates.length} ${label("APE non collegati: comune catastale assente","unlinked APEs: cadastral municipality absent")}</summary><p>${label("Questi record non sono attribuiti automaticamente a Torino e non entrano nel conteggio degli immobili.","These records are not automatically assigned to Torino and are excluded from property counts.")}</p><ul>${data.unresolved_certificates.map(x=>`<li>${safe(x.public_code)} · ${safe(x.address)} ${safe(x.civic)}</li>`).join('')}</ul></details>`:''}
      <section class="registry-roofs" id="registryRoofs"></section>`;
    const select=el.querySelector("#registryParcel");
    if(local&&window.PropertyWorkbench){const back=document.createElement('button');back.type='button';back.className='btn outline';back.textContent=label('Torna allo spazio immobili','Back to property workspace');back.onclick=()=>{state.legacy=false;render(el);};el.querySelector('.registry-heading').append(back);}
    const sourceDownload=document.createElement('a');sourceDownload.className='btn outline';sourceDownload.href='data/download/torino_property_registry_v2.zip';sourceDownload.download='torino_property_registry_v2.zip';sourceDownload.textContent=label('Scarica registro fonti (CSV)','Download source register (CSV)');el.querySelector('.registry-toolbar').append(sourceDownload);
    const acquisition=document.createElement('p');acquisition.className='hint';
    acquisition.textContent=label(`Dettagli acquisiti: ${fmt(count.properties_with_reported_interior||0)} identità con interno riportato; ${fmt(count.targeted_parcel_queries||0)} ricerche catastali mirate. I limiti delle ricerche per via restano visibili.`,`Acquired detail: ${fmt(count.properties_with_reported_interior||0)} identities with a reported interior; ${fmt(count.targeted_parcel_queries||0)} targeted cadastral searches. Street-search cap warnings remain visible.`);
    el.querySelector('.registry-source-note').append(acquisition);
    if(count.targeted_parcel_search_total){const progress=document.createElement('p');progress.className='hint';progress.textContent=label(`Ricerche catastali mirate: ${fmt(count.targeted_parcel_queries)} / ${fmt(count.targeted_parcel_search_total)} tentate; ${fmt(count.targeted_parcel_queries_error||0)} errori, ${fmt(count.targeted_parcel_queries_capped||0)} risposte al limite, ${fmt(count.targeted_parcel_queries_empty||0)} risposte vuote. Una risposta vuota o sotto il limite non dimostra completezza.`,`Targeted cadastral searches: ${fmt(count.targeted_parcel_queries)} / ${fmt(count.targeted_parcel_search_total)} attempted; ${fmt(count.targeted_parcel_queries_error||0)} errors, ${fmt(count.targeted_parcel_queries_capped||0)} capped responses, ${fmt(count.targeted_parcel_queries_empty||0)} empty responses. Empty or below-cap responses do not establish completeness.`);el.querySelector('.registry-source-note').append(progress);}
    function options(query="") {
      const q=query.trim().toLocaleLowerCase();
      const matches=summary.parcels.filter(x=>x.parcel===state.parcel||!q||`${x.parcel} ${x.addresses.join(" ")}`.toLocaleLowerCase().includes(q));
      const current=matches.find(x=>x.parcel===state.parcel);
      const visible=[...(current?[current]:[]),...matches.filter(x=>x!==current).slice(0,199)];
      select.innerHTML=visible.map(x=>`<option value="${safe(x.parcel)}" ${x.parcel===state.parcel?"selected":""}>${safe(x.parcel)} · ${x.properties} ${label("immobili","properties")} · ${safe(x.addresses[0]||"")}</option>`).join("");
      el.querySelector('#registryMatches').textContent=matches.length>visible.length?label(`Mostrati ${visible.length} di ${matches.length} risultati: affina la ricerca.`,`Showing ${visible.length} of ${matches.length} matches: refine the search.`):label(`${matches.length} risultati`,`${matches.length} matches`);
    }
    options();
    el.querySelector("#registrySearch").oninput=e=>options(e.target.value);
    select.onchange=()=>{state.parcel=select.value;state.property=null;state.filters={query:"",kind:"all",entrance:null};render(el);};
    el.querySelector("#registryMap").onclick=()=>{setTab("map");if(lotByFp.has(state.parcel))selectLot(state.parcel,null,{fit:true});};
    el.querySelector("#registryExport").onclick=()=>downloadJSON(data,`property-evidence-${state.parcel.replace("/","-")}.json`);
    el.querySelectorAll("[data-property]").forEach(button=>button.onclick=()=>{state.property=button.dataset.property;draw(el,summary,data);});
    el.querySelectorAll('[data-alias-property]').forEach(button=>button.onclick=()=>{state.property=button.dataset.aliasProperty;draw(el,summary,data);});
    el.querySelectorAll("[data-entrance],[data-review-entrance]").forEach(button=>button.onclick=()=>{const e=entById.get(button.dataset.entrance||button.dataset.reviewEntrance);if(!e)return;setTab("map");selectLot(state.parcel,e.id,{fit:true});openStreet(e);});
    el.querySelectorAll("[data-review]").forEach(button=>button.onclick=async()=>{
      button.disabled=true;
      try {
        const box=button.closest(".registry-link");
        await json(api+"/api/review",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({relationship_id:button.dataset.review,decision:button.dataset.decision,note:box.querySelector('[data-review-note]').value,valid_from:box.querySelector('[data-valid-from]').value||null,valid_to:box.querySelector('[data-valid-to]').value||null})});
        await render(el);
      }catch(error){toast(label("Revisione non salvata: ","Review not saved: ")+error.message,true);button.disabled=false;}
    });
    ParcelIdentity.render(el.querySelector('#parcelIdentityDossier'),data,identityIndex,state.filters,
      filters=>{state.filters=filters;draw(el,summary,data);},
      id=>{const ent=entById.get(id);if(ent){setTab("map");selectLot(data.parcel,ent.id,{fit:true});openStreet(ent);}},state.addresses);
    const investigation=document.createElement('section');
    el.querySelector('#parcelIdentityDossier').after(investigation);
    InvestigationView.render(investigation,state.investigationSummary,state.investigation,data,fp=>{state.parcel=fp;state.property=null;state.filters={query:'',kind:'all',entrance:null};render(el);});
    if(local&&window.PropertyReviewView&&state.review){
      const review=document.createElement('section');investigation.after(review);
      PropertyReviewView.render(review,state.reviewSummary,state.review,fp=>{state.parcel=fp;state.property=null;state.filters={query:'',kind:'all',entrance:null};render(el);});
    }
    renderRoofs(el.querySelector("#registryRoofs"));
  }
  function propertyHtml(p,c,data){
    const links=data.links.filter(l=>(l.source===p.id || l.kind==='property_alias' && l.target===p.id) && l.status==="candidate");
    return `<div class="registry-identity"><div><span class="evidence">${translate(kinds[p.scope]||kinds.cadastral_property)}</span><h2>${p.members.map(m=>`${safe(m[2])}/${safe(m[3])}/${safe(m[4]||"?")}`).join(" + ")}</h2></div>${c?.inspected_pdf?`<span class="evidence">${label("PDF ispezionato","PDF inspected")}</span>`:""}</div>
      <p>${safe(p.address)} ${safe(p.civic||"")}</p><dl class="registry-facts"><div><dt>${label("Piano","Floor")}</dt><dd>${safe(p.floor)}</dd></div><div><dt>${label("Interni riportati negli APE","Interiors reported in APEs")}</dt><dd>${safe(p.reported_interiors?.join(' · ')||null)}</dd></div><div><dt>${label("Superficie riscaldata","Heated area")}</dt><dd>${fmt(p.heated_area_m2,2)} m²</dd></div><div><dt>${label("Uso","Use")}</dt><dd>${p.residential?label("Residenziale","Residential"):label("Non residenziale / altro","Non-residential / other")}</dd></div><div><dt>${label("APE ammissibili alla data","Date-eligible APEs")}</dt><dd>${p.eligible_certificates}</dd></div></dl>
      ${p.interior_observations?.length?`<details><summary>${label('Provenienza degli interni · osservazioni, non identificatori catastali','Interior provenance · observations, not cadastral identifiers')}</summary><p class="hint">${label('Sono conservati anche valori grezzi e segnaposto. Osservazioni discordanti non sono unite in un singolo interno.','Raw values and placeholders are retained. Conflicting observations are not collapsed into one interior number.')}</p><ul>${p.interior_observations.map(o=>`<li>${safe(o.raw)} → ${safe(o.normalized||label(o.kind==='descriptor'?'descrizione, non numero interno':o.kind==='needs_review'?'valore da verificare':'segnaposto / non indicato',o.kind==='descriptor'?'descriptor, not an interior number':o.kind==='needs_review'?'value requiring review':'placeholder / not reported'))} · ${safe(o.submitted)} · ${safe(o.certificate_id)} · <a href="${safe(o.source)}" target="_blank" rel="noopener noreferrer">${label('fonte regionale','regional source')}</a></li>`).join('')}</ul></details>`:''}
      <p class="registry-warning">${label("La superficie riguarda l'oggetto attestato; non si duplica per subalterno. Piano e accesso non costituiscono una geometria interna.","Area belongs to the attested object and is not duplicated per subalterno. Floor and entrance do not establish interior geometry.")}</p>
      ${p.flags.length?`<ul class="registry-flags">${p.flags.map(f=>`<li>${safe(flagLabels[f]?translate(flagLabels[f]):f)}</li>`).join("")}</ul>`:""}
      <details><summary>${label("Identificatori catastali originali","Original cadastral identifiers")}</summary><ul>${p.members.map(m=>`<li>${safe(m[0])} · ${label("sezione","section")} ${safe(m[1]||label("non indicata","not reported"))} · ${safe(m[2])}/${safe(m[3])}/${safe(m[4]||"?")}</li>`).join("")}</ul></details>
      ${InvestigationView.property(p,state.investigation)}${local&&window.PropertyReviewView?PropertyReviewView.property(p,state.review,data):''}<h3>${label("Collegamenti proposti · revisione","Proposed relationships · review")}</h3><p class="hint">${label("Una corrispondenza di indirizzo è una proposta; la vicinanza di un edificio non identifica l'appartamento. Accetta solo con evidenze aggiuntive.","An address match is a proposal; a nearby building does not identify the apartment. Accept only with additional evidence.")}</p>
      ${links.map(l=>linkHtml(l,data,p)).join("") || `<p>${label("Nessun collegamento candidato disponibile.","No candidate relationships available.")}</p>`}
      <h3>${label("Storico attestati e provenienza","Certificate history & provenance")}</h3>
      <div class="registry-certificates">${p.certificates.map(id=>certificateHtml(data.certificates.find(x=>x.id===id))).join("")}</div>`;
  }
  function certificateHtml(x){
    const flags={
      source_floor_disagreement:["Piano discordante tra le fonti","Floor differs between sources"],
      source_heated_area_m2_disagreement:["Superficie discordante tra le fonti","Area differs between sources"],
      source_status_disagreement:["Stato discordante tra le fonti","Status differs between sources"],
      source_cadastral_members_differ:["La fonte regionale e il portale elencano identificatori catastali differenti","Regional and live sources list different cadastral identifiers"],
      conflicting_live_snapshots:["Osservazioni successive discordanti","Conflicting successive observations"],
      same_attributes_different_certificate_key:["Attributi uguali, chiavi APE diverse: attestati tenuti separati","Equal attributes, different APE keys: certificates kept separate"],
      ambiguous_certificate_alias:["Equivalenza tra attestati non risolta","Certificate equivalence unresolved"]
    };
    return `<article><strong>${safe(x.public_code||x.source_record_id||x.id)}</strong><span class="evidence ${x.eligible_on_date?"":"assumption"}">${safe(x.status)}</span>
      <p>${safe(x.submitted)} → ${safe(x.expires)} · ${safe(x.source_kind)}</p><p>${x.eligible_on_date?label("Attivo nella fonte e non scaduto alla data di riferimento.","Active in source and unexpired on the reference date."):label("Non incluso tra gli APE ammissibili alla data.","Excluded from date-eligible APEs.")}</p>
      <a href="${safe(x.source)}" target="_blank" rel="noopener noreferrer">${label("Apri fonte originale","Open original source")} ↗</a>
      ${x.source_aliases?.length?`<p>${label("Fonti riconciliate con chiave dell'attestato, data e dati catastali concordanti.","Sources reconciled using the certificate key, date and corroborating cadastral data.")}</p>
      ${x.source_aliases.map(a=>`<details><summary>${label('Osservazione regionale · campi originali','Regional observation · original fields')}</summary><dl class="kv"><dt>${label('Identificatore nella fonte','Source identifier')}</dt><dd>${safe(a.id)}</dd><dt>${label('Dati catastali nella fonte','Source cadastral identifiers')}</dt><dd>${a.members.map(m=>m.map(safe).join(' / ')).join(' + ')}</dd><dt>${label('Piano nella fonte','Source floor')}</dt><dd>${safe(a.floor)}</dd><dt>${label('Superficie nella fonte','Source area')}</dt><dd>${fmt(a.heated_area_m2,2)} m²</dd><dt>${label('Unità dichiarate nell’edificio (non verificate)','Declared building units (unverified)')}</dt><dd>${safe(a.declared_building_units)}</dd></dl></details>`).join('')}`:''}
      ${x.flags?.length?`<p class="registry-warning">${x.flags.map(f=>safe(flags[f]?translate(flags[f]):f)).join(' · ')}</p>`:''}</article>`;

  }
  function linkHtml(link,data,property){
    const entrance=link.target.startsWith("entrance:");
    if(link.kind==='property_alias'){
      const otherId=link.source===property.id?link.target:link.source;
      const other=data.properties.find(p=>p.id===otherId);
      const proxy={...link,kind:'property_alias_display',target:'alias:'+otherId,evidence:[label('Stessi identificatori eccetto la sezione catastale. Verificare se sezione assente e dichiarata identificano lo stesso immobile. Accettare non somma i consumi e non cancella le fonti.','Same identifiers except cadastral section. Verify whether absent and stated sections identify the same property. Acceptance does not sum energy or delete source records.')]};
      return `<div><button type="button" class="btn outline sm" data-alias-property="${safe(otherId)}">${label('Confronta possibile identità equivalente','Compare possible equivalent identity')}: ${safe(other?.members.map(m=>m[1]||'?').join(' + '))}</button>${linkHtml(proxy,data,property)}</div>`;
    }
    const id=link.target.split(":").slice(1).join(":");
    const e=entrance&&data.entrances.find(e=>String(e.COD_CIVICO)===id);
    const decision=link.review?.decision||"unreviewed";
    const decisionLabel={accepted:["Accettato in revisione","Accepted in review"],rejected:["Rifiutato in revisione","Rejected in review"],unreviewed:["Da verificare","Unreviewed"]};
    const evidenceIT={"source property parcel matches inherited entrance parcel assignment":"lotto dell'APE e assegnazione GIS dell'ingresso concordanti","exact normalized street and civic including suffix":"via e civico normalizzati esatti, inclusa la lettera","same parcel":"stesso lotto","inherited GIS entrance-to-building proposal":"proposta ingresso-edificio ereditata dal GIS","parcel-only proposal; interior unit position unknown":"proposta basata sul solo lotto; posizione interna sconosciuta"};
    return `<article class="registry-link"><div><strong>${link.target.startsWith('alias:')?label('Possibile equivalenza catastale','Possible cadastral equivalence'):entrance?label("Ingresso","Entrance"):label("Edificio","Building")} ${link.target.startsWith('alias:')?'':safe(e?.indirizzo||id)}</strong><span class="evidence ${decision==="unreviewed"?"assumption":""}">${translate(decisionLabel[decision])}</span></div><p>${link.evidence.map(x=>safe(label(evidenceIT[x]||x.replace('entrance GIS match:','Assegnazione GIS ingresso:'),x))).join(" · ")}</p>${entrance?`<button type="button" class="btn outline sm" data-entrance="${safe(id)}">${label("Vedi ingresso e Street View","View entrance & Street View")}</button>`:""}<label>${label("Nota di revisione","Review note")}<input data-review-note maxlength="2000" value="${safe(link.review?.note||"")}" ${state.api?"":"disabled"}></label><div class="registry-validity"><label>${label("Valido dal (se noto)","Valid from (if known)")}<input data-valid-from type="date" value="${safe(link.review?.valid_from||'')}" ${state.api?'':'disabled'}></label><label>${label("Valido fino al, escluso (se noto)","Valid until, exclusive (if known)")}<input data-valid-to type="date" value="${safe(link.review?.valid_to||'')}" ${state.api?'':'disabled'}></label></div><div class="actions">${[["accepted","Accetta","Accept"],["rejected","Rifiuta","Reject"],["unreviewed","Riapri verifica","Reopen review"]].map(([decision,it,en])=>`<button type="button" class="btn outline sm" data-review="${safe(link.id)}" data-decision="${decision}" ${state.api?"":"disabled"}>${label(it,en)}</button>`).join("")}</div></article>`;
  }
  async function renderRoofs(el){
    try {const r=await json("data/roof_evidence.json");el.innerHTML=`<h2>${label("Copertura 3D e qualità delle fonti","3D coverage & source quality")}</h2><p>${label(r.summary_it,r.summary_en)}</p><button type="button" class="btn outline" id="roofReferenceMap">${label("Apri campione altezze sulla mappa","Open height reference sample on map")}</button><div class="registry-roof-grid">${r.sources.map(s=>`<article><h3>${safe(s.title)}</h3><span class="evidence assumption">${label(s.status_it,s.status_en)}</span><p>${label(s.finding_it,s.finding_en)}</p><a href="${safe(s.url)}" target="_blank" rel="noopener noreferrer">${label("Fonte","Source")} ↗</a></article>`).join("")}</div>`;
      if(!local){
        el.querySelector('#roofReferenceMap').remove();
        const note=document.createElement('p');note.className='hint';note.textContent=label('La geometria del campione ARPA è esclusa dalla pubblicazione: diritti di riuso non risolti.','ARPA sample geometry is excluded from publication: reuse rights remain unresolved.');el.prepend(note);
        return;
      }
      el.querySelector("#roofReferenceMap").onclick=async()=>{
        const geo=await json("data/roof_reference_sample.geojson");
        const coverage=await json('data/lidar_coverage_sample.geojson');
        if(!state.coverageLayer)state.coverageLayer=L.geoJSON(coverage,{style:{color:'#94782f',weight:2,dashArray:'7 5',fillOpacity:0},attribution:'MASE / PST-A · CC BY 4.0 · coverage index only',onEachFeature:(f,l)=>l.bindPopup(()=>`<b>${safe(f.properties.tavola)}</b><p>${label('Indice LiDAR: risoluzione dichiarata 1 m. Raster non acquisito; pixel validi non verificati.','LiDAR index: advertised 1 m resolution. Raster not acquired; valid pixels unverified.')}</p>`)});
        if(!state.heightLayer)state.heightLayer=L.geoJSON(geo,{style:{color:"#8257a6",weight:2,fillOpacity:0.08},attribution:"ARPA Piemonte · Edifici 3D 2017 · local height reference",onEachFeature:(f,l)=>l.bindPopup(()=>`<b>ARPA · ${safe(f.properties.OBJECTID)}</b><p>ELEV: ${safe(f.properties.ELEV)} m · DES: ${safe(f.properties.DES)}</p><p>${label("Solo quota in gronda · nessuna falda di tetto","Eaves-height attribute only · no roof planes")}</p>`)});
        if(!state.referenceGroup){
          state.referenceGroup=L.layerGroup([state.coverageLayer,state.heightLayer]);
          const toggle=document.createElement('label');toggle.className='switch';toggle.innerHTML='<span id="roofReferenceLabel"></span><input type="checkbox" id="roofReferenceToggle">';document.querySelector('[data-view="livelli"] .block').append(toggle);
          document.querySelector('#roofReferenceToggle').onchange=e=>e.target.checked?state.referenceGroup.addTo(map):map.removeLayer(state.referenceGroup);
        }
        document.querySelector('#roofReferenceLabel').textContent=label('Campione altezze e indice LiDAR','Height sample & LiDAR index');
        document.querySelector('#roofReferenceToggle').checked=true;
        setTab("map");state.referenceGroup.addTo(map);map.fitBounds(state.heightLayer.getBounds(),{padding:[30,30]});
      };
    }catch(_){el.innerHTML="";}
  }
  langBox.addEventListener('click',()=>{const labelEl=document.querySelector('#roofReferenceLabel');if(labelEl)labelEl.textContent=label('Campione altezze e indice LiDAR','Height sample & LiDAR index');});
  document.addEventListener("lotselected",e=>{state.parcel=e.detail.fp;state.property=null;state.filters={query:"",kind:"all",entrance:null};});
  return {render,open(fp,property=null){state.parcel=fp;state.property=property;state.legacy=false;window.PropertyWorkbench?.select(fp,property);state.filters={query:"",kind:"all",entrance:null};setTab("registry");}};
})();
