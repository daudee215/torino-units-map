"""Validate every static city shard and its bounded publication allowlist."""
from pathlib import Path
import gzip,hashlib,json,re
from concurrent.futures import ThreadPoolExecutor
FORBIDDEN={'review','review_events','note','review_note','owner','tenant','concessionario','codice_fiscale','raw_pdf','credentials','workflow','saved_at','file','local_path','raw_file'}
def clean(value):
 if isinstance(value,dict):
  assert not FORBIDDEN.intersection(value),FORBIDDEN.intersection(value)
  for child in value.values():clean(child)
 elif isinstance(value,list):
  for child in value:clean(child)
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def check(root):
 folder=root/'data/city';manifest=read(folder/'manifest.json');summary=read(folder/'summary.json')
 assert manifest['version']==summary['version']=='2.5.0'
 assert manifest['public_source_only'] and summary['public_source_only'] and summary['local_only'] is False
 assert summary['counts']['property_source_identities']==226951 and summary['counts']['parcel']==82434
 assert summary['static']['record_count']==491895 and len(summary['static']['search_prefixes'])>50
 allowed=set();paths=[]
 for r in manifest['files']:
  name=r['path'];assert re.fullmatch(r'(?:summary\.json|(?:records/[0-9a-f]{3}|briefs/\d+|search/[0-9a-f]+|members/\d+|tiles/\d+_\d+|workbench/records/[0-9a-f]{2}|workbench/parcels/\d+|workbench/search|workbench/summary)\.json\.gz)',name),name
  assert name not in allowed;allowed.add(name)
  p=folder/name;assert p.is_file() and not p.is_symlink();paths.append(p)
 assert allowed|{'manifest.json'}=={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
 metadata={r['path']:r for r in manifest['files']}
 def inspect(path):
  name=path.relative_to(folder).as_posix();raw=path.read_bytes();expected=metadata[name]
  assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256'],name
  obj=read(path);clean(obj)
  if name.startswith('records/'):
   for rid,r in obj.items():
    assert rid==r['id'] and hashlib.sha256(rid.encode()).hexdigest().startswith(path.name[:3])
    if r['kind']=='property':assert not r['current_entrance_confirmed']
   return len(obj),0
  if name.startswith('workbench/records/'):
   for r in obj.values():assert not r['current_entrance_confirmed']
   return 0,len(obj)
  return 0,0
 with ThreadPoolExecutor(max_workers=8) as pool:counts=list(pool.map(inspect,paths))
 assert sum(c[0] for c in counts)==491895 and sum(c[1] for c in counts)==24884
 assert sum(r['bytes'] for r in manifest['files'])==manifest['bytes']<650*1024**2
 print(f'Public city verified: {len(paths):,} hashed source-only shards; 491,895 city records and 24,884 pilot records; no local review fields.',flush=True)
 return paths+[folder/'manifest.json']
if __name__=='__main__':check(Path(__file__).resolve().parents[1])
