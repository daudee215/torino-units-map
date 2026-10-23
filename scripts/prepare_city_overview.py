"""Add generalized parcel outlines for whole-city viewing, retaining source IDs.

This is a display-only 2 m simplification. Exact geometry remains in the detailed
tiles and source records. It does not create or merge cadastral references.
"""
from collections import defaultdict
from pathlib import Path
import gzip,hashlib,json,math,sqlite3
from pyproj import Transformer
from shapely.geometry import shape,mapping
from shapely.ops import transform
ROOT=Path(__file__).resolve().parents[1]

def overview(write,summary):
 to_m=Transformer.from_crs(4326,32632,always_xy=True).transform
 to_ll=Transformer.from_crs(32632,4326,always_xy=True).transform
 def rounded(value):
  if isinstance(value,(list,tuple)):return [rounded(x) for x in value]
  return round(value,6)
 tiles=defaultdict(list);step=.025;unique=set()
 with sqlite3.connect((ROOT/'output/city/catalog.sqlite').as_uri()+'?mode=ro',uri=True) as db:
  for rid,fp,title,raw in db.execute("SELECT id,fp,title,geo FROM entities WHERE kind='parcel' ORDER BY n"):
   source=shape(json.loads(raw));g=transform(to_ll,transform(to_m,source).simplify(2,preserve_topology=True));geo=mapping(g);geo['coordinates']=rounded(geo['coordinates']);bbox=list(source.bounds)
   feature=dict(type='Feature',id=rid,geometry=geo,properties=dict(id=rid,kind='parcel',fp=fp,title=title,bbox=bbox))
   unique.add(rid)
   for x in range(math.floor(bbox[0]/step),math.floor(bbox[2]/step)+1):
    for y in range(math.floor(bbox[1]/step),math.floor(bbox[3]/step)+1):tiles[f'{x}_{y}'].append(feature)
 assert len(unique)==summary['counts']['parcel']
 for key,features in tiles.items():write('overview/'+key+'.json.gz',features)
 summary['static']['overview']=dict(step=step,tiles=sorted(tiles),parcel_references=len(unique),simplification_m=2,source_geometry_unchanged=True)
 print(f'Generalized whole-city overview: {len(unique):,} original references in {len(tiles)} tiles.',flush=True)

def prepare():
 folder=ROOT/'data/city';manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'));summary=json.loads((folder/'summary.json').read_text(encoding='utf-8'))
 files={r['path']:r for r in manifest['files']}
 def write(name,value):
  raw=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode();data=gzip.compress(raw,compresslevel=9,mtime=0) if name.endswith('.gz') else raw
  p=folder/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(data);files[name]=dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 overview(write,summary);summary['version']='2.5.1';manifest['version']='2.5.1';write('summary.json',summary)
 manifest['files']=list(files.values());manifest['bytes']=sum(r['bytes'] for r in files.values());(folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('Overview gzip bytes:',sum(r['bytes'] for n,r in files.items() if n.startswith('overview/')))
if __name__=='__main__':prepare()
