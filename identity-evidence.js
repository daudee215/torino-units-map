/* Evidence indexes only. No inference of apartment interiors or legal identity. */
(function(root){
  "use strict";
  function status(link,onDate){
    const r=link.review||{};
    if(r.decision==="rejected")return "rejected";
    if(r.valid_from&&r.valid_from>onDate||r.valid_to&&r.valid_to<=onDate)return "outside_validity";
    return r.decision==="accepted"?"accepted":"candidate";
  }
  function index(data,onDate){
    const byProperty=new Map(data.properties.map(p=>[p.id,[]]));
    const byEntrance=new Map(data.entrances.map(e=>[String(e.COD_CIVICO),[]]));
    for(const link of data.links){
      if(link.kind!=="property_entrance"||!byProperty.has(link.source))continue;
      const id=link.target.replace(/^entrance:/,"");
      const entry={link,entranceId:id,status:status(link,onDate)};
      byProperty.get(link.source).push(entry);
      if(byEntrance.has(id))byEntrance.get(id).push(entry);
    }
    const active=entries=>entries.filter(e=>e.status==="candidate"||e.status==="accepted");
    return {byProperty,byEntrance,active};
  }
  const normalized=x=>String(x??"").normalize("NFKD").replace(/[\u0300-\u036f]/g,"").toLowerCase().trim();
  function filter(data,idx,{query="",kind="all",entrance=null}={}){
    const q=normalized(query);
    return data.properties.filter(p=>{
      const links=idx.active(idx.byProperty.get(p.id)||[]);
      if(entrance&&!links.some(e=>e.entranceId===String(entrance)))return false;
      const hay=normalized([p.address,p.civic,p.floor,...(p.reported_interiors||[]),...p.members.map(m=>m.join("/"))].join(" "));
      if(q){
        const parts=q.split('/');
        const exactKey=parts.length>=3;
        const matches=exactKey?p.members.some(m=>normalized(parts.length===3?m.slice(2).join('/'):parts.length===4?[m[0],...m.slice(2)].join('/'):m.join('/'))===q):hay.includes(q);
        if(!matches)return false;
      }
      if(kind==="missing_identity")return !p.identity_complete;
      if(kind==="unlinked")return links.length===0;
      if(kind==="multiple_entrances")return new Set(links.map(e=>e.entranceId)).size>1;
      if(kind==="reviewed")return links.some(e=>e.status==="accepted");
      if(kind==="grouped")return p.members.length>1||p.scope!=="cadastral_property";
      if(kind==="section_conflict")return p.flags.includes("cadastral_section_alias_requires_review");
      if(kind==="has_interior")return (p.reported_interiors||[]).length>0;
      if(kind==="interior_conflict")return p.flags.includes("conflicting_reported_interiors");
      return true;
    });
  }
  const api={index,filter,status};if(typeof module!=="undefined"&&module.exports)module.exports=api;else root.IdentityEvidence=api;
})(typeof window==="undefined"?globalThis:window);
