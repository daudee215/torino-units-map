/* Exercise the actual static municipal adapter, with no HTTP/API fallback. */
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path'),vm=require('node:vm'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'..');
let municipalFolder='data/municipal/';
(async()=>{
 let requests=0,bytes=0;const turfSandbox={};vm.createContext(turfSandbox);vm.runInContext(await fs.readFile(path.join(root,'vendor/turf.min.js'),'utf8'),turfSandbox);
 const box={window:{},location:{hostname:'example.github.io',search:''},URL,URLSearchParams,TextEncoder,Response,DecompressionStream,crypto:webcrypto,Map,Set,console,turf:turfSandbox.turf};
 box.fetch=async relative=>{assert(!relative.includes('8766')&&!relative.startsWith('http'),'Static adapter must never call a local API');const source=relative.startsWith('data/municipal/')?municipalFolder+relative.slice(15):relative;assert(source.startsWith(municipalFolder)||source.startsWith('data/city/'));const target=path.resolve(root,source.split('?')[0]);assert(target.startsWith(root+path.sep));requests++;try{const raw=await fs.readFile(target);bytes+=raw.length;return new Response(raw);}catch(e){if(e.code==='ENOENT')return new Response('',{status:404});throw e;}};
 vm.createContext(box);vm.runInContext(await fs.readFile(path.join(root,'city-data-client.js'),'utf8'),box);box.CityDataClient=box.window.CityDataClient;vm.runInContext(await fs.readFile(path.join(root,'municipal-data-client.js'),'utf8'),box);const m=box.window.MunicipalDataClient;assert(!m.local);
 const s=await m.get('');assert.equal(s.static.record_count,434085);
 for(const [kind,count] of Object.entries(s.counts)){const d=await m.get('/search?kind='+kind);assert.equal(d.total,count);assert.equal(d.records.length,50);}
 for(const [quality,count] of [['model',98078],['height_disagreement',1727],['non_ground',6724],['floor_unknown',7848]])assert.equal((await m.get('/search?kind=volume&quality='+quality)).total,count);
 let d=await m.get('/search?kind=volume&q=1');assert(d.total>50);assert(d.records.length===50);
 const rid='municipal:202609:volume:1';d=await m.get('/record/'+rid);assert.equal(d.record.site_candidates[0].id,'municipal:202609:site:7316');assert(d.record.site_candidates[0].geometry_intersects);
 d=await m.get('/connected/'+rid);assert.equal(d.parcels.length,3);assert.equal(d.selected_parcel,null);
 const parcel='cadastre:L219_128200.94';d=await m.get('/connected/'+parcel+'?section=properties');assert.equal(d.total,14);const p=d.records.find(r=>r.title==='1282/94/39');assert.equal(p.evidence.candidates[0].id,'civic:116066');assert(!p.current_access_confirmed);
 d=await m.get('/connected/cadastre:L219_138700.1?section=properties&offset=700');assert.equal(d.total,738);assert.equal(d.records.length,38);
 d=await m.get('/property-evidence/'+p.id);assert(!d.current_access_confirmed);
 d=await m.get('/connected/'+parcel+'?section=municipal&kind=volume');assert(d.total>0&&d.records.length<=50);
 d=await m.get('/connected/'+parcel+'?section=civics');assert(d.total>0&&d.records.length<=50);
 d=await m.get('/investigation');assert.equal(d.cases.length,50);assert.equal(d.unresolved.total,1262);
 d=await m.get('/unresolved?offset=1250');assert.equal(d.records.length,12);const finding=d.records[0];assert.equal((await m.get('/finding/'+finding.id)).source_site_reference,'0');
 for(const bbox of ['7.68,45.06,7.69,45.07','7.70,45.10,7.71,45.11','7.62,45.01,7.63,45.02']){d=await m.get('/features?kind=volume&bbox='+bbox);assert(d.features.length>0&&d.features.length<=2000);}
 d=await m.get('/features?kind=volume&bbox=7.58,45.01,7.77,45.14');assert(d.zoom_required&&!d.features.length);
 d=await m.get('/overview?bbox=7.57,45.00,7.78,45.15');assert.equal(d.cells.reduce((s,r)=>s+r.volumes,0),128273);
 d=await m.get('/context/'+rid+'?kind=archive');assert(d.total>0&&d.records.length<=50);
 d=await m.get('/links/'+rid+'?kind=parcel');assert.equal(d.total,3);
 await assert.rejects(m.get('/connected/'+parcel+'?parcel=wrong'));await assert.rejects(m.get('/features?kind=volume&bbox=bad'));await assert.rejects(m.get('/search?kind=building&quality=model'));
 const result={version:'2.8.0-dev.1',staticOnly:true,recordCount:434085,propertyFixture:14,unresolved:1262,cases:50,sourceRequests:requests,bytesRead:bytes};await fs.mkdir(path.join(root,'output/qa'),{recursive:true});await fs.writeFile(path.join(root,'output/qa/municipal-static-checks.json'),JSON.stringify(result,null,2));console.log(result);
})().catch(e=>{console.error(e);process.exitCode=1;});
