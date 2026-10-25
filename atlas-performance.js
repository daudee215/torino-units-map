/* Opt-in local diagnostics. No remote telemetry, record IDs or address logging. */
window.AtlasPerformance=(()=>{
 const enabled=new URLSearchParams(location.search).has('diagnostics');
 const events=[];let tasks=0,taskMs=0,skips=0,queued=false,longTaskSupported=false;
 function snapshot(){
  const nav=performance.getEntriesByType('navigation')[0];
  const resources=performance.getEntriesByType('resource');
  const same=resources.filter(r=>{try{return new URL(r.name).origin===location.origin;}catch{return false;}});
  return {schema:'torino-performance-v1',dataset_cache_mode:new URLSearchParams(location.search).has('diagnosticsCold')?'forced reload':'browser default',navigation_type:nav?.type||null,dom_ready_ms:Math.round(nav?.domContentLoadedEventEnd||0),load_ms:Math.round(nav?.loadEventEnd||0),elapsed_ms:Math.round(performance.now()),resource_entries:resources.length,same_origin_resources:same.length,same_origin_transfer_bytes:same.reduce((n,r)=>n+r.transferSize,0),transfer_note:'Resource Timing reported bytes; cache and cross-origin restrictions can report zero. Not total publication size.',long_task_supported:longTaskSupported,long_tasks:longTaskSupported?tasks:null,long_task_ms:longTaskSupported?Math.round(taskMs):null,heap_used_bytes:performance.memory?.usedJSHeapSize??null,heap_note:'Optional Chromium estimate; not memory retained only by this application',unchanged_layers_skipped:skips,events:[...events]};
 }
 function render(){if(!enabled||queued)return;queued=true;requestAnimationFrame(()=>{queued=false;let box=document.querySelector('#atlasPerformance');if(!box){box=document.createElement('details');box.id='atlasPerformance';box.style.cssText='position:fixed;z-index:3500;left:8px;bottom:8px;max-width:calc(100vw - 16px);max-height:45vh;overflow:auto;background:white;border:1px solid #88a9bf;padding:8px;font:10px monospace;color:#25465d';box.innerHTML='<summary>Performance diagnostics · local only</summary><button type="button">Refresh snapshot</button><pre style="white-space:pre-wrap;max-width:600px"></pre>';box.querySelector('button').onclick=render;document.body.append(box);}box.querySelector('pre').textContent=JSON.stringify(snapshot(),null,2);});}
 if(enabled){try{new PerformanceObserver(list=>{for(const e of list.getEntries()){tasks++;taskMs+=e.duration;}render();}).observe({type:'longtask',buffered:true});longTaskSupported=true;}catch{}window.addEventListener('load',render);}
 function start(operation){if(!enabled)return ()=>{};const t=performance.now();let ended=false;return ()=>{if(ended)return;ended=true;events.push({operation,duration_ms:Math.round((performance.now()-t)*10)/10});if(events.length>50)events.shift();render();};}
 return {start,skip(){if(enabled){skips++;render();}},refresh:render};
})();
