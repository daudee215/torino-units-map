/* Static source catalogue adapter for GitHub Pages. Local service stays local. */
window.CityDataClient=(()=>{
 const BASE='data/city/';const cache=new Map();let summaryPromise;
 const local=['127.0.0.1','localhost'].includes(location.hostname)&&!new URLSearchParams(location.search).has('staticCity');
 function load(path){if(cache.has(path))return cache.get(path);const p=fetch(BASE+path+'?v=2.5.1').then(async r=>{if(r.status===404)return null;if(!r.ok)throw Error('City source file unavailable');if(path.endsWith('.gz')){if(typeof DecompressionStream==='undefined')throw Error('Please use a browser supporting gzip decompression');return new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).json();}return r.json();}).catch(err=>{cache.delete(path);throw err;});cache.set(path,p);if(cache.size>100)cache.delete(cache.keys().next().value);return p;}
 function summary(){return summaryPromise??=load('summary.json').then(s=>{if(!s)throw Error('City publication unavailable');return s;});}
 function tokens(text){return text.toLowerCase().normalize('NFD').replace(/\p{M}/gu,'').match(/[\p{L}\p{N}]+/gu)||[];}
 const hex=s=>Array.from(new TextEncoder().encode(s),b=>b.toString(16).padStart(2,'0')).join('');
 async function briefs(ids){const blocks=[...new Set(ids.map(n=>Math.floor((n-1)/1000)))];const chunks=await Promise.all(blocks.map(b=>load('briefs/'+b+'.json.gz')));const all=new Map(chunks.flat().filter(Boolean).map(r=>[r.n,r]));return ids.map(n=>all.get(n)).filter(Boolean);}
 async function get(path){
  if(local){const r=await fetch('http://127.0.0.1:8766/api/city'+path);if(!r.ok)throw Error('Local city catalogue unavailable');return r.json();}
  const s=await summary();if(!path)return s;const url=new URL('https://local.invalid/'+path.replace(/^\//,'')),q=url.searchParams;
  if(url.pathname==='/search'){
   const kind=q.get('kind')||'property',range=s.static.ranges[kind];if(!range)throw Error('Invalid source category');let candidates=null;
   for(const token of tokens((q.get('q')||'').slice(0,180))){const prefix=Array.from(token).slice(0,2).join('');const prefixes=Array.from(token).length<2?s.static.search_prefixes.filter(p=>p.startsWith(prefix)):[prefix];const shards=await Promise.all(prefixes.map(p=>load('search/'+hex(p)+'.json.gz')));const ids=new Set();for(const shard of shards)for(const [word,values] of Object.entries(shard||{}))if(word.startsWith(token))for(const n of values)if(n>=range[0]&&n<=range[1])ids.add(n);candidates=candidates===null?ids:new Set([...candidates].filter(n=>ids.has(n)));}
   const parcel=q.get('parcel');if(parcel){if(!/^\d+\/[0-9A-Za-z]+$/.test(parcel))throw Error('Invalid parcel');const members=await load('members/'+parcel.split('/')[0]+'.json.gz')||{};const ids=new Set(members[parcel]||[]);candidates=candidates===null?ids:new Set([...candidates].filter(n=>ids.has(n)));}
   const offset=Math.max(0,Math.min(1000000,Number(q.get('offset'))||0));let page,total;
   if(candidates===null){total=range[1]-range[0]+1;page=Array.from({length:Math.max(0,Math.min(50,total-offset))},(_,i)=>range[0]+offset+i);}else{const ids=[...candidates].sort((a,b)=>a-b);total=ids.length;page=ids.slice(offset,offset+50);}
   return {total,offset,limit:50,records:await briefs(page)};
  }
  if(url.pathname.startsWith('/record/')){
   const id=decodeURIComponent(url.pathname.slice('/record/'.length));const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(id));const bucket=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('').slice(0,3);const shard=await load('records/'+bucket+'.json.gz');if(!shard?.[id])throw Error('Unknown city record');return {record:shard[id]};
  }
  if(url.pathname==='/features'){
   const b=(q.get('bbox')||'').split(',').map(Number),[x0,y0,x1,y1]=b;const kind=q.get('kind')||'parcel';if(b.length!==4||!b.every(Number.isFinite)||!(7<x0&&x0<x1&&x1<8&&44<y0&&y0<y1&&y1<46))throw Error('Invalid map bounds');if((x1-x0)*(y1-y0)>.0002)return {type:'FeatureCollection',features:[],zoom_required:true,truncated:false};
   const step=s.static.tile_step,paths=[];for(let x=Math.floor(x0/step);x<=Math.floor(x1/step);x++)for(let y=Math.floor(y0/step);y<=Math.floor(y1/step);y++)paths.push('tiles/'+x+'_'+y+'.json.gz');const sets=await Promise.all(paths.map(load));const features=new Map();for(const f of sets.flat().filter(Boolean)){const b=f.properties.bbox;if(f.properties.kind===kind&&b[0]<=x1&&b[2]>=x0&&b[1]<=y1&&b[3]>=y0)features.set(f.id,f);}return {type:'FeatureCollection',features:[...features.values()].slice(0,1500),truncated:features.size>1500,zoom_required:false};
  }
  throw Error('Unknown city source request');
 }
 async function overview(bbox){
  const s=await summary(),o=s.static.overview;if(!o)throw Error('City parcel overview unavailable');
  const b=bbox.split(',').map(Number);if(b.length!==4||!b.every(Number.isFinite))throw Error('Invalid overview bounds');
  const keys=o.tiles.filter(key=>{const [x,y]=key.split('_').map(Number);return x*o.step<=b[2]&&(x+1)*o.step>=b[0]&&y*o.step<=b[3]&&(y+1)*o.step>=b[1];});
  const rows=await Promise.all(keys.map(key=>load('overview/'+key+'.json.gz'))),features=new Map();
  for(const f of rows.flat().filter(Boolean)){const a=f.properties.bbox;if(a[0]<=b[2]&&a[2]>=b[0]&&a[1]<=b[3]&&a[3]>=b[1])features.set(f.id,f);}
  return {type:'FeatureCollection',features:[...features.values()],simplification_m:o.simplification_m};
 }
 return {get,local,load,overview};
})();
window.PropertyDataClient=(()=>{
 async function get(path){
  if(CityDataClient.local){const r=await fetch('http://127.0.0.1:8766/api/property-workspace'+path);if(!r.ok)throw Error('Local property catalogue unavailable');return r.json();}
  const load=CityDataClient.load;if(!path)return load('workbench/summary.json.gz');const url=new URL('https://local.invalid/'+path.replace(/^\//,'')),args=url.searchParams;
  if(url.pathname==='/search'){
   const rows=await load('workbench/search.json.gz'),terms=(args.get('q')||'').toLowerCase().split(/\s+/).filter(Boolean),source=args.get('source')||'all',parcel=args.get('parcel');const weights={section_case:0,municipal_only:1,shared_key:2,ape:3};
   const found=rows.filter(r=>(!parcel||r.parcels.includes(parcel))&&(source==='all'||source==='municipal'&&r.kind==='municipal_reported_key'||source==='ape'&&r.kind==='ape_identity'||r.origin===source)&&terms.every(t=>r.search.includes(t))).sort((a,b)=>(weights[a.origin]-weights[b.origin])||a.parcel.localeCompare(b.parcel)||a.id.localeCompare(b.id));const offset=Math.max(0,Number(args.get('offset'))||0);return {total:found.length,offset,limit:50,records:found.slice(offset,offset+50)};
  }
  if(url.pathname.startsWith('/record/')){
   const id=decodeURIComponent(url.pathname.slice(8)),digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(id)),bucket=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('').slice(0,2);const rows=await load('workbench/records/'+bucket+'.json.gz'),record=rows?.[id];if(!record)throw Error('Unknown pilot record');let fp=args.get('parcel');if(!record.parcels.includes(fp))fp=record.parcel;const contexts=await load('workbench/parcels/'+fp.split('/')[0]+'.json.gz');return {record,context:contexts[fp],workflow:{status:'unreviewed',note:'',saved_at:null}};
  }
  throw Error('Read-only public source catalogue');
 }
 return {get};
})();
