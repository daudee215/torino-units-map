/* Browser-local references only; never store source geometry, notes or reviews. */
window.AtlasSelections=(()=>{
 const key='torino-atlas-saved-v1',limit=50;
 let memory=[],sessionOnly=false;
 const validId=id=>typeof id==='string'&&id.length<=250&&/^(?:municipal|cadastre|civic|property|bdtre):[A-Za-z0-9_:.\/-]+$/.test(id);
 function clean(rows){const seen=new Set();return (Array.isArray(rows)?rows:[]).filter(r=>r&&validId(r.id)&&typeof r.title==='string'&&!seen.has(r.id)&&seen.add(r.id)).slice(0,limit).map(r=>({id:r.id,title:r.title.replace(/[\u0000-\u001f\u007f]/g,'').slice(0,180),kind:typeof r.kind==='string'&&/^[a-z_]{1,30}$/.test(r.kind)?r.kind:''}));}
 function items(){if(!sessionOnly){try{memory=clean(JSON.parse(localStorage.getItem(key)||'[]'));}catch(_){sessionOnly=true;}}return memory.map(r=>({...r}));}
 function write(rows){memory=clean(rows);if(!sessionOnly){try{localStorage.setItem(key,JSON.stringify(memory));}catch(_){sessionOnly=true;}}return !sessionOnly;}
 function toggle(record){if(!record||!validId(record.id)||typeof record.title!=='string')return {invalid:true};const rows=items(),saved=rows.some(r=>r.id===record.id);if(!saved&&rows.length>=limit)return {full:true,saved:false};const persistent=write(saved?rows.filter(r=>r.id!==record.id):[record,...rows]);return {saved:!saved,persistent};}
 function remove(id){return {persistent:write(items().filter(r=>r.id!==id))};}
 function initialRecord(hash){if(!String(hash).startsWith('#record='))return null;try{const id=decodeURIComponent(hash.slice(8));return validId(id)?id:null;}catch(_){return null;}}
 function recordURL(id,base=location.href){if(!validId(id))throw Error('Invalid source identity');const url=new URL(base);if(!['http:','https:'].includes(url.protocol))throw Error('Invalid atlas URL');url.hash='record='+encodeURIComponent(id);return url.href;}
 return {items,toggle,remove,initialRecord,recordURL,isSaved:id=>items().some(r=>r.id===id),limit,key};
})();
