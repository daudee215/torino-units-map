/* Local citywide explorer. Requests are bounded by page/viewport. */
window.CityWorkspace=(()=>{
 const API='http://127.0.0.1:8766/api/city';
 let cm=null,root=null,sequence=0,detailSequence=0,viewportSequence=0,timer=null,options=null,summary=null,selectionLayer=null;
 const state={query:'',kind:'property',offset:0,parcel:'',center:null,zoom:12,selected:null};
 const t=(it,en)=>document.documentElement.lang==='it'?it:en;
 const e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const n=x=>Number(x).toLocaleString(document.documentElement.lang==='it'?'it-IT':'en-GB');
 async function get(path){return window.CityDataClient.get(path);}
 function deactivate(){sequence++;detailSequence++;viewportSequence++;clearTimeout(timer);if(cm){state.center=cm.getCenter();state.zoom=cm.getZoom();cm.remove();cm=null;}root=null;}
 function coverage(){return `<h2>${t('Copertura di Torino','Torino coverage')}</h2><p>${t('Intero comune · L219 / ISTAT 001272','Whole municipality · L219 / ISTAT 001272')}</p><dl>${[['parcel','Riferimenti cartografici','Cartographic parcel references'],['building','Impronte BDTRE','BDTRE footprints'],['entrance','Civici comunali','Municipal civic points'],['ape_identities','Identità / gruppi APE','APE identities / groups'],['ape_certificate_ids','Certificati APE · archivio regionale','APE certificates · regional bulk'],['municipal_only_identities','Chiavi solo inventario','Inventory-only keys']].map(([k,it,en])=>`<dt>${t(it,en)}</dt><dd>${n(summary.counts[k]||0)}</dd>`).join('')}</dl><p class="city-notice">${t('Non è un censimento completo degli appartamenti. Collegamenti a ingressi e immobili da verificare.','This is not a complete apartment census. Property and entrance connections require verification.')}</p><p>${n(summary.counts.pilot_additional_ape_identities)} ${t('identità aggiuntive dalle consultazioni del pilota incluse nel totale.','additional identities from pilot portal queries included in the total.')}</p><h3>${t('Qualità dei collegamenti','Connection quality')}</h3><p>${n(summary.quality.properties_with_unique_address_candidate)} ${t('identità con un candidato civico esatto; accesso non confermato.','identities with one exact civic candidate; access unconfirmed.')}<br>${n(summary.quality.incomplete_property_identities)} ${t('identità incomplete.','incomplete identities.')}</p><h3>${t('Edizioni delle fonti','Source editions')}</h3><p>Catasto: ${e(summary.cadastre.timeStamp)}<br>BDTRE 2026<br>APE: ${e(summary.ape_submission_range?.[0]?.slice(0,10))} → ${e(summary.ape_submission_range?.[1]?.slice(0,10))}<br>${t('Inventario comunale: aprile 2023','Municipal inventory: April 2023')}</p><p>${window.CityDataClient.local?t('Il pilota San Donato conserva le indagini approfondite e le note locali.','The San Donato pilot retains its detailed investigations and local notes.'):t('Il pilota San Donato conserva le indagini di fonte. Le note locali non sono pubblicate.','The San Donato pilot retains its source investigations. Local notes are not published.')}</p><button class="btn outline" id="cityPilot">${t('Apri il pilota revisionato','Open reviewed pilot')}</button><p><a href="https://www.agenziaentrate.gov.it/portale/download-massivo-cartografia-catastale" target="_blank" rel="noopener">Agenzia delle Entrate · CC BY 4.0 ↗</a></p><p><a href="${e(summary.bdtre_source)}" target="_blank" rel="noopener">Regione Piemonte · BDTRE ↗</a></p><p>${window.CityDataClient.local?t('Stato locale · nessuna nuova pubblicazione','Local development · no new publication'):t('Edizione pubblica · dati di fonte','Public edition · source data')}</p>`;}
 async function render(host,opts){
  // Move the shared Street View outside the subtree before replacing it.
  if(opts.street.parentElement!==document.querySelector('.mapwrap'))document.querySelector('.mapwrap').append(opts.street);
  deactivate();root=host;options=opts;const seq=sequence;
  host.classList.add('city-workspace-host');host.innerHTML=`<div class="empty">${t('Caricamento catalogo di Torino…','Loading Torino catalogue…')}</div>`;
  try{summary=await get('');if(seq!==sequence||!root)return;
   host.innerHTML=`<section class="city-workspace"><header class="city-heading"><div><small>TORINO / L219</small><h1>${t('Atlante immobili · tutta Torino','Property atlas · whole Torino')}</h1></div><span>${n(summary.counts.parcel)} ${t('riferimenti cartografici','cartographic references')} · ${n(summary.counts.building)} ${t('edifici','buildings')} · ${window.CityDataClient.local?t('Locale 2.5.1','Local 2.5.1'):e(summary.version)}</span><div class="city-extent-controls"><button class="btn outline" id="cityExtent">${t('Intero comune','Whole municipality')}</button><button class="btn outline" id="cityNorth">${t('Torino nord','North Torino')}</button><button class="btn outline" id="citySouth">${t('Torino sud','South Torino')}</button></div></header><div class="city-body"><aside class="city-search"><label for="cityQuery">${t('Indirizzo, foglio / particella / subalterno','Address, sheet / parcel / subalterno')}</label><input id="cityQuery" type="search" value="${e(state.query)}" placeholder="${t('Cerca in tutta Torino…','Search all Torino…')}"><label for="cityKind">${t('Tipo di record','Record type')}</label><select id="cityKind">${[['property','Immobili / gruppi','Properties / groups'],['parcel','Particelle','Parcels'],['entrance','Ingressi civici','Civic entrances'],['building','Edifici BDTRE','BDTRE buildings']].map(([v,it,en])=>`<option value="${v}" ${v===state.kind?'selected':''}>${t(it,en)}</option>`).join('')}</select><div id="cityFilter"></div><p id="cityResultsCount" role="status"></p><div id="cityResults"></div><div class="city-pagination"><button class="btn outline" id="cityPrev">←</button><span id="cityRange"></span><button class="btn outline" id="cityNext">→</button></div></aside><div class="city-mapwrap"><div id="cityMap" aria-label="${t('Mappa di tutta Torino','Whole Torino map')}"></div><div class="city-map-status" id="cityMapStatus" role="status"></div></div><aside class="city-inspector" id="cityInspector">${coverage()}</aside></div><footer>${t('Particelle e edifici caricati solo nella vista · seleziona un elemento per esplorare le fonti','Parcels and buildings load only in the current view · select a feature to explore its sources')}</footer></section>`;
   opts.street.hidden=true;host.querySelector('.city-mapwrap').append(opts.street);
   cm=L.map('cityMap',{minZoom:10,maxZoom:21,preferCanvas:true}).setView(state.center||[45.067,7.69],state.zoom);
   if(!state.center)cm.fitBounds([[summary.bounds[1],summary.bounds[0]],[summary.bounds[3],summary.bounds[2]]],{padding:[18,18],maxZoom:13});
   L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',{maxNativeZoom:16,maxZoom:21,attribution:'Basemap © Esri, HERE, OpenStreetMap'}).addTo(cm);
   L.geoJSON(summary.boundary,{style:{color:'#316e9c',weight:2,fill:false,interactive:false}}).addTo(cm);
   const layers={parcel:L.geoJSON(null,{style:{color:'#55798d',weight:.7,fillColor:'#f6f9fa',fillOpacity:.35},onEachFeature:(f,l)=>l.on('click',ev=>{if(ev.originalEvent)ev.originalEvent.cityFeatureHandled=true;select(f.properties.id);})}).addTo(cm),building:L.geoJSON(null,{style:{color:'#6f7780',weight:.6,fillColor:'#a7b2bb',fillOpacity:.35},onEachFeature:(f,l)=>l.on('click',ev=>{if(ev.originalEvent)ev.originalEvent.cityFeatureHandled=true;select(f.properties.id);})}).addTo(cm),entrance:L.geoJSON(null,{pointToLayer:(f,ll)=>L.circleMarker(ll,{radius:4,color:'#fff',weight:1,fillColor:'#007ac2',fillOpacity:1}),onEachFeature:(f,l)=>l.on('click',ev=>{if(ev.originalEvent)ev.originalEvent.cityFeatureHandled=true;select(f.properties.id,true);})}).addTo(cm)};
   cm.createPane('cityOverview').style.zIndex='390';
   // One canvas holds citywide outlines; avoid 82,434 Leaflet path objects.
   const ParcelOverview=L.Layer.extend({
    initialize(){this.features=[];},
    onAdd(m){this.canvas=L.DomUtil.create('canvas','leaflet-layer city-parcel-overview');this.canvas.setAttribute('aria-hidden','true');this.canvas.style.pointerEvents='none';m.getPane('cityOverview').append(this.canvas);m.on('moveend resize',this.redraw,this);m.on('zoomstart',this.hide,this);this.redraw();},
    onRemove(m){m.off('moveend resize',this.redraw,this);m.off('zoomstart',this.hide,this);this.canvas.remove();},
    hide(){if(this.canvas)this.canvas.style.visibility='hidden';},
    setFeatures(features){this.features=features;this.redraw();},
    redraw(){
     if(!this._map||!this.canvas)return;
     const m=this._map,size=m.getSize(),ratio=Math.min(devicePixelRatio||1,2),ctx=this.canvas.getContext('2d');
     this.canvas.width=Math.ceil(size.x*ratio);this.canvas.height=Math.ceil(size.y*ratio);this.canvas.style.width=size.x+'px';this.canvas.style.height=size.y+'px';this.canvas.style.visibility='visible';L.DomUtil.setPosition(this.canvas,m.containerPointToLayerPoint([0,0]));ctx.setTransform(ratio,0,0,ratio,0,0);ctx.lineWidth=.45;ctx.strokeStyle='rgba(75,110,130,.7)';ctx.fillStyle='rgba(247,250,252,.2)';ctx.beginPath();let count=0;
     const paint=()=>{ctx.fill('evenodd');ctx.stroke();ctx.beginPath();};
     for(const f of this.features){const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;
      for(const polygon of polygons)for(const ring of polygon){ring.forEach(([lng,lat],i)=>{const p=m.latLngToContainerPoint([lat,lng]);if(i===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);});ctx.closePath();}
      if(++count%1000===0)paint();
     }paint();
    }
   });
   const overviewLayer=new ParcelOverview().addTo(cm);
   const parcelGroup=L.layerGroup([overviewLayer,layers.parcel]).addTo(cm);
   let overviewFeatures=[];
   selectionLayer=L.geoJSON(null,{style:{color:'#007ac2',weight:3,fillColor:'#69b6e3',fillOpacity:.22},pointToLayer:(f,ll)=>L.circleMarker(ll,{radius:8,color:'#007ac2',weight:3,fillOpacity:.2}),interactive:false}).addTo(cm);
   L.control.layers(null,{[t('Particelle · AdE','Parcels · AdE')]:parcelGroup,[t('Edifici · BDTRE','Buildings · BDTRE')]:layers.building,[t('Civici · Comune','Civics · Municipality')]:layers.entrance}).addTo(cm);
   cm.attributionControl.addAttribution('Catasto © Agenzia delle Entrate · BDTRE © Regione Piemonte · Civici © Città di Torino · CC BY 4.0');
   async function view(){
    if(!cm||seq!==sequence)return;
    const v=++viewportSequence,status=host.querySelector('#cityMapStatus'),bbox=cm.getBounds().toBBoxString(),detail=cm.getZoom()>=16;
    status.textContent=t('Caricamento delle particelle nella vista…','Loading parcel outlines in this view…');
    try{
     const [overview,sets]=await Promise.all([CityDataClient.overview(bbox),detail?Promise.all(Object.keys(layers).map(k=>get('/features?kind='+k+'&bbox='+bbox))):Promise.resolve(null)]);
     if(v!==viewportSequence||seq!==sequence||!cm)return;
     overviewFeatures=overview.features;overviewLayer.setFeatures(overview.features);
     Object.keys(layers).forEach((k,i)=>{layers[k].clearLayers();if(sets)layers[k].addData(sets[i]);});
     if(selectionLayer)selectionLayer.bringToFront();
     const label=n(overview.features.length)+' '+t('particelle nella vista · panoramica generalizzata a 2 m','parcel outlines in view · generalized 2 m overview');
     status.textContent=label+(sets&&!sets.some(s=>s.truncated||s.zoom_required)?' · '+n(sets[1].features.length)+' '+t('edifici','buildings')+' · '+n(sets[2].features.length)+' '+t('civici','civics'):' · '+t('ingrandisci per edifici e civici dettagliati','zoom for detailed buildings and civics'));
    }catch(err){if(v===viewportSequence&&seq===sequence)status.textContent=err.message;}
   }
   cm.on('moveend',view);view();
   cm.on('click',ev=>{
    if(ev.originalEvent?.cityFeatureHandled||!cm.hasLayer(parcelGroup))return;
    const {lng,lat}=ev.latlng,point=turf.point([lng,lat]);
    const matches=overviewFeatures.filter(f=>{const b=f.properties.bbox;return b[0]<=lng&&b[2]>=lng&&b[1]<=lat&&b[3]>=lat&&turf.booleanPointInPolygon(point,f);});
    if(matches.length===1)select(matches[0].id);
    else if(matches.length>1)host.querySelector('#cityInspector').innerHTML=`<h2>${t('Particelle sovrapposte nella panoramica','Overlapping overview parcels')}</h2><p>${t('Scegli un riferimento per vedere la geometria di fonte.','Choose a reference to inspect its source geometry.')}</p>${matches.map(f=>link(f.id,f.properties.title)).join('')}`;
   });
   const fit=(south,north)=>cm.fitBounds([[south,summary.bounds[0]],[north,summary.bounds[2]]],{padding:[18,18],maxZoom:16});
   host.querySelector('#cityExtent').onclick=()=>fit(summary.bounds[1],summary.bounds[3]);
   host.querySelector('#cityNorth').onclick=()=>fit((summary.bounds[1]+summary.bounds[3])/2,summary.bounds[3]);
   host.querySelector('#citySouth').onclick=()=>fit(summary.bounds[1],(summary.bounds[1]+summary.bounds[3])/2);
   host.querySelector('#cityQuery').oninput=ev=>{state.query=ev.target.value;state.offset=0;clearTimeout(timer);timer=setTimeout(search,250);};
   host.querySelector('#cityKind').onchange=ev=>{state.kind=ev.target.value;state.offset=0;state.parcel='';search();};
   host.querySelector('#cityPrev').onclick=()=>{state.offset=Math.max(0,state.offset-50);search();};host.querySelector('#cityNext').onclick=()=>{state.offset+=50;search();};
   host.querySelector('#cityInspector').onclick=inspectorClick;
   search();
   if(state.selected)select(state.selected);
  }catch(err){if(seq===sequence)host.innerHTML=`<div class="empty">${e(err.message)}. ${window.CityDataClient.local?t('Avvia entrambi i servizi locali.','Start both local services.'):t('Ricarica la pagina e riprova.','Reload the page and try again.')}</div>`;}
 }
 let searchSequence=0;
 async function search(){const host=root;if(!host)return;const seq=++searchSequence;host.querySelector('#cityResultsCount').textContent=t('Ricerca…','Searching…');
  try{const data=await get('/search?'+new URLSearchParams({q:state.query,kind:state.kind,offset:state.offset,parcel:state.parcel}));if(seq!==searchSequence||root!==host)return;
   host.querySelector('#cityResultsCount').textContent=n(data.total)+' '+t('record di fonte','source records');
   host.querySelector('#cityFilter').innerHTML=state.parcel?`<button class="btn outline" id="cityClearParcel">${e(state.parcel)} ×</button>`:'';
   if(state.parcel)host.querySelector('#cityClearParcel').onclick=()=>{state.parcel='';state.offset=0;search();};
   host.querySelector('#cityResults').innerHTML=data.records.map(r=>`<button type="button" class="city-result" data-city-id="${e(r.id)}" aria-pressed="${state.selected===r.id}"><b>${e(r.title.length>110?r.title.slice(0,110)+'…':r.title)}</b><small>${e(r.description)}</small></button>`).join('')||`<p>${t('Nessun record trovato. Non significa assenza di immobili.','No records found. This does not establish absence of properties.')}</p>`;
   host.querySelector('#cityResults').onclick=ev=>{const b=ev.target.closest('[data-city-id]');if(b)select(b.dataset.cityId);};
   host.querySelector('#cityPrev').disabled=!state.offset;host.querySelector('#cityNext').disabled=state.offset+50>=data.total;host.querySelector('#cityRange').textContent=data.total?`${state.offset+1}–${Math.min(state.offset+50,data.total)}`:'0';
  }catch(err){if(seq===searchSequence&&root===host)host.querySelector('#cityResultsCount').textContent=err.message;}
 }
 function inspectorClick(ev){const b=ev.target.closest('[data-city-id]');if(b){select(b.dataset.cityId,b.dataset.street==='1');return;}const fp=ev.target.closest('[data-city-parcel]');if(fp){state.parcel=fp.dataset.cityParcel;state.kind='property';state.query='';state.offset=0;root.querySelector('#cityQuery').value='';root.querySelector('#cityKind').value='property';search();return;}if(ev.target.closest('#cityPilot')){options.pilot();}}
 const link=(id,title,street=false)=>`<button class="btn outline city-link" data-city-id="${e(id)}" ${street?'data-street="1"':''}>${e(title)}</button>`;
 async function select(id,streetView=false){const host=root;if(!host)return;const seq=++detailSequence;state.selected=id;
  try{const {record:r}=await get('/record/'+encodeURIComponent(id));if(seq!==detailSequence||root!==host||!cm)return;
   const inspector=host.querySelector('#cityInspector');let html=`<small>${e(({property:t('Immobile / gruppo','Property / group'),parcel:t('Particella','Parcel'),building:t('Edificio','Building'),entrance:t('Ingresso civico','Civic entrance')})[r.kind]||r.kind)}</small><h2>${e(r.title.length>140?r.title.slice(0,140)+'…':r.title)}</h2>`;
   if(r.kind==='property'){
    selectionLayer.clearLayers();
    html+=`<p>${e(r.address)}</p><span class="city-notice">${t('Accesso attuale e posizione dell’unità non verificati','Current entrance and unit position unverified')}</span><dl><dt>${t('Ambito della fonte','Source scope')}</dt><dd>${e(({cadastral_property:t('Identità catastale riportata','Reported cadastral identity'),group:t('Gruppo attestato','Attested group'),whole_building:t('Intero edificio attestato','Attested whole building'),reported_cadastral_reference:t('Riferimento catastale da inventario','Inventory cadastral reference')})[r.scope]||r.scope)}</dd><dt>${t('Certificati','Certificates')}</dt><dd>${n(r.certificates.length)}</dd></dl>${!r.identity_complete?`<p class="city-notice">${t('Identificativi incompleti nella fonte: nessun subalterno inventato.','Incomplete source identifiers: no subalterno has been inferred.')}</p>`:''}<h3>${t('Identificativi originali','Original identifiers')}</h3>${r.members.map(m=>`<p class="city-key">${e(m.join(' / '))}</p>`).join('')}<h3>${t('Particelle cartografiche candidate','Candidate cartographic parcels')}</h3>${Object.entries(r.cartographic_candidates).map(([fp,ids])=>`<div><button class="btn outline" data-city-parcel="${e(fp)}">${e(fp)} · ${t('record','records')}</button>${ids.map(i=>link(i,t('Mappa','Map')+' ↗')).join('')}${!ids.length?`<small>${t('Nessuna corrispondenza geometrica','No geometry match')}</small>`:''}</div>`).join('')}<p>${t('Confronto foglio/particella: sezioni, allegati e sviluppi richiedono verifica.','Sheet/parcel comparison: sections, attachments and developments require review.')}</p><h3>${t('Candidati da indirizzo','Address candidates')}</h3>${r.address_candidates.map(a=>link(a.id,a.address,true)).join('')||`<p>${t('Nessuna corrispondenza esatta con un civico comunale.','No exact municipal civic match.')}</p>`}<p>${t('Indirizzi esatti normalizzati; non confermano l’ingresso dell’appartamento.','Exact normalized addresses do not confirm the apartment entrance.')}</p><h3>${t('Osservazioni APE','APE observations')}</h3>${r.certificates.map(c=>`<details><summary>${e(c.id)} · ${e((c.submitted||'').slice(0,10))}</summary><p>${e(c.address)} ${e(c.civic)}</p><p>${t('Piano dichiarato','Reported floor')}: ${e(c.floor||'—')}<br>${t('Superficie riscaldata dell’oggetto attestato','Heated area of the attested object')}: ${e(c.heated_area_m2??'—')} m²<br>${t('Ambito','Scope')}: ${e(c.object_scope)}<br>${t('Scadenza dichiarata','Reported expiry')}: ${e(c.expires||'—')}<br>${t('Stato dichiarato nella fonte','Reported source status')}: ${e(c.status||(c.active_source_flag==='1'?t('Flag attivo nella fonte','Active flag in source'):String(c.active_source_flag??'—')))}</p><a href="${e(c.source_url)}" target="_blank" rel="noopener">${t('Fonte regionale','Regional source')} ↗</a></details>`).join('')}<h3>${t('Inventario comunale · aprile 2023','Municipal inventory · April 2023')}</h3>${r.municipal_refs.map(a=>`<details><summary>${t('Pagina','Page')} ${e(a.page)} · ${e(a.asset_primary_address)}</summary><p>${e(a.asset_description)}</p><p>${t('Indirizzo e descrizione del gruppo patrimoniale, non dell’unità. Validità attuale sconosciuta.','Asset-group address and description, not unit attributes. Current validity unknown.')}</p><a href="${e(a.source)}#page=${a.page}" target="_blank" rel="noopener">PDF ↗</a></details>`).join('')||'<p>—</p>'}`;
    if(r.pilot_record_available)html+=`<button class="btn outline" id="cityPilot">${t('Apri indagine del pilota','Open pilot investigation')}</button>`;
   }else{
    html+=`<p>${t('Geometria di fonte; relazioni proposte da verificare.','Source geometry; proposed relationships require review.')}</p>`;
    if(r.kind==='parcel')html+=`<p class="city-key">${e(r.reference)}</p><p>${t('Allegato / sviluppo','Attachment / development')}: ${e(r.allegato)} / ${e(r.sviluppo)}</p><button class="btn outline" data-city-parcel="${e(r.fp)}">${n(r.property_record_count)} ${t('record immobiliari di fonte','property source records')}</button><p>${e(r.source_timestamp)}</p>`;
    if(r.kind==='building')html+=`<p>${t('Uso dichiarato','Reported use')}: ${e(r.use||'—')}<br>${t('Aggiornamento della fonte','Source update')}: ${e(r.source_updated||'—')}<br>${t('Impronta 2D; nessun LoD2/2.5 dichiarato','2D footprint; no claimed LoD2/2.5')}</p>`;
    if(r.kind==='entrance')html+=`<p>${t('Circoscrizione','District')}: ${e(r.district||'—')}</p>${link(r.id,t('Apri Street View','Open Street View'),true)}`;
    if(r.parcel_candidates)html+=`<h3>${t('Particelle candidate · intersezione geometrica','Candidate parcels · geometric intersection')}</h3>${r.parcel_candidates.map(i=>link(i,i.replace('cadastre:',''))).join('')||'<p>—</p>'}`;
    html+=`<p><a href="${e(r.source_url)}" target="_blank" rel="noopener">${t('Fonte originale','Original source')} ↗</a></p>`;
    if(r.geometry){selectionLayer.clearLayers();selectionLayer.addData(r.geometry);selectionLayer.bringToFront();const shape=L.geoJSON(r.geometry);const bounds=shape.getBounds();if(bounds.isValid())cm.fitBounds(bounds,{maxZoom:r.kind==='entrance'?19:18,padding:[35,35]});}
    if(r.kind==='entrance'){const [lng,lat]=r.coordinates;options.openStreet({id:r.id,p:{indirizzo:r.title},layer:{getLatLng:()=>({lat,lng})}});}
   }
   inspector.innerHTML=html;inspector.scrollTop=0;
   if(r.kind==='property'&&r.address_candidates.length===1){const [lng,lat]=r.address_candidates[0].coordinates;cm.setView([lat,lng],18);}
   host.querySelectorAll('.city-result').forEach(b=>b.setAttribute('aria-pressed',b.dataset.cityId===id?'true':'false'));
   options.current=r;window.cityPilotRecord=r;
  }catch(err){if(seq===detailSequence&&root===host)host.querySelector('#cityInspector').innerHTML=`<p>${e(err.message)}</p>`;}
 }
 return {render,deactivate};
})();
