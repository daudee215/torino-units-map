/* Exercise actual civic/parcel source shards and the selection policy. */
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path'),vm=require('node:vm'),{webcrypto}=require('node:crypto'),zlib=require('node:zlib');
(async()=>{
 const root=path.resolve(__dirname,'..'),box={window:{},document:{documentElement:{lang:'en'}},URL,TextEncoder,Response,DecompressionStream,crypto:webcrypto};
 box.fetch=async relative=>{assert(relative.startsWith('data/access-resolution/')&&!relative.includes('..'));return new Response(await fs.readFile(path.join(root,relative.split('?')[0])));};
 vm.createContext(box);vm.runInContext(await fs.readFile(path.join(root,'access-resolution.js'),'utf8'),box);const m=box.window.AccessResolution;
 const outside=await m.resolveCivic('civic:50320');assert.equal(outside.automatic,'cadastre:L219_117600.311');assert.equal(outside.tier,'property_address');assert(!outside.municipal_point_parcels.some(p=>p.id===outside.automatic));
 const geom=await m.resolveCivic('civic:50282');assert.equal(geom.automatic,'cadastre:L219_117400.359');assert.equal(geom.tier,'bdtre_point');assert(!geom.municipal_point_parcels.some(p=>p.id===geom.automatic));
 const multiple=await m.resolveCivic('civic:72519');assert.equal(multiple.candidates.length,2);assert.equal(multiple.automatic,null);
 const unknown=await m.resolveCivic('civic:75715');assert.equal(unknown.automatic,null);assert(m.navigationBanner(unknown).includes('nearest parcel is not selected'));
 const fixture={id:'civic:test',title:'<img src=x>',coordinates:[7.6,45.0],related_parcels:[{id:'cadastre:A',fp:'1/2',property_source_count:5,access_point_count:1},{id:'cadastre:B',fp:'1/3',property_source_count:1,access_point_count:0},{id:'cadastre:road',fp:'1/STRADA1',property_source_count:0,access_point_count:3}],municipal_point_parcels:[]};
 assert.equal(m.navigation(fixture).automatic,null,'Neither strongest count nor one intersecting point resolves multiple reported property candidates');
 const banner=m.navigationBanner(m.navigation(fixture));assert(!banner.includes('STRADA1'));assert(banner.includes('&lt;img src=x&gt;')&&!banner.includes('<img src=x>'));
 const html={isConnected:true,innerHTML:'',textContent:''};await m.civic(html,'civic:116066');assert(html.innerHTML.includes('Vehicle access')&&html.innerHTML.includes('Internal-access record'));assert(html.innerHTML.includes('not confirmation')&&html.innerHTML.includes('may share production'));
 const parcel=await m.parcel('cadastre:L219_120400.98');await m.documents(html,parcel);assert(html.innerHTML.includes('1204/98/37'));assert(!html.innerHTML.includes('reported subalterni 68'),'Garage does not inherit attic-stair roles');
 const index=JSON.parse(zlib.gunzipSync(await fs.readFile(path.join(root,'data/access-resolution/unmapped-index.json.gz'))));assert.equal(index.length,6819);
 assert.equal(m.filter(index,{signal:'reference_hypothesis'}).length,44);assert.equal(m.filter(index,{reason:'complex_reference'}).length,44);
 const later=index[6500];assert.equal(m.filter(index,{query:later.id})[0].id,later.id);
 assert(await m.unlocated(html,'property:5a8ac9ca3b38ede41e1c89dc'));assert(html.innerHTML.includes('L219 / 1245 / 243 / 26 /'));assert(html.innerHTML.includes('1245/26'));assert(html.innerHTML.includes('do not replace the source reference'));
 box.document.documentElement.lang='it';await m.civic(html,'civic:116066');assert(html.innerHTML.includes('Accesso carrabile')&&html.innerHTML.includes('non conferma'));await m.unlocated(html,'property:5a8ac9ca3b38ede41e1c89dc');assert(html.innerHTML.includes('Nessuna chiave o appartenenza modificata'));
 console.log('Access resolution verified: outside-point parcel navigation, source/geometry precedence, explicit ambiguity, no nearest or road assignment, source role/date limits, scoped stair evidence, all-record filtering and preserved original keys; IT/EN and HTML safety.');
})().catch(e=>{console.error(e);process.exitCode=1;});
