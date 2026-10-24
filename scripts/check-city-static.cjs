/* Exercise the real public adapter against exported files, without a local API. */
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path'),vm=require('node:vm'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'..');
(async()=>{
 let requests=0;
 const sandbox={window:{},location:{hostname:'example.github.io',search:''},URL,URLSearchParams,TextEncoder,Response,DecompressionStream,crypto:webcrypto,Map,Set,console};
 sandbox.fetch=async relative=>{assert(relative.startsWith('data/city/'));const target=path.resolve(root,relative.split('?')[0]);assert(target.startsWith(path.join(root,'data','city')+path.sep));requests++;try{return new Response(await fs.readFile(target));}catch(error){if(error.code==='ENOENT')return new Response('',{status:404});throw error;}};
 vm.createContext(sandbox);vm.runInContext(await fs.readFile(path.join(root,'city-data-client.js'),'utf8'),sandbox);sandbox.CityDataClient=sandbox.window.CityDataClient;
 const city=sandbox.window.CityDataClient,pilot=sandbox.window.PropertyDataClient;
 assert.equal(city.local,false);
 const workspace=await fs.readFile(path.join(root,'workspace.js'),'utf8');const init=workspace.slice(workspace.indexOf('const W ='),workspace.indexOf('try { W.lang'))+';W.tab';
 for(const hash of ['', '#lotto-1175-434'])assert.equal(vm.runInNewContext(init,{URLSearchParams,location:{search:'',hash},EnergyModel:{defaults:{}}}),'city');
 // Saved pilot links now land in the single municipal atlas, preserving source IDs.
 assert.equal(vm.runInNewContext(init,{URLSearchParams,location:{search:'?view=pilot',hash:'#lotto-1175-434'},EnergyModel:{defaults:{}}}),'city');
 const summary=await city.get('');assert.equal(summary.version,'2.5.1');assert.equal(summary.counts.property_source_identities,226951);
 const overview=await city.overview('7.57,45.00,7.78,45.15');assert.equal(overview.features.length,82434);assert.equal(overview.simplification_m,2);
 const north=await city.overview('7.57,45.10,7.78,45.15'),south=await city.overview('7.57,45.00,7.78,45.04');assert(north.features.length>1000&&south.features.length>1000);
 assert(north.features.some(f=>f.properties.bbox[3]>45.13));assert(south.features.some(f=>f.properties.bbox[1]<45.012));
 let data=await city.get('/search?kind=property');assert.equal(data.total,226951);assert.equal(data.records.length,50);
 data=await city.get('/search?kind=property&parcel=1282/94');assert.equal(data.total,14);
 data=await city.get('/search?kind=property&q=VIA%20ROMA');assert(data.total>500);assert(data.records.length<=50);
 data=await city.get('/search?kind=property&q=v');assert(data.total>500);
 data=await city.get('/record/'+encodeURIComponent('cadastre:L219_128200.94'));assert.equal(data.record.reference,'L219_128200.94');assert.equal(data.record.property_record_count,14);
 data=await city.get('/features?kind=parcel&bbox=7.68,45.06,7.69,45.07');assert(data.features.length>0&&data.features.length<=1500);
 data=await city.get('/features?kind=parcel&bbox=7.58,45.01,7.77,45.14');assert(data.zoom_required&&!data.features.length);
 data=await pilot.get('/search?source=municipal');assert.equal(data.total,178);const id=data.records[0].id;
 data=await pilot.get('/record/'+encodeURIComponent(id));assert.equal(data.record.id,id);assert.equal(data.workflow.note,'');assert.equal(data.workflow.status,'unreviewed');assert(!data.record.current_entrance_confirmed);
 await assert.rejects(pilot.get('/case'));
 console.log(`Static city adapter verified: city/pilot search, one-character prefixes, parcel records and bounded map tiles; ${requests} source-file reads, no local API.`);
})().catch(error=>{console.error(error);process.exitCode=1;});
