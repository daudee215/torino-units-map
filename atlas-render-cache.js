/* Render identity cache: overlays stay independent from unchanged base layers. */
window.AtlasRenderCache=()=>{
 const states=new Map();
 return {changed(key,layer,data,enabled){
  const next={layer,data:enabled?data:null,enabled:Boolean(enabled)},old=states.get(key);
  if(old&&old.layer===next.layer&&old.data===next.data&&old.enabled===next.enabled)return false;
  states.set(key,next);return true;
 },clear(){states.clear();}};
};
