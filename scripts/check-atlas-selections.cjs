/* Validate real reference storage and URL rules, including failure boundaries. */
const fs=require('node:fs/promises'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
(async()=>{
 const source=await fs.readFile(path.join(__dirname,'../atlas-selections.js'),'utf8');
 let stored='[]',fail=false;
 const sandbox={window:{},URL,location:{href:'https://example.github.io/torino-units-map/?release=2.10.0'},localStorage:{getItem:()=>stored,setItem:(k,v)=>{if(fail)throw Error('Storage unavailable');stored=v;}}};
 vm.createContext(sandbox);vm.runInContext(source,sandbox);const a=sandbox.window.AtlasSelections;
 assert.equal(a.initialRecord('#record=municipal-key%3A2e13c5315ddb640270b2ff2e'),'municipal-key:2e13c5315ddb640270b2ff2e');
 const record={id:'cadastre:L219_128200.94',title:'1282/94',kind:'parcel',geometry:{type:'Polygon'},review:'must not persist'};
 assert(a.toggle(record).persistent);assert(a.isSaved(record.id));assert.deepEqual(Object.keys(JSON.parse(stored)[0]).sort(),['id','kind','title']);
 const url=a.recordURL(record.id);assert.equal(new URL(url).pathname,'/torino-units-map/');assert.equal(a.initialRecord(new URL(url).hash),record.id);
 for(const bad of ['#lotto-1175-434','#record=%E0%A4%A','#record=javascript:bad','#record=civic%3A1%0A','#record=civic%3A%3Cimg%3E'])assert.equal(a.initialRecord(bad),null);
 assert.throws(()=>a.recordURL('javascript:alert'));assert.throws(()=>a.recordURL(record.id,'file:///tmp/atlas'));
 assert(!a.toggle(record).saved);assert.equal(a.items().length,0);
 for(let i=0;i<50;i++)assert(a.toggle({id:'civic:'+i,title:'Civic '+i,kind:'entrance'}).saved);
 assert(a.toggle({id:'civic:999',title:'Extra'}).full);assert.equal(a.items().length,50);a.remove('civic:0');assert(!a.isSaved('civic:0'));
 fail=true;const changed=a.toggle({id:'civic:900',title:'Session only'});assert(changed.saved&&!changed.persistent);assert(a.isSaved('civic:900'));
 console.log('Saved references verified: exact source IDs, URL round trip, legacy/invalid hashes, reference-only fields, 50-record cap and storage failure.');
})().catch(e=>{console.error(e);process.exitCode=1;});
