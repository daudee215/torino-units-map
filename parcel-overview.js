/* Display-only raster outlines. Detailed selectable source geometry stays separate. */
window.ParcelOverviewTiles=(()=>{
 const BASE='data/parcel-overview/';let promise;
 function config(){return promise??=fetch(BASE+'manifest.json?v=2.9.0').then(r=>{if(!r.ok)throw Error('Parcel overview tiles unavailable');return r.json();});}
 function leaflet(map,c){const layer=L.tileLayer(BASE+'{z}/{x}/{y}.png',{tileSize:256,minZoom:c.minzoom,maxNativeZoom:c.maxzoom,maxZoom:21,noWrap:true,bounds:[[c.bounds[1],c.bounds[0]],[c.bounds[3],c.bounds[2]]],attribution:c.attribution,opacity:.85});return layer;}
 function maplibreSource(c){return {type:'raster',tiles:[new URL(BASE+'{z}/{x}/{y}.png',location.href).href.replace(/%7B/g,'{').replace(/%7D/g,'}')],tileSize:256,minzoom:c.minzoom,maxzoom:c.maxzoom,bounds:c.bounds,attribution:'Catasto © Agenzia delle Entrate · CC BY 4.0'};}
 return {config,leaflet,maplibreSource};
})();
