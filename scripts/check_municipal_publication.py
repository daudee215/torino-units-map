"""Inspect every prepared municipal shard; produce a bounded source-only allowlist."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import gzip,json,hashlib,re
from check_city_publication import clean
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def check(folder=None):
 folder=folder or ROOT/'output/municipal-static';manifest=read(folder/'manifest.json');summary=read(folder/'summary.json')
 assert manifest['version']==summary['version']=='2.8.0-dev.1' and manifest['public_source_only'] and summary['public_source_only'] and not summary['local_only']
 allowed={r['path'] for r in manifest['files']};assert len(allowed)==len(manifest['files'])
 assert allowed|{'manifest.json'}=={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
 def inspect(r):
  name=r['path'];assert re.fullmatch(r'(?:summary\.json|(?:records/[0-9a-f]{3}|links/[0-9a-f]{3}|evidence/[0-9a-f]{3}|civics/[0-9a-f]{3}|briefs/\d+|search/[0-9a-f]+|tiles/(?:site|building|minor|volume|canopy|pedestrian|vehicle|road|archive|census|commercial)/\d+_\d+|broad/(?:site|building|minor|volume|canopy|pedestrian|vehicle|road|archive|census|commercial)|overview|qualities|investigation|unresolved|documents)\.json\.gz)',name),name
  p=folder/name;assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(folder.resolve());raw=p.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'],name
  obj=read(p);clean(obj)
  counts=Counter()
  if name.startswith('records/'):
   for rid,v in obj.items():
    assert rid==v['id'] and hashlib.sha256(rid.encode()).hexdigest().startswith(name.split('/')[1][:3]);assert not v['current_access_confirmed'];counts[v['kind']]+=1
    assert not set(v['attributes'])&{'EMAIL','TELEFONO','PROPRIETARIO','CONCESSIONARIO','CODICE_FISCALE'}
  if name.startswith('evidence/'):
   for v in obj.values():assert not v['current_access_confirmed']
  return counts
 counts=Counter()
 with ThreadPoolExecutor(max_workers=8) as pool:
  for result in pool.map(inspect,manifest['files']):counts.update(result)
 assert dict(counts)==summary['counts'] and sum(counts.values())==434085
 assert sum(r['bytes'] for r in manifest['files'])==manifest['bytes']<450*1024**2
 result=dict(version='2.8.0-dev.1',source_only=True,counts=dict(counts),files=len(allowed)+1,bytes=manifest['bytes'],raw_or_sqlite_files=0)
 (ROOT/'output/qa/municipal-publication-checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2),flush=True)
 return [folder/r['path'] for r in manifest['files']]+[folder/'manifest.json']
if __name__=='__main__':check()
