const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const box={window:{}};vm.createContext(box);vm.runInContext(fs.readFileSync(require('path').join(__dirname,'../atlas-render-cache.js'),'utf8'),box);
const c=box.window.AtlasRenderCache(),layer={},data={features:[1]},other={features:[1]};
assert(c.changed('parcel',layer,data,true));assert(!c.changed('parcel',layer,data,true));
assert(c.changed('parcel',layer,other,true));assert(c.changed('parcel',{},other,true));
assert(c.changed('parcel',layer,data,false));assert(!c.changed('parcel',layer,other,false));
assert(c.changed('parcel',layer,data,true));c.clear();assert(c.changed('parcel',layer,data,true));
console.log('Layer cache: unchanged data skipped, enablement/data/map-layer changes repainted.');
